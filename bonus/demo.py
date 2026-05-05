from agent import HybridMemoryAgent

def main():
    print("--- Khởi tạo Hybrid Memory Agent cho User: u_001 ---")
    # Lần chạy đầu tiên sẽ tải model embedding mất ~30s
    agent = HybridMemoryAgent(user_id="u_001")
    
    print("\n--- Đang giả lập việc User đọc tài liệu và lưu vào Episodic Memory ---")
    memories = [
        "Tôi vừa đọc một bài viết rất hay về Kubernetes và container orchestration.",
        "Tôi đang cấu hình AWS Auto Scaling, tự động mở rộng hạ tầng theo lưu lượng người dùng rất tiện.",
        "Dạo này tôi phải đọc nhiều về Cloud Security và IAM policies để chuẩn bị cho dự án mới."
    ]
    for mem in memories:
        agent.remember(mem)
        print(f" [+] Remembered: {mem}")
        
    print("\n" + "="*50)
    print("DEMO: 5 QUERIES MINH HOẠ")
    print("="*50)
    
    queries = [
        # 1. Hỏi đơn giản (chỉ vector hit)
        ("Tôi đã đọc gì về Kubernetes?", "Hỏi đơn giản (Vector hit)"),
        
        # 2. Hỏi cần profile context
        ("Recommend đọc gì tiếp?", "Hỏi cần Profile Context (topic_affinity)"),
        
        # 3. Hỏi cần fresh activity
        ("Tôi đang quan tâm gì gần đây?", "Hỏi cần Fresh Activity (queries_last_hour)"),
        
        # 4. Hỏi paraphrase (vector wins)
        ("Tài liệu về tự động mở rộng hạ tầng?", "Hỏi paraphrase (Vector wins)"),
        
        # 5. Hỏi mixed (hybrid + profile)
        ("Cho tôi summary cloud security", "Hỏi mixed (Hybrid + Profile)")
    ]
    
    for i, (q, desc) in enumerate(queries, 1):
        print(f"\nQUERY {i}: {q}")
        print(f"Loại: {desc}")
        context = agent.recall(q)
        print(context)

if __name__ == "__main__":
    main()
