# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** kingpro
**Thành viên:** Lục Tiến Đạt - 2A202602969, Dương Thị Ngân - 2A202602808, Nguyễn Thanh Bình - 2A202602777, Nguyễn Văn Duy - 2A202602729
**Ngày:** 20/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách Trả hàng / Hoàn tiền của Shopee

**Tại sao nhóm chọn chủ đề này?**

> Thương mại điện tử có các quy định trả hàng, hoàn tiền rất phức tạp, chia làm hai đối tượng rõ rệt là Người mua (Buyer) và Người bán (Seller). Việc chọn chủ đề này giúp kiểm thử hiệu quả tính năng lọc theo đối tượng (`audience`), giúp RAG agent trả lời chính xác quy định mà không bị nhầm lẫn giữa hai vai trò.

### Danh sách tài liệu (Data Inventory)

| #   | Tên tài liệu                  | Nguồn (Source URL)                                | Ngày lấy / Phiên bản    | Số ký tự | Metadata đã gán                                         |
| --- | ----------------------------- | ------------------------------------------------- | ----------------------- | -------- | ------------------------------------------------------- |
| 1   | `buyer-refund-timeline.md`    | https://help.shopee.vn/portal/4/article/189473... | 2026-08-03 / not-stated | 5,176    | audience: buyer, category: refund-timeline, lang: vi    |
| 2   | `buyer-return-eligibility.md` | https://help.shopee.vn/portal/4/article/188931... | 2026-08-03 / not-stated | 8,709    | audience: buyer, category: return-eligibility, lang: vi |
| 3   | `buyer-return-process.md`     | https://help.shopee.vn/portal/4/article/190242... | 2026-08-03 / not-stated | 11,735   | audience: buyer, category: return-process, lang: vi     |
| 4   | `buyer-return-shipping.md`    | https://help.shopee.vn/portal/4/article/189477... | 2026-08-03 / not-stated | 7,714    | audience: buyer, category: return-shipping, lang: vi    |
| 5   | `return-refund-policy.md`     | https://help.shopee.vn/portal/4/article/77251...  | 2026-08-03 / 2026-03-11 | 25,322   | audience: both, category: general-policy, lang: vi      |
| 6   | `seller-refund-appeal.md`     | https://banhang.shopee.vn/edu/article/3647        | 2026-08-03 / 2025-11-03 | 6,326    | audience: seller, category: seller-appeal, lang: vi     |
| 7   | `seller-return-evidence.md`   | https://banhang.shopee.vn/edu/article/25057       | 2026-08-03 / 2025-06-02 | 11,083   | audience: seller, category: return-evidence, lang: vi   |
| 8   | `seller-return-process.md`    | https://banhang.shopee.vn/edu/article/563         | 2026-08-03 / not-stated | 10,088   | audience: seller, category: seller-response, lang: vi   |
| 9   | `seller-warranty-policy.md`   | https://example.com/policy/seller-warranty        | 2026-09-18 / not-stated | 967      | audience: seller, category: warranty-policy, lang: vi   |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu  | Ví dụ giá trị                       | Tại sao hữu ích cho truy xuất (retrieval)?                                                |
| --------------- | ----- | ----------------------------------- | ----------------------------------------------------------------------------------------- |
| `audience`      | `str` | `buyer`, `seller`, `both`           | Phân vùng tài liệu cho Người mua hoặc Người bán, tránh nhầm lẫn điều khoản khi truy xuất. |
| `category`      | `str` | `return-process`, `refund-timeline` | Lọc chính xác chủ đề con của quy trình trước khi tìm kiếm vector.                         |
| `language`      | `str` | `vi`                                | Đảm bảo tính nhất quán ngôn ngữ khi truy xuất.                                            |
| `source_url`    | `str` | `https://help.shopee.vn/...`        | Cung cấp link gốc để trích dẫn nguồn (source traceability).                               |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

So sánh các chiến lược phân đoạn trên tài liệu chính sách cốt lõi `return-refund-policy.md`:

| Tài liệu | Chiến lược (Strategy) | Thành viên phụ trách | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `return-refund-policy.md` | `FixedSizeChunker` (size=500, ov=50) | Dương Thị Ngân | 43 | 489.6 | Kém (dễ cắt đứt câu/từ tại mốc 500 ký tự) |
| `return-refund-policy.md` | `SentenceChunker` (max=3) | Nguyễn Thanh Bình | 44 | 428.4 | Khá (giữ câu hoàn chỉnh nhưng tách rời tiêu đề mục) |
| `return-refund-policy.md` | `RecursiveChunker` (size=500) | Lục Tiến Đạt | 64 | 294.3 | Rất tốt (ưu tiên giữ trọn vẹn cấu trúc đề mục và điều khoản) |
| `return-refund-policy.md` | `MarkdownHeadingChunker` (size=650) | Nguyễn Văn Duy | 65 | 289.6 | Rất tốt (bám sát cấu trúc heading Markdown của chính sách) |

### Chiến lược của từng thành viên

**Thành viên 1 — Lục Tiến Đạt (2A202602969)**

- **Loại chiến lược:** `RecursiveChunker` (chunk_size=500, separators=["\n\n", "\n", ". ", " ", ""])
- **Mô tả & lý do chọn cho chủ đề này:** Chiến lược chia nhỏ đệ quy ưu tiên bảo tồn cấu trúc tiêu đề Markdown và các gạch đầu dòng của chính sách. Giúp các chunk luôn mang đầy đủ tiêu đề và nội dung chi tiết.

**Thành viên 2 — Dương Thị Ngân (2A202602808)**

- **Loại chiến lược:** `FixedSizeChunker` (chunk_size=500, overlap=50)
- **Mô tả & lý do chọn cho chủ đề này:** Sử dụng phương pháp chia khối kích thước cố định 500 ký tự với 50 ký tự gối đầu (overlap). Phương pháp này đơn giản, tốc độ thực thi nhanh nhưng có nhược điểm là có thể cắt ngang một câu điều khoản quan trọng tại ranh giới chunk.

**Thành viên 3 — Nguyễn Thanh Bình (2A202602777)**

- **Loại chiến lược:** `SentenceChunker` (max_sentences_per_chunk=3)
- **Mô tả & lý do chọn cho chủ đề này:** Tách văn bản theo từng câu đơn dựa trên ranh giới câu (`. `, `! `, `? `) và gom mỗi 3 câu thành một khối. Chiến lược này đảm bảo tính trọn vẹn ngữ pháp của câu, nhưng đôi khi làm đứt gãy mối liên kết giữa tiêu đề mục chính sách và các điều khoản con.

**Thành viên 4 — Nguyễn Văn Duy (2A202602729)**

- **Loại chiến lược:** `MarkdownHeadingChunker` (`chunk_size=650`) — cắt theo tiêu đề `##`/`###`, section dài mới cắt bằng `RecursiveChunker` và gắn lại heading.
- **Mô tả & lý do chọn cho chủ đề này:** Chính sách Shopee được tổ chức theo các mục rõ ràng. Giữ và lặp lại heading trên từng mảnh con giúp chunk vẫn mang tên điều khoản khi được truy xuất riêng, hạn chế mất ngữ cảnh ở section dài.

### So Sánh Giữa Các Thành Viên

| Thành viên        | Chiến lược (Strategy)                | Điểm truy xuất (/10) | Điểm mạnh                                           | Điểm yếu                                      |
| ----------------- | ------------------------------------ | -------------------- | --------------------------------------------------- | --------------------------------------------- |
| Lục Tiến Đạt      | `RecursiveChunker` (size=500)        | 10/10                | Giữ trọn cấu trúc ngữ nghĩa tiêu đề mục và nội dung | Số lượng chunk tạo ra nhiều hơn               |
| Dương Thị Ngân    | `FixedSizeChunker` (size=500, ov=50) | 7/10                 | Thực thi nhanh, kích thước chunk đều đặn            | Dễ cắt đứt giữa chừng câu hoặc từ ngữ         |
| Nguyễn Thanh Bình | `SentenceChunker` (max=3)            | 8/10                 | Câu văn hoàn chỉnh về ngữ pháp, không bị đứt câu    | Tách rời tiêu đề khỏi phần nội dung bên dưới  |
| Nguyễn Văn Duy    | `MarkdownHeadingChunker` (size=650)  | 9/10                 | Giữ tên mục và ngữ cảnh điều khoản                  | Heading lặp có thể tăng nhiễu hoặc đứng riêng |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> **`RecursiveChunker` (chunk_size=500)** là chiến lược tối ưu nhất cho văn bản chính sách thương mại điện tử (đạt **10/10** điểm truy xuất). Vì các bài viết quy định Shopee có cấu trúc tiêu đề (`#`, `##`) và danh sách gạch đầu dòng phân tầng rõ ràng; `RecursiveChunker` ưu tiên ngắt theo đoạn lớn (`\n\n`, `\n`) trước khi chia nhỏ, giúp bảo toàn trọn vẹn tiêu đề điều khoản gắn liền với nội dung quy định chi tiết bên dưới.
> 
> Xếp ngay sau là **`MarkdownHeadingChunker` (9/10)** của bạn Duy: chiến lược này rất tốt trong việc bám theo tiêu đề Markdown, nhưng việc lặp lại heading có thể gây nhiễu nếu đoạn văn quá ngắn hoặc đứng độc lập. Trong khi đó, **`SentenceChunker` (8/10)** làm đứt gãy liên kết giữa tiêu đề mục cha với các điều khoản con, và **`FixedSizeChunker` (7/10)** cho hiệu quả thấp nhất do thường xuyên cắt đứt ngang xương các câu văn và thuật ngữ tại ranh giới 500 ký tự.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| #   | Câu hỏi (Query)                                                                                                                     | Câu trả lời chuẩn (Gold Answer)                                                                                                                                                                        | Chunk nào chứa thông tin?               |
| --- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------- |
| 1   | Người mua thanh toán đơn hàng bằng Thẻ tín dụng/ghi nợ thì nhận được tiền hoàn trong bao lâu?                                       | Thời gian nhận được tiền hoàn là từ **7–14 ngày làm việc** (tùy theo từng ngân hàng) sau khi Shopee chấp nhận hoàn tiền, và tiền sẽ hoàn về đúng tài khoản Thẻ tín dụng/ghi nợ đã dùng khi thanh toán. | `buyer-refund-timeline.md` (Bảng 1)     |
| 2   | Đối với sản phẩm thực phẩm tươi sống và đông lạnh, thời gian tối đa để người mua gửi yêu cầu Trả hàng/Hoàn tiền là bao lâu?         | Trong vòng **24 giờ** kể từ lúc đơn hàng được cập trạng thái “Giao hàng thành công” (trừ lý do Chưa nhận được hàng).                                                                                   | `buyer-return-eligibility.md` (Mục 1.2) |
| 3   | Người bán có thời hạn bao nhiêu ngày để gửi khiếu nại nếu không đồng ý với quyết định Hoàn tiền ngay của Shopee?                    | Người bán phải gửi khiếu nại trong vòng **2 ngày** kể từ khi Shopee gửi thông báo quyết định Hoàn tiền ngay cho Người mua mà không yêu cầu trả hàng. Shopee sẽ xem xét trong 3–5 ngày làm việc.        | `seller-refund-appeal.md` (Mục 1)       |
| 4   | Khi người bán khiếu nại quyết định hoàn tiền ngay không yêu cầu trả hàng của Shopee, loại bằng chứng nào là bắt buộc phải cung cấp? | Bắt buộc cung cấp **Bằng chứng đóng gói** (video ghi lại toàn bộ quá trình đóng gói sản phẩm trước khi bàn giao cho Đơn vị vận chuyển). Không yêu cầu bằng chứng mở hàng hoàn.                         | `seller-return-evidence.md` (Bảng B)    |
| 5   | Trong các phương thức gửi hàng hoàn trả của Shopee, hình thức nào yêu cầu người mua phải thanh toán trước phí trả hàng?             | Hình thức **"Tự sắp xếp"**: Người mua cần thanh toán trước phí trả hàng tại bưu cục, sau đó Shopee sẽ hỗ trợ hoàn lại phí trả hàng này.                                                                | `buyer-return-shipping.md` (Mục 1.1)    |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| #   | Câu hỏi                               | Chiến lược tốt nhất cho câu này                | Có chunk liên quan trong top-3? | Ghi chú                                                    |
| --- | ------------------------------------- | ---------------------------------------------- | ------------------------------- | ---------------------------------------------------------- |
| 1   | Thời gian hoàn tiền Thẻ tín dụng      | `RecursiveChunker`                             | Có                              | Truy xuất chính xác Bảng 1 mốc thời gian (2đ)              |
| 2   | Hạn trả hàng thực phẩm tươi sống      | `RecursiveChunker`                             | Có                              | Đoạn 24 giờ nằm trọn trong chunk mục 1.2 (2đ)              |
| 3   | Hạn khiếu nại của Người bán           | `RecursiveChunker` + Filter `audience: seller` | Có                              | Nhờ có metadata filter loại bỏ nhầm lẫn với buyer (2đ)     |
| 4   | Bằng chứng khiếu nại của Người bán    | `RecursiveChunker` + Filter `audience: seller` | Có                              | Bảng bằng chứng đóng gói trích xuất đầy đủ (2đ)            |
| 5   | Phương thức trả hàng thanh toán trước | `RecursiveChunker` + Filter `audience: buyer`  | Có                              | Lấy đúng điều khoản hoàn phí của hình thức Tự sắp xếp (2đ) |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> Rất hữu ích, đặc biệt ở câu 3, câu 4 và câu 5. Nhóm đã thực hiện A/B Test bắt buộc trên Câu hỏi 3:
>
> - **Khi KHÔNG dùng filter**: Cả 3 slot trong Top-3 đều bị chiếm bởi tài liệu chung `return-refund-policy.md` (chính sách chung của cả 2 bên) và hoàn toàn không chứa mốc thời hạn 2 ngày khiếu nại của Người bán.
> - **Khi CÓ dùng `metadata_filter={"audience": "seller"}`**: Top-1 truy xuất chính xác tài liệu `seller-refund-appeal.md` chứa mốc thời gian quy định ("Người bán phải gửi khiếu nại trong vòng 2 ngày kể từ khi Shopee gửi thông báo...").

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

### Phân tích lỗi (Failure Analysis)

- **Câu hỏi gặp lỗi (Failure Case)**: Câu hỏi 1 — _"Người mua thanh toán đơn hàng bằng Thẻ tín dụng/ghi nợ thì nhận được tiền hoàn trong bao lâu?"_ khi chạy với mô hình embedding thô / `MockEmbedder`.
- **Nguyên nhân (Tại sao hỏng)**:
  1. `MockEmbedder` băm MD5 chuỗi ký tự nên không mã hoá ngữ nghĩa, dẫn đến chunk có điểm số cao nhất lại thuộc tài liệu `return-refund-policy.md` (nói chung chung về phạm vi áp dụng) thay vì trúng ngay Bảng 1 của `buyer-refund-timeline.md`.
  2. Đoạn văn chứa bảng thời gian hoàn tiền bị phân mảnh nếu kích thước chunk quá nhỏ, làm cho từ khóa "Thẻ tín dụng/ghi nợ" nằm ở dòng trên nhưng mốc số "7–14 ngày" lại bị đẩy sang chunk khác nếu không có overlap hợp lý.
- **Đề xuất cải tiến**:
  1. Sử dụng mô hình Embedding thực tế (như `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` hoặc Gemini Embeddings) để đo chính xác khoảng cách ngữ nghĩa thay vì dựa vào tần suất ký tự ngẫu nhiên.
  2. Bổ sung `overlap` hợp lý cho các bảng biểu hoặc giữ nguyên cấu trúc Markdown table trong 1 chunk duy nhất.

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

> 1. Tầm quan trọng của việc bảo tồn cấu trúc ngữ nghĩa văn bản: `RecursiveChunker` và `MarkdownHeadingChunker` vượt trội hơn hẳn `FixedSizeChunker` khi xử lý văn bản quy định/điều khoản nhiều cấp mục.
> 2. Vai trò sống còn của Siêu dữ liệu (Metadata Pre-filtering) trong hệ thống RAG đa đối tượng (người mua vs người bán), được chứng minh qua thực nghiệm A/B Test.
> 3. Cơ chế trích dẫn nguồn (Source Traceability `[1]`, `[2]`) giúp người dùng kiểm chứng và ngăn chặn hoàn toàn hiện tượng ảo giác (hallucination).

**Bài học rút ra khi so sánh trong nhóm:**

> Cùng một bộ tài liệu, nhưng chiến lược cắt thô theo kích thước cố định (`FixedSizeChunker` của bạn Ngân) dẫn tới tình trạng cụt ý và rớt điểm truy xuất ở các câu hỏi chi tiết. Chiến lược câu (`SentenceChunker` của bạn Bình) giữ trọn câu nhưng làm mất liên kết với tiêu đề mục cha. Trong khi đó, việc bám sát cấu trúc ngữ nghĩa và tiêu đề (`RecursiveChunker` của bạn Đạt và `MarkdownHeadingChunker` của bạn Duy) giúp vector embedding thu nạp trọn vẹn ngữ cảnh nhất, đem lại điểm truy xuất cao nhất cho nhóm (9–10/10).

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> Nhóm sẽ gắn thêm metadata về `sub_topic` hoặc `product_type` (ví dụ: hàng tươi sống, hàng điện tử) để bộ lọc có thể truy xuất sâu hơn vào từng nhóm ngành hàng đặc thù.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí                                 | Điểm tự đánh giá |
| ---------------------------------------- | ---------------- |
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10          |
| Thiết kế chiến lược (Strategy Design)    | 15 / 15          |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10          |
| Thuyết trình (Demo)                      | 5 / 5            |
| **Tổng phần nhóm**                       | **40 / 40**      |
