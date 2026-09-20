# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thanh Bình
**Nhóm:** kingpro
**Ngày:** 2026-09-20

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai đoạn văn có độ tương tự cosine cao khi vector của chúng hướng gần giống nhau, tức là nội dung có ý nghĩa gần nhau dù có thể dùng từ khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Người mua có thể yêu cầu trả hàng khi sản phẩm bị lỗi.
- Câu B: Khách hàng được hoàn trả sản phẩm nếu hàng nhận được bị hư hỏng.
- Tại sao tương đồng: Hai câu cùng diễn đạt điều kiện trả hàng do lỗi hoặc hư hỏng của sản phẩm.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Tiền hoàn được chuyển về ví điện tử sau khi yêu cầu được chấp nhận.
- Câu B: Người bán cần đóng gói sản phẩm đúng quy cách vận chuyển.
- Tại sao khác: Một câu nói về thời gian và phương thức hoàn tiền, câu còn lại nói về đóng gói vận chuyển.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào hướng của vector nên so sánh được ý nghĩa mà ít bị ảnh hưởng bởi độ lớn của vector. Khoảng cách Euclid nhạy với độ lớn, vì vậy hai văn bản cùng chủ đề vẫn có thể bị đánh giá xa nhau nếu vector có chuẩn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `ceil((10.000 - 50) / (500 - 50)) = ceil(9.950 / 450) = ceil(22,11)`.
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số lượng tăng thành `ceil((10.000 - 100) / (500 - 100)) = ceil(24,75) = 25 chunks`. Overlap lớn hơn giúp giữ thông tin nằm sát ranh giới chunk, nhưng làm tăng số chunk và chi phí lưu trữ/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])(?:[ \t]+|\n+)` để tách sau dấu kết thúc câu mà vẫn giữ dấu câu. Các câu được strip rồi gom theo `max_sentences_per_chunk`; chuỗi rỗng trả về `[]`. Cách này chưa phân biệt hoàn hảo chữ viết tắt như `TS.` hoặc số thập phân.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán thử separator theo thứ tự đoạn văn, dòng, câu, từ rồi ký tự. Mảnh còn quá dài được đệ quy với separator tiếp theo; các mảnh nhỏ liên tiếp được gom tới gần `chunk_size`. Base case là text đã đủ ngắn, danh sách separator rỗng, hoặc separator cuối `""`, khi đó text được cắt cứng theo kích thước.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuyển thành record in-memory gồm id, content, bản sao metadata và embedding. `search` chỉ embed query một lần, tính dot product với từng embedding, sắp xếp điểm giảm dần và trả tối đa `top_k` kết quả mà không làm lộ vector trong output.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Metadata được lọc trước khi tính similarity để các kết quả sai audience không chiếm chỗ trong top-k. `delete_document` loại mọi record có `metadata["doc_id"]` khớp tài liệu gốc, nên xóa được đồng thời tất cả chunk của tài liệu đó.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent lấy top-k chunk, đánh số từng đoạn và kèm nguồn trước khi đưa vào prompt. Prompt yêu cầu chỉ trả lời theo ngữ cảnh chính sách trả hàng–hoàn tiền, trích dẫn `[1]`, `[2]` và nói rõ khi dữ liệu không đủ; store rỗng được xử lý mà không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
python -m pytest tests -q -p no:cacheprovider
..........................................                               [100%]
42 passed in 0.03s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Bộ câu hỏi Benchmark và Gold Answer — Cá nhân (5 điểm)

Bộ benchmark có đúng 5 câu và bao phủ các dạng tra số liệu, điều kiện, quy trình, liệt kê và lọc metadata. Gold answer chỉ tổng hợp thông tin xuất hiện trực tiếp trong corpus; cột cuối chỉ rõ file và mục dùng để kiểm chứng.

| # | Dạng hỏi | Query | Gold answer | Nguồn kiểm chứng / Filter |
|---|----------|-------|-------------|--------------------------|
| 1 | Tra số liệu | Sau khi Shopee chấp nhận hoàn tiền, tiền hoàn cho đơn thanh toán bằng thẻ tín dụng hoặc ghi nợ mất bao lâu? | Tiền được hoàn về thẻ tín dụng/ghi nợ trong **7–14 ngày làm việc**, tùy theo ngân hàng. | `buyer-refund-timeline.md` — Bảng 1; không filter |
| 2 | Hỏi điều kiện | Nếu sản phẩm khác rõ ràng về chất liệu, màu sắc, thông số hoặc kiểu dáng so với mô tả thì có thể chọn lý do trả hàng nào? | Có thể chọn lý do **“Khác với mô tả”**; lý do này áp dụng cho tất cả sản phẩm. | `buyer-return-eligibility.md` — mục 1.3; `audience: buyer` |
| 3 | Hỏi quy trình | Nếu yêu cầu được chấp nhận theo phương án Trả hàng và Hoàn tiền, người mua cần làm gì và trong bao lâu? | Người mua cần chọn hình thức trả hàng và hoàn tất gửi hàng về kho Shopee hoặc Người bán trong vòng **6 ngày** kể từ khi nhận thông báo gửi trả hàng. | `buyer-return-process.md` — mục 3; `audience: buyer` |
| 4 | Liệt kê | Hãy liệt kê các hình thức gửi hàng hoàn trả mà Shopee hướng dẫn cho người mua. | Ba hình thức gồm: **Đơn vị vận chuyển đến lấy hàng, Trả hàng tại bưu cục và Tự sắp xếp**. | `buyer-return-shipping.md` — mục 1.1 và 2.2; `audience: buyer` |
| 5 | Lọc metadata | Khi khiếu nại hàng hoàn có vấn đề, cần chuẩn bị những thông tin và bằng chứng nào? | Cần chuẩn bị lý do khiếu nại, thông tin đơn hàng, mã vận đơn/thông tin vận chuyển, hình ảnh kiện hàng, video mở kiện, hình ảnh sản phẩm ban đầu nếu có và bằng chứng thể hiện hàng hoàn bị sai, thiếu, vỡ hoặc không nguyên vẹn. | `seller-refund-appeal.md` — mục 5; `audience: seller` |

**Lý do câu 5 cần metadata filter:**
> Câu hỏi không nêu rõ vai trò người hỏi, trong khi corpus có cả tài liệu cho người mua và người bán cùng dùng các từ “khiếu nại”, “hàng hoàn” và “bằng chứng”. Lọc `audience: seller` trước retrieval giúp kết quả tập trung vào nghĩa vụ chuẩn bị bằng chứng của Người bán.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

Benchmark dùng 8 tài liệu trong `data/refund/`, chia theo heading thành 65 chunks với `chunk_size=1800`. Vì `MockEmbedder` dựa trên MD5 không phản ánh ngữ nghĩa, lần chạy này dùng lexical embedding chuẩn hóa tiếng Việt bằng thư viện chuẩn; toàn bộ kết quả thô được lưu trong `ket_qua_benchmark.txt`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Thời gian hoàn về thẻ tín dụng/ghi nợ | `buyer-refund-timeline` — phần giới thiệu phương thức hoàn tiền | 0.5803 | Không ở top-1; chunk chứa mốc 7–14 ngày ở top-2 | Trích được dòng bảng: thẻ tín dụng/ghi nợ hoàn trong 7–14 ngày làm việc `[2]`. |
| 2 | Điều kiện chọn lý do “Khác với mô tả” | `buyer-return-eligibility` — bảng lý do trả hàng | 0.3896 | Có | Trích đúng lý do “Khác với mô tả”, mô tả trường hợp và phạm vi tất cả sản phẩm `[1]`. |
| 3 | Quy trình sau khi được chấp nhận trả hàng | `buyer-return-process` — phân loại phương án xử lý | 0.5468 | Có | Trích đúng yêu cầu chọn hình thức trả hàng và gửi trả trong vòng 6 ngày `[1]`. |
| 4 | Liệt kê hình thức gửi hàng hoàn trả | `buyer-return-shipping` — tiêu đề tài liệu | 0.5010 | Không ở top-1; chunk chứa danh sách ở top-3 | Trích được ba hình thức: đơn vị vận chuyển đến lấy, trả tại bưu cục và tự sắp xếp `[3]`. |
| 5 | Bằng chứng khiếu nại hàng hoàn | `seller-refund-appeal` — thông tin Người bán nên chuẩn bị | 0.5863 | Có | Liệt kê đúng lý do, thông tin đơn, mã vận đơn, hình ảnh, video và bằng chứng tình trạng hàng hoàn `[1]`. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5 / 5**

**Đánh giá:**
> Cả 5 câu đều có đúng chunk chứa gold evidence trong top-3 và câu trả lời trích xuất chứa thông tin bắt buộc. Câu 1 và câu 4 cho thấy chỉ nhìn top-1 có thể đánh giá sai chất lượng retrieval: top-1 đúng tài liệu nhưng chưa chứa đủ chi tiết, còn bằng chứng cần thiết nằm ở top-2 hoặc top-3.

**Ảnh hưởng của metadata filter:**
> Câu 5 dùng `metadata_filter={"audience": "seller"}` trước khi xếp hạng. Top-3 khi đó chỉ tập trung vào tài liệu khiếu nại/bằng chứng của Người bán, tránh lẫn hướng dẫn bổ sung bằng chứng dành cho Người mua.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chưa có dữ liệu kết quả từ thành viên hoặc nhóm khác để so sánh trực tiếp. Từ lần chạy cá nhân, bài học rõ nhất là phải chấm theo **chunk chứa bằng chứng** thay vì chỉ theo `doc_id`, vì đúng tài liệu chưa bảo đảm đoạn top-1 đủ thông tin để trả lời.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Bộ câu hỏi benchmark và Gold Answer | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
