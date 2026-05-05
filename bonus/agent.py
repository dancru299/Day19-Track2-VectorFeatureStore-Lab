import sys
from pathlib import Path
import time
import json

# Add project root to sys.path so we can import from app
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from feast import FeatureStore

class HybridMemoryAgent:
    def __init__(self, user_id: str = "u_001"):
        self.user_id = user_id
        
        # Init Vector Store (Episodic Memory)
        self.embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.qdrant = QdrantClient(":memory:")
        self.collection_name = "user_memory"
        self.qdrant.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        self._point_id = 0
        
        # Init Feature Store (Stable Profile & Activity)
        feast_repo_path = PROJECT_ROOT / "app" / "feast_repo"
        self.fs = FeatureStore(repo_path=str(feast_repo_path))
        
        self.request_features = [
            "user_profile_features:reading_speed_wpm",
            "user_profile_features:preferred_language",
            "user_profile_features:topic_affinity",
            "query_velocity_features:queries_last_hour",
        ]

    def remember(self, text: str) -> None:
        """Add a new piece of episodic memory for this user."""
        # Simple chunking logic (per message)
        vector = list(self.embedder.embed([text]))[0]
        
        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=self._point_id,
                    vector=vector.tolist(),
                    payload={
                        "user_id": self.user_id,
                        "text": text,
                        "timestamp": int(time.time())
                    }
                )
            ]
        )
        self._point_id += 1

    def recall(self, query: str) -> str:
        """Retrieve top-K memories + user profile features -> return assembled context."""
        
        # 1. Get user profile + recent activity from Feast
        try:
            profile_response = self.fs.get_online_features(
                features=self.request_features,
                entity_rows=[{"user_id": self.user_id}],
            ).to_dict()
            
            # Feast returns dict of lists, we take the first element
            speed = profile_response.get("reading_speed_wpm", [0])[0]
            lang = profile_response.get("preferred_language", ["unknown"])[0]
            topic = profile_response.get("topic_affinity", ["none"])[0]
            recent_queries = profile_response.get("queries_last_hour", [0])[0]
            
            profile_str = f"Liking topic: {topic}, Reading speed: {speed} wpm, Lang: {lang}."
            activity_str = f"Queries last hour: {recent_queries}"
        except Exception as e:
            profile_str = "Profile not available."
            activity_str = "Activity not available."

        # 2. Hybrid search Qdrant filtered by user_id
        # (For this POC we use pure semantic search for episodic memories)
        query_vector = list(self.embedder.embed([query]))[0]
        hits = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=query_vector.tolist(),
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=self.user_id)
                    )
                ]
            ),
            limit=3
        ).points
        
        memory_str = "\n".join([f" - {h.payload['text']} (score: {h.score:.2f})" for h in hits])
        if not memory_str:
            memory_str = " No recent episodic memories found."

        # 3. Assemble context string
        context = (
            f"--- SYSTEM CONTEXT FOR USER {self.user_id} ---\n"
            f"[User Profile] {profile_str}\n"
            f"[Recent Activity] {activity_str}\n"
            f"[Episodic Memories Retrieved]\n{memory_str}\n"
            f"----------------------------------------"
        )
        return context
