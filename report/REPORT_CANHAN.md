# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đinh Thị Minh Tâm
**Nhóm:** G47
**Ngày:** 19/09/2026

> Báo cáo này dùng cùng corpus, năm câu benchmark và Gold Answer với `REPORT_NHOM.md`. Kết quả được chạy bằng chiến lược cá nhân `HeadingChunker` kết hợp `RecursiveChunker`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao nghĩa là gì?**

Hai embedding có cosine similarity cao khi chúng hướng gần giống nhau trong không gian vector. Về mặt khái niệm, mô hình xem hai đoạn văn có nội dung hoặc ý nghĩa gần nhau, dù chúng có thể không dùng đúng cùng từ ngữ.

**Ví dụ có độ tương tự CAO:**

- Câu A: “Vector store lưu embeddings để tìm kiếm ngữ nghĩa.”
- Câu B: “Kho vector lưu các embedding phục vụ truy xuất tương tự.”
- Tại sao tương đồng: Hai câu cùng mô tả chức năng lưu vector và tìm nội dung gần nhau về ngữ nghĩa.

**Ví dụ có độ tương tự THẤP:**

- Câu A: “Hệ thống RAG cần trích dẫn nguồn.”
- Câu B: “Cây xoài cần ánh sáng và nước để phát triển.”
- Tại sao khác: Hai câu thuộc hai chủ đề không liên quan: hệ thống AI và chăm sóc cây trồng.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

Cosine tập trung vào hướng của vector, tức mẫu đặc trưng ngữ nghĩa, thay vì độ lớn tuyệt đối. Vì vậy nó ít nhạy hơn với khác biệt về độ dài hoặc scale của vector; đặc biệt với embedding đã chuẩn hóa, cosine là thước đo trực quan và thuận tiện để xếp hạng.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10.000 ký tự, `chunk_size=500`, `overlap=50`. Bao nhiêu chunks?**

```text
step = 500 - 50 = 450
count = ceil((10.000 - 50) / 450)
      = ceil(9.950 / 450)
      = ceil(22,111...)
      = 23 chunks
Đáp án 23 chunks
```

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

```text
step = 500 - 100 = 400
count = ceil((10.000 - 100) / 400)
      = ceil(24,75)
      = 25 chunks
Đáp án 25 chunks
```

Số chunk tăng từ 23 lên 25 vì mỗi chunk mới chỉ tiến thêm 400 thay vì 450 ký tự. Overlap lớn hơn giúp giữ ngữ cảnh ở ranh giới chunk, nhưng đổi lại làm tăng dữ liệu trùng lặp, dung lượng lưu trữ và chi phí embedding/truy xuất.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk` — hướng tiếp cận:**

Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng đứng sau `.`, `!` hoặc `?`, nhờ vậy vẫn giữ dấu kết thúc trong câu. Sau đó tôi loại phần rỗng, chuẩn hóa khoảng trắng và nhóm tối đa `max_sentences_per_chunk`; đầu vào rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split` — hướng tiếp cận:**

Thuật toán thử separator theo thứ tự ưu tiên `\n\n`, `\n`, `. `, dấu cách rồi ký tự. Nếu đoạn đã không vượt `chunk_size`, đó là base case; nếu hết separator, hàm cắt cố định theo ký tự để luôn tiến triển. Separator được gắn lại để không làm mất nội dung, các phần nhỏ được gộp đến giới hạn, còn phần quá lớn tiếp tục được tách đệ quy.

### Lớp `EmbeddingStore`

**`add_documents` + `search` — hướng tiếp cận:**

Mỗi `Document` được chuẩn hóa thành record gồm `id`, `content`, bản sao `metadata`, `embedding` và thứ tự thêm. Store dùng in-memory list để kết quả nhất quán; truy vấn được embed một lần, tính dot product với từng record, sắp xếp score giảm dần và chỉ trả `top_k` mà không làm lộ vector embedding trong output.

**`search_with_filter` + `delete_document` — hướng tiếp cận:**

Tôi lọc metadata trước khi similarity search để các slot top-k không bị tài liệu sai phạm vi chiếm mất. `_make_record` bảo đảm luôn có `metadata['doc_id']` (id chunk dạng `file#0` được quy về `file`); `delete_document` loại toàn bộ record có `doc_id` tương ứng và trả về việc có record nào thực sự bị xóa hay không.

### Tác tử `KnowledgeBaseAgent`

**`answer` — hướng tiếp cận:**

Agent lấy top-k chunk, đánh số `[1]`, `[2]`, `[3]`, đính kèm nguồn và ghép chúng vào phần ngữ cảnh của prompt. Prompt yêu cầu chỉ dùng bằng chứng đã truy xuất, trích dẫn số nguồn và nói rõ khi thông tin không đủ; nếu store rỗng, agent trả thông báo ngay mà không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

Lệnh đã chạy:

```bash
pytest tests/ -v
```

Kết quả:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/dyerg/K4-L3A-Data-Foundations
collecting ... collected 46 items

tests/test_heading_chunker.py ....                                      [  8%]
tests/test_solution.py ..........................................        [100%]

============================== 46 passed in 0.05s ==============================
```

Ngoài test suite, tôi đã chạy `python3 main.py "Chunking là gì?"`; chương trình nạp 5 tài liệu, lưu chúng vào `EmbeddingStore`, trả top-3 và gọi `KnowledgeBaseAgent` thành công.

**Số lượng bài test vượt qua:** **46 / 46** (42 test bắt buộc và 4 test bổ sung cho `HeadingChunker`).

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Tôi dự đoán trước khi chạy, sau đó đo bằng model thật `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Model chuẩn hóa vector nên dot product trong store tương đương cosine similarity; trong năm cặp này, tôi xem khoảng 0,5 trở lên là tương đồng tương đối cao và dưới 0,3 là thấp.

| Cặp | Câu A | Câu B | Dự đoán trước khi chạy | Điểm thực tế | Đúng? |
|------|-------|-------|------------------------|--------------|-------|
| 1 | Vector store lưu embeddings để tìm kiếm ngữ nghĩa. | Kho vector lưu các embedding phục vụ truy xuất tương tự. | Cao | 0,677601 | Có |
| 2 | Chunk quá nhỏ có thể làm mất ngữ cảnh. | Đoạn văn quá ngắn thường thiếu thông tin xung quanh. | Cao | 0,686612 | Có |
| 3 | Python thường được dùng để xây dựng API. | FastAPI và Flask hỗ trợ phát triển dịch vụ HTTP bằng Python. | Cao | 0,563714 | Có |
| 4 | Metadata giúp thu hẹp không gian tìm kiếm. | Bộ lọc theo phòng ban có thể giảm kết quả nhiễu. | Cao | 0,284707 | Chưa đúng như dự đoán |
| 5 | Hệ thống RAG cần trích dẫn nguồn. | Cây xoài cần ánh sáng và nước để phát triển. | Thấp | 0,148690 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Cặp 4 bất ngờ nhất: hai câu đều nói về tác dụng thu hẹp kết quả bằng metadata nhưng score chỉ 0,284707, thấp hơn ba cặp tương đồng còn lại. Điều này cho thấy embedding nắm bắt ngữ nghĩa tốt hơn mock nhưng vẫn nhạy với cách diễn đạt và mức độ cụ thể; “metadata” và “phòng ban” không hoàn toàn đồng nghĩa, nên cosine score cần được đánh giá cùng benchmark retrieval thay vì dùng một ngưỡng cứng cho mọi chủ đề.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

### Thiết lập thí nghiệm

- Corpus: 6 file Markdown đã làm sạch trong `data/hoc-bong/`; frontmatter được tách khỏi content trước khi chunk.
- Chiến lược cá nhân: `HeadingChunker(chunk_size=500)`; section dài được chẻ bằng `RecursiveChunker` và heading được lặp lại trên mọi mảnh con.
- Tổng số: 22 chunk; mỗi chunk có ID `file#i` và thừa kế toàn bộ metadata của file nguồn.
- Backend: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, chạy local.
- Retrieval: `search_with_filter(..., top_k=3)`; riêng câu 2 dùng `metadata_filter={"audience": "student"}`.
- Bằng chứng đầy đủ được lưu trong `ket_qua_benchmark.txt`.

| # | Câu hỏi (Query) | Top-1 chunk truy xuất được (tóm tắt) | Score | Có liên quan? | Câu trả lời của Agent (tóm tắt) |
|---|-----------------|--------------------------------------|-------|----------------|---------------------------------|
| 1 | Có bao nhiêu sinh viên nhận học bổng bán phần trong chương trình học bổng tuyển sinh Khóa 46 năm 2020? | `...khoa-46-dhcq#5`: mục **Số người nhận** | 0,8137 | Có — Top-1 | Có 356 sinh viên nhận học bổng bán phần. |
| 2 | Để được xét và nhận học bổng khuyến khích học tập cần thực hiện như thế nào? | `...he-thong-tin-chi#5`: điều kiện tối thiểu 15 tín chỉ | 0,6779 | Có nhưng thiếu — Top-1 | Context trả lời được điều kiện 15 tín chỉ nhưng thiếu ba điều kiện nằm ở chunk `#4`; câu trả lời chưa đủ Gold Answer. |
| 3 | Quy trình xét và chi trả học bổng khuyến khích học tập gồm những bước nào? | `quy-trinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap#1`: bước 1–2 | 0,6990 | Có — Top-1 và Top-3 | Ghép `#1` và `#2` cho đủ ba bước: hội đồng xét; phòng đào tạo công bố/khiếu nại; phòng tài chính công bố thời gian, địa điểm nhận. |
| 4 | Hãy liệt kê ba mức học bổng tuyển sinh Khóa 46 năm 2020 và giá trị tương ứng. | `...hkc-nam-2020#0`: thông báo kết quả học bổng khác | 0,7666 | Không | Tài liệu K46 có trong Top-3 nhưng chỉ là chunk tiêu đề `#0`; chunk `#1` chứa các mức 1,5/1/0,5 không được truy xuất nên không đủ bằng chứng trả lời. |
| 5 | Việc chi trả học bổng KKHT học kỳ cuối năm 2020 cho Khóa 43–45 dự kiến được thông báo khi nào? | `...hkc-nam-2020#0`: thông báo kết quả và chi trả | 0,8740 | Có — Top-1 | Phòng Tài chính – Kế toán dự kiến thông báo việc chi trả trong tháng 12/2020. |

**Bao nhiêu câu hỏi trả về ít nhất một chunk liên quan trong top-3?** **4 / 5**. Theo rubric nội dung: câu 1, 3, 5 đạt 2 điểm; câu 2 đạt 1 điểm vì thiếu chi tiết; câu 4 đạt 0 điểm, tổng **7/10**.

### Phân tích kết quả và failure case

Failure rõ nhất là câu 4: Top-3 có chunk `#0` của đúng tài liệu K46 nhưng không có chunk `#1` chứa ba mức học bổng. Nếu chỉ chấm theo `doc_id`, trường hợp này dễ bị đánh dấu đúng sai lệch; kiểm tra nội dung cho thấy agent không thể tạo Gold Answer từ context được cung cấp. Cách cải thiện là đưa tiêu đề tài liệu vào mỗi section khi embedding, thêm `category=admission-scholarship` cho truy vấn này hoặc thử tăng trọng số từ khóa “giá trị/mức”.

Ở câu 2, filter `audience=student` loại chunk quy trình `staff` khỏi Top-3, nhưng danh sách bốn điều kiện bị chia thành `#4` và `#5`; chỉ `#5` được lấy. Kết quả cho thấy metadata filter giải quyết phạm vi đối tượng, còn chunk size và ranh giới bullet vẫn quyết định câu trả lời có đầy đủ hay không.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

Điều đáng giá nhất tôi rút ra từ phần đối chiếu chiến lược là không nên đánh giá retrieval chỉ bằng việc tài liệu đúng xuất hiện trong Top-3; phải kiểm tra chính chunk đó có chứa dữ kiện để trả lời hay không. So sánh với fixed-size, sentence và recursive baseline cũng cho thấy chunking theo heading giữ ngữ cảnh tốt hơn cho văn bản quy định, nhưng cần overlap theo bullet hoặc gộp các mảnh cùng section để tránh mất một phần danh sách như ở câu 2.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **57 / 60** |
