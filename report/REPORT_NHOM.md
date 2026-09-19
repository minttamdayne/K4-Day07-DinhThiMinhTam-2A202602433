# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** G47
**Thành viên:** Đinh Thị Minh Tâm
**Ngày:** 19/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy định và thông báo học bổng dành cho sinh viên đại học chính quy tại UEH.

**Tại sao nhóm chọn chủ đề này?**
> Học bổng là chủ đề có nhiều điều kiện, mốc thời gian và mức hỗ trợ cụ thể nên phù hợp để đánh giá khả năng truy xuất chính xác. Bộ tài liệu dùng nguồn công khai chính thức của UEH và tách riêng nội dung dành cho sinh viên với quy trình dành cho cán bộ, nhờ đó có thể đo tác dụng của bộ lọc `audience`.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định xét cấp học bổng khuyến khích học tập | [UEH](https://daotao.ueh.edu.vn/quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien-dai-hoc-chinh-quy-trong-dao-tao-theo-he-thong-tin-chi/) | 2026-09-19 / `1358/QĐ-ĐHKT-QLĐT&CTSV` | 2.015 | `audience=student`; `category=scholarship-eligibility` |
| 2 | Quy trình xét và chi trả học bổng khuyến khích học tập | [UEH](https://daotao.ueh.edu.vn/quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien-dai-hoc-chinh-quy-trong-dao-tao-theo-he-thong-tin-chi/) | 2026-09-19 / `1358/QĐ-ĐHKT-QLĐT&CTSV` | 838 | `audience=staff`; `category=scholarship-process` |
| 3 | Kết quả học bổng khuyến khích học tập HKC 2020 cho Khóa 43–45 | [UEH](https://daotao.ueh.edu.vn/quyet-dinh-cap-hoc-bong-khuyen-khich-hoc-tap-va-danh-sach-sinh-vien-khoa-43-44-45-dhcq-dat-hoc-bong-khuyen-khich-hoc-tap-hkc-nam-2020/) | 2026-09-19 / `not-stated` | 603 | `audience=student`; `category=scholarship-result` |
| 4 | Học bổng hỗ trợ học tập học kỳ cuối năm 2021 | [UEH](https://daotao.ueh.edu.vn/thong-bao-cap-hoc-bong-ho-tro-hoc-tap-hoc-ky-cuoi-nam-2021-cho-sinh-vien-dai-hoc-chinh-quy/) | 2026-09-19 / `not-stated` | 459 | `audience=student`; `category=support-scholarship` |
| 5 | Cấp học bổng tuyển sinh Khóa 47 | [UEH](https://daotao.ueh.edu.vn/thong-bao-ve-viec-cap-hoc-bong-tuyen-sinh-khoa-47-cho-sinh-vien-dai-hoc-chinh-quy/) | 2026-09-19 / `not-stated` | 410 | `audience=student`; `category=admission-scholarship` |
| 6 | Học bổng tuyển sinh đại học chính quy năm 2020 cho Khóa 46 | [UEH](https://daotao.ueh.edu.vn/thong-bao-ve-viec-hoc-bong-tuyen-sinh-dai-hoc-chinh-quy-nam-2020-khoa-46-dhcq/) | 2026-09-19 / `not-stated` | 1.434 | `audience=student`; `category=admission-scholarship` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc `not-stated`) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `quy-trinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap` | Khóa duy nhất để đối chiếu file, nguồn và chunk. |
| `title` | string | `Quy trình của các đơn vị xét và chi trả học bổng...` | Tăng tín hiệu ngữ nghĩa khi truy xuất. |
| `source_url` | URL | `https://daotao.ueh.edu.vn/...` | Truy nguyên và kiểm chứng câu trả lời. |
| `retrieved_at` | date (`YYYY-MM-DD`) | `2026-09-19` | Cho biết thời điểm chụp dữ liệu. |
| `document_version` | string | `1358/QĐ-ĐHKT-QLĐT&CTSV` hoặc `not-stated` | Phân biệt phiên bản; không suy đoán số hiệu khi nguồn không nêu. |
| `audience` | enum | `student`, `staff` | Lọc tách điều kiện sinh viên khỏi quy trình nội bộ của đơn vị thực hiện. |
| `department` | string | `student-affairs` | Giới hạn truy xuất theo đơn vị phụ trách. |
| `category` | enum/string | `scholarship-eligibility` | Phân biệt điều kiện, quy trình, kết quả và loại học bổng. |
| `language` | ISO-like string | `vi` | Chọn pipeline embedding/trả lời phù hợp ngôn ngữ. |
| `license_or_permission` | string | `public-source` | Ghi căn cứ được phép đưa nguồn vào corpus. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(body, chunk_size=200)` trên ba tài liệu sau khi loại bỏ khối YAML frontmatter. Độ dài được tính theo ký tự, đúng với cách `chunk_size` được cài đặt trong các chunker hiện tại.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Quy định xét học bổng KKHT (2.015 ký tự) | FixedSizeChunker (`fixed_size`) | 11 | 183,2 | Không ổn định — có thể cắt giữa câu hoặc điều kiện. |
| Quy định xét học bổng KKHT (2.015 ký tự) | SentenceChunker (`by_sentences`) | 7 | 286,1 | Có — giữ trọn câu, nhưng nhiều chunk vượt ngưỡng 200 ký tự. |
| Quy định xét học bổng KKHT (2.015 ký tự) | RecursiveChunker (`recursive`) | 15 | 132,8 | Một phần — ưu tiên ranh giới đoạn nhưng không lặp lại heading. |
| Quy trình xét và chi trả (838 ký tự) | FixedSizeChunker (`fixed_size`) | 5 | 167,6 | Không ổn định — bước thực hiện có thể bị cắt giữa câu. |
| Quy trình xét và chi trả (838 ký tự) | SentenceChunker (`by_sentences`) | 3 | 278,0 | Có — mỗi bước còn nguyên nghĩa, nhưng chunk khá dài. |
| Quy trình xét và chi trả (838 ký tự) | RecursiveChunker (`recursive`) | 6 | 138,3 | Một phần — giữ được đoạn/bước nhưng có thể tách khỏi heading. |
| Học bổng tuyển sinh K46 (1.434 ký tự) | FixedSizeChunker (`fixed_size`) | 8 | 179,2 | Không ổn định — bảng tiêu chí và số liệu có thể bị chia ngang. |
| Học bổng tuyển sinh K46 (1.434 ký tự) | SentenceChunker (`by_sentences`) | 3 | 476,0 | Có về câu, nhưng chunk quá dài do các dòng bảng không có dấu kết câu. |
| Học bổng tuyển sinh K46 (1.434 ký tự) | RecursiveChunker (`recursive`) | 10 | 142,0 | Một phần — giữ ranh giới Markdown tốt hơn nhưng không mang heading sang mảnh sau. |

### Chiến lược

**Thành viên — Đinh Thị Minh Tâm (R3)**
- **Loại chiến lược:** Custom `HeadingChunker` kết hợp `RecursiveChunker`.
- **Mô tả & lý do chọn:** Văn bản quy định có cấu trúc `#`, `##` rõ ràng, nên tách ngay trước heading giúp mỗi chunk tương ứng với một mục nghiệp vụ hoàn chỉnh. Nếu section vượt ngưỡng, phần thân được chẻ đệ quy và heading được gắn lại vào **mọi** mảnh con để các mảnh sau không mất ngữ cảnh điều khoản.
- **Code snippet (nếu custom):** Xem cài đặt đầy đủ tại `src/chunking.py`.
```python
section = f"{heading}\n{body}"
if len(section) <= chunk_size:
    chunks.append(section)
else:
    body_budget = chunk_size - len(heading) - 1
    for child in RecursiveChunker(chunk_size=body_budget).chunk(body):
        chunks.append(f"{heading}\n{child}")  # lặp heading cho từng mảnh
```

### So Sánh Giữa Các Thành Viên

Nhóm hiện có một thành viên, vì vậy phần so sánh dùng ba baseline làm đối chứng với chiến lược custom; không gán điểm benchmark giả cho các baseline chưa chạy đủ năm câu hỏi.

| Chiến lược | Kết quả/điểm đã đo | Điểm mạnh | Điểm yếu |
|---|---:|---|---|
| Fixed-size | Baseline: 11/5/8 chunk trên ba tài liệu | Kích thước dễ kiểm soát, triển khai đơn giản. | Cắt giữa câu, điều kiện hoặc hàng bảng; ngữ cảnh không ổn định. |
| Sentence | Baseline: 7/3/3 chunk | Giữ câu trọn vẹn, dễ đọc. | Độ dài trung bình lên tới 476 ký tự vì bảng/danh sách ít dấu kết câu. |
| Recursive | Baseline: 15/6/10 chunk | Ưu tiên ranh giới đoạn và kiểm soát kích thước tốt hơn. | Mảnh sau có thể mất heading nên khó biết đang thuộc điều kiện hoặc quy trình nào. |
| Heading + Recursive | Benchmark: **7/10**, 22 chunk trên toàn corpus | Bám cấu trúc tài liệu; lặp heading cho mảnh con; truy nguyên tốt. | Có thể tách các ý của cùng một danh sách sang nhiều chunk; câu 2 thiếu một nhóm điều kiện và câu 4 không lấy đúng section. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> `HeadingChunker` kết hợp `RecursiveChunker` là chiến lược phù hợp nhất cho corpus quy định học bổng vì các heading đã biểu diễn ranh giới ngữ nghĩa tự nhiên giữa điều kiện, mức học bổng và quy trình. So với fixed-size dễ cắt ngang điều khoản và sentence chunking tạo chunk quá dài ở bảng/danh sách, chiến lược này giữ section nguyên vẹn khi có thể và gắn lại heading vào mọi mảnh con khi phải chẻ nhỏ, nên mỗi kết quả vẫn đủ ngữ cảnh để kiểm chứng Gold Answer. Đổi lại, việc lặp heading làm tăng nhẹ số ký tự và số chunk, nhưng chi phí này hợp lý vì cải thiện tính mạch lạc và khả năng truy nguyên.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

**Embedding backend dùng khi benchmark:** `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`EMBEDDING_PROVIDER=local`). Đây là embedder đa ngữ thật, chạy cục bộ và chuẩn hóa vector; kết quả cosine trong phần đánh giá không sử dụng `MockEmbedder`.

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | **[Tra số liệu]** Có bao nhiêu sinh viên nhận học bổng bán phần trong chương trình học bổng tuyển sinh Khóa 46 năm 2020? | Có **356 sinh viên** nhận học bổng bán phần. | `thong-bao-ve-viec-hoc-bong-tuyen-sinh-dai-hoc-chinh-quy-nam-2020-khoa-46-dhcq.md` — mục **Số người nhận**. |
| 2 | **[Điều kiện áp dụng — cần lọc metadata]** Để được xét và nhận học bổng khuyến khích học tập cần thực hiện như thế nào? | Phải đang trong 8 học kỳ chính; có kết quả học tập và rèn luyện từ loại khá trở lên; không bị kỷ luật từ mức khiển trách; mọi học phần được tính phải đạt ít nhất 5/10; và đăng ký ít nhất 15 tín chỉ theo kế hoạch, không tính học trả nợ hoặc học cải thiện. | `quy-dinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap-cho-sinh-vien-dai-hoc-chinh-quy-trong-dao-tao-theo-he-thong-tin-chi.md` — mục **Điều kiện tham gia xét học bổng**; chạy với `metadata_filter={"audience": "student"}`. |
| 3 | **[Quy trình thực hiện]** Quy trình xét và chi trả học bổng khuyến khích học tập gồm những bước nào? | (1) Sau khi có điểm, Hội đồng xét học bổng họp và quyết định mức, điểm xét theo khóa/chuyên ngành; (2) Phòng Quản lý đào tạo – Công tác sinh viên công bố danh sách và thời gian nhận khiếu nại; (3) Phòng Tài chính – Kế toán công bố thời gian, địa điểm nhận học bổng. | `quy-trinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap.md` — mục **Trình tự thực hiện**. |
| 4 | **[Liệt kê]** Hãy liệt kê ba mức học bổng tuyển sinh Khóa 46 năm 2020 và giá trị tương ứng. | Học bổng xuất sắc bằng 1,5 lần mức học phí học kỳ cuối năm 2020 chương trình đại trà; học bổng toàn phần bằng 1 lần mức học phí đó; học bổng bán phần bằng 0,5 lần mức học phí đó. | `thong-bao-ve-viec-hoc-bong-tuyen-sinh-dai-hoc-chinh-quy-nam-2020-khoa-46-dhcq.md` — mục **Giá trị học bổng**. |
| 5 | **[Tra mốc thời gian]** Việc chi trả học bổng khuyến khích học tập học kỳ cuối năm 2020 cho sinh viên Khóa 43, 44 và 45 dự kiến được thông báo khi nào? | Phòng Tài chính – Kế toán dự kiến thông báo việc chi trả trong **tháng 12/2020** trên website của phòng. | `quyet-dinh-cap-hoc-bong-khuyen-khich-hoc-tap-va-danh-sach-sinh-vien-khoa-43-44-45-dhcq-dat-hoc-bong-khuyen-khich-hoc-tap-hkc-nam-2020.md` — đoạn thông báo kết quả. |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Số sinh viên nhận học bổng bán phần K46 | Heading + Recursive | Có — Top-1 | Chunk `...khoa-46-dhcq#5` chứa trực tiếp “356 sinh viên”; **2/2 điểm**. |
| 2 | Điều kiện để được xét và nhận học bổng KKHT | Heading + Recursive + `audience=student` | Có nhưng chưa đủ — Top-1 | Top-1 chứa điều kiện 15 tín chỉ, nhưng chunk chứa ba điều kiện còn lại (`#4`) không vào Top-3; ngữ cảnh chỉ trả lời được một phần Gold Answer; **1/2 điểm**. |
| 3 | Quy trình xét và chi trả học bổng KKHT | Heading + Recursive | Có — Top-1 và Top-3 | `#1` chứa bước 1–2, `#2` chứa bước 3; ghép context Top-3 trả lời đủ quy trình; **2/2 điểm**. |
| 4 | Ba mức học bổng tuyển sinh K46 và giá trị | Heading + Recursive | Không | Top-3 có chunk tiêu đề của đúng tài liệu nhưng không có section `#1` chứa các mức 1,5/1/0,5; không chấm đúng chỉ dựa vào `doc_id`; **0/2 điểm**. |
| 5 | Thời điểm thông báo chi trả HKC 2020 | Heading + Recursive | Có — Top-1 | Top-1 chứa trực tiếp mốc “tháng 12/2020”; **2/2 điểm**. |

**Tổng điểm retrieval thực nghiệm:** **7/10**. Việc kiểm tra được thực hiện ở mức nội dung chunk, không chỉ kiểm tra tài liệu gold có xuất hiện trong Top-3.

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, ở câu 2. Câu hỏi được viết trung tính, không nêu người hỏi là sinh viên hay cán bộ, trong khi corpus có tài liệu `audience=student` về điều kiện và tài liệu `audience=staff` về quy trình cùng loại học bổng. Thử nghiệm A/B dùng cùng `HeadingChunker`, model local đa ngữ và `top_k=3` cho kết quả sau:

| Hạng | Không dùng filter | Score | Dùng `audience=student` | Score |
|---|---|---:|---|---:|
| 1 | Điều kiện sinh viên — chunk `...he-thong-tin-chi#5` | 0,6779 | Điều kiện sinh viên — chunk `...he-thong-tin-chi#5` | 0,6779 |
| 2 | Điều kiện sinh viên — chunk `...he-thong-tin-chi#3` | 0,6769 | Điều kiện sinh viên — chunk `...he-thong-tin-chi#3` | 0,6769 |
| 3 | Quy trình cán bộ (`audience=staff`) — chunk `quy-trinh-xet-cap-hoc-bong-khuyen-khich-hoc-tap#1` | 0,6690 | Nội dung sinh viên — chunk `...he-thong-tin-chi#6` | 0,6388 |

> Như vậy, filter đã loại chunk quy trình dành cho cán bộ khỏi Top-3 và thay bằng chunk thuộc tài liệu sinh viên. Kết quả này chứng minh metadata được thừa kế tới từng chunk và được lọc trước bước xếp hạng vector.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> - Đúng `doc_id` chưa đủ để kết luận retrieval thành công: ở câu 4, tài liệu K46 xuất hiện trong Top-3 nhưng section chứa ba mức học bổng không xuất hiện, nên context vẫn không trả lời được.
> - Heading giúp giữ chủ đề cho các mảnh nhỏ; tuy nhiên một danh sách dài có thể bị tách thành nhiều chunk, khiến câu 2 chỉ truy xuất được điều kiện 15 tín chỉ mà bỏ sót ba điều kiện còn lại.
> - Metadata filtering tạo khác biệt đo được: với câu 2, filter `audience=student` loại chunk quy trình `staff` khỏi Top-3 và thay bằng chunk của tài liệu sinh viên.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một nội dung, fixed-size kiểm soát độ dài nhưng dễ cắt ngang ý, sentence chunking giữ ngữ pháp nhưng sinh chunk quá dài ở bảng, còn recursive giữ ranh giới đoạn nhưng có thể tách đoạn khỏi heading. Heading + Recursive phù hợp hơn với quy chế có cấu trúc, song kết quả 7/10 cho thấy cấu trúc tốt không tự đảm bảo retrieval đúng: kích thước section con và cách xếp hạng embedding vẫn quyết định Gold Answer có nằm trong Top-3 hay không.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ gộp phần mở đầu ngắn của section với danh sách ngay sau nó, đồng thời dùng overlap theo đơn vị bullet để các điều kiện liên quan có thể cùng xuất hiện trong một chunk. Với bảng và danh sách số liệu, nhóm sẽ bổ sung metadata `category` cụ thể hơn hoặc tiền tố tiêu đề tài liệu vào content embedding, rồi chạy lại A/B nhiều giá trị `chunk_size` trên đúng năm câu benchmark trước khi chốt chiến lược.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 13 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **34 / 40** |
