# Reflection — Lab 19

**Tên:** Nguyễn Anh Đức
**Cohort:** _<A20-K1>_
**Path đã chạy:** _<lite>_

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

**Trả lời:**
Phân tích kết quả từ notebook `02_hybrid_search_rrf.ipynb`:

1.  **Hybrid thắng ở loại query nào?**
    *   **Mixed (Hỗn hợp):** Hybrid Mode thắng áp đảo (Precision@10 = **0.360**), vượt xa Semantic (0.230) và Keyword (0.210).
    *   **Paraphrase (Diễn giải):** Hybrid Mode thắng rõ rệt (0.350 vs Semantic 0.290 và Keyword 0.170).
    *   **Exact (Chính xác):** Cả ba mode gần như ngang nhau, nhưng Hybrid vẫn nhỉnh hơn một chút (0.430 vs Semantic 0.420 và Keyword 0.410).

2.  **Tại sao?**
    *   **BM25** xử lý tốt khi từ khóa xuất hiện đúng trong văn bản, nhưng thất bại khi câu hỏi dùng từ đồng nghĩa hoặc cấu trúc khác.
    *   **Vector Search** bắt được ngữ nghĩa, nhưng lại bị nhiễu bởi các văn bản có chủ đề liên quan nhưng không chứa đúng từ khóa chính.
    *   **Hybrid (RRF):** Sự kết hợp giúp khắc phục điểm yếu của nhau. Khi câu hỏi dài và phức tạp (Mixed/Paraphrase), BM25 tìm được các đoạn văn chứa từ khóa quan trọng (anchor terms) và Vector Search tìm được các văn bản có ngữ nghĩa tương tự. Thuật toán RRF (Reciprocal Rank Fusion) sau đó hợp nhất kết quả từ hai bộ lọc này, loại bỏ nhiễu và tập trung vào những tài liệu xuất hiện ở thứ hạng cao trong **cả hai** bộ lọc, dẫn đến độ chính xác cao nhất.

3.  **Khi nào không dùng Hybrid?**
    *   **Khi truy vấn cực ngắn và đơn giản (Exact Match):** Trong trường hợp câu hỏi chỉ chứa 1-3 từ và các tài liệu chứa từ đó rất nhiều, BM25 truyền thống hoạt động hiệu quả và nhanh chóng. Việc thêm Vector Search có thể làm tăng độ trễ mà không cải thiện đáng kể độ chính xác (như thấy trong bảng thống kê).
    *   **Khi cần kết quả tức thì và đơn giản:** Đối với các hệ thống yêu cầu phản hồi dưới 10ms cho các truy vấn đơn giản, việc bỏ qua bước tính toán vector có thể là cần thiết.

---

## Điều ngạc nhiên nhất khi làm lab này

_(Optional, 1–2 câu)_

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
