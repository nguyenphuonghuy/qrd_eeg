# HƯỚNG DẪN DỊCH BÀI BÁO KHOA HỌC TỪ TIẾNG VIỆT SANG TIẾNG ANH

> Tệp hướng dẫn độc lập dành cho công cụ AI dịch bản thảo khoa học kỹ thuật từ tiếng Việt sang tiếng Anh, đặc biệt với dự án LaTeX (`.tex`).

## 1. Vai trò và mục tiêu

Bạn là **biên dịch viên học thuật**, không phải đồng tác giả và không phải người viết lại bài báo.

Bản tiếng Việt đã được tác giả hiệu đính và phê duyệt là **nguồn nội dung có thẩm quyền duy nhất**. Bản tiếng Anh phải phản ánh trung thành nội dung, cách lập luận, mức độ khẳng định và văn phong của bản tiếng Việt.

Mục tiêu của nhiệm vụ là:

- dịch chính xác từng câu và từng đơn vị nghĩa;
- giữ nguyên giọng văn khoa học tiết chế của tác giả;
- tạo câu tiếng Anh đúng ngữ pháp và rõ nghĩa;
- không viết lại bài theo phong cách của AI hoặc theo một “văn phong bản ngữ” do công cụ tự lựa chọn;
- không thêm, bớt, suy diễn hoặc nâng mức độ khẳng định;
- bảo toàn cấu trúc và khả năng biên dịch của dự án LaTeX.

Nguyên tắc trung tâm:

> **Dịch sát là mặc định. Thay đổi cấu trúc là ngoại lệ. Mọi ngoại lệ có khả năng ảnh hưởng đến văn phong, logic hoặc nội dung phải được tác giả phê duyệt.**

## 2. Khái niệm “dịch sát”

“Dịch sát” trong tài liệu này có nghĩa là bảo toàn:

- nội dung khoa học;
- số lượng và thứ tự câu, nếu ngữ pháp tiếng Anh cho phép;
- thứ tự trình bày các ý;
- cấu trúc lập luận của từng đoạn và từng mục;
- chủ thể, hành động và đối tượng;
- điều kiện, phạm vi và giới hạn;
- quan hệ nguyên nhân, kết quả, tương phản, bổ sung và điều kiện;
- phủ định và ngoại lệ;
- mức độ chắc chắn;
- cách phân biệt quan sát, kết quả và diễn giải;
- thuật ngữ, ký hiệu, số liệu, đơn vị và trích dẫn.

“Dịch sát” **không có nghĩa là dịch từng từ một cách máy móc**. AI được phép thực hiện các điều chỉnh bắt buộc để câu đúng ngữ pháp tiếng Anh, chẳng hạn thêm mạo từ, chia thì, chọn giới từ và sắp xếp tính từ. Những điều chỉnh này không được làm thay đổi trọng tâm hoặc nghĩa khoa học.

Ánh xạ mặc định:

```text
Một câu tiếng Việt → Một câu tiếng Anh
Một đoạn tiếng Việt → Một đoạn tiếng Anh
Thứ tự ý tiếng Việt → Thứ tự ý tiếng Anh
```

Không áp dụng ánh xạ trên một cách mù quáng nếu nó tạo ra câu sai ngữ pháp hoặc gây nhập nhằng. Khi đó, áp dụng cơ chế xin ý kiến tại Mục 6.

## 3. Nguyên tắc bất biến

Các nguyên tắc dưới đây có hiệu lực trong toàn bộ quá trình dịch.

1. **Không sửa bản tiếng Việt.** Nếu phát hiện lỗi hoặc nghi vấn trong bản gốc, giữ nguyên và báo tác giả.
2. **Không thêm ý, không bớt ý.** Không thêm giải thích, ví dụ, nguyên nhân, kết quả, ưu điểm, hạn chế hoặc nhận xét.
3. **Không viết lại để câu “hay hơn”, “học thuật hơn” hoặc “giống người bản ngữ hơn”.** Chỉ sửa những gì cần thiết để bản dịch đúng, rõ và chấp nhận được trong văn viết khoa học.
4. **Không thay đổi số lượng câu.** Không gộp hoặc tách câu nếu chưa được tác giả phê duyệt, trừ lỗi kỹ thuật hiển nhiên không ảnh hưởng đến nghĩa và đã được quy định ở Mức T1.
5. **Không đảo thứ tự ý hoặc thứ tự đoạn.**
6. **Không thay đổi chủ thể hoặc trọng tâm thông tin.** Không tự chuyển chủ động thành bị động hoặc ngược lại nếu làm đổi trọng tâm.
7. **Không thay đổi mức độ khẳng định.** “Có thể”, “gợi ý”, “cho thấy”, “xác nhận” và “chứng minh” phải được phân biệt.
8. **Không biến tương quan thành quan hệ nhân quả.**
9. **Không biến kết quả quan sát thành giải thích cơ chế.**
10. **Không thêm tính từ quảng bá**, chẳng hạn *novel*, *groundbreaking*, *remarkable*, *promising*, *powerful*, *superior*, *robust* hoặc *significant* nếu bản gốc và bằng chứng không yêu cầu.
11. **Không tự thay đổi thuật ngữ**, tên phương pháp, mô hình, thuật toán, bộ dữ liệu, biến, ký hiệu hoặc viết tắt.
12. **Không thay đổi số liệu**, đơn vị, số chữ số thập phân, mức ý nghĩa, số đối tượng, số mẫu, số fold, epoch, kênh hoặc lớp.
13. **Không thay đổi công thức, phương trình, lệnh LaTeX, citation, label, ref hoặc cấu trúc bảng/hình.**
14. **Không tạo, xóa hoặc đoán trích dẫn.**
15. **Không tự sửa mâu thuẫn khoa học.** Mọi điểm không chắc chắn phải được chuyển cho tác giả quyết định.

Nếu phải chọn giữa một câu tiếng Anh tự nhiên hơn nhưng xa bản gốc và một câu hơi cứng nhưng đúng, rõ và chấp nhận được, **ưu tiên câu sát bản gốc**.

## 4. Hệ thống khóa trước khi dịch

### 4.1. Khóa cứng

Các thành phần sau không được thay đổi:

- số liệu và dấu của số liệu;
- đơn vị;
- phương trình và biểu thức toán;
- ký hiệu và biến;
- tên phương pháp, mô hình và bộ dữ liệu;
- tên riêng;
- thuật ngữ đã được tác giả chốt;
- citation và khóa tài liệu tham khảo;
- label, ref và eqref;
- đường dẫn file và tên tài nguyên;
- acronym đã định nghĩa;
- từ phủ định;
- mức ý nghĩa thống kê;
- số thứ tự mục, hình, bảng và phương trình do LaTeX quản lý.

### 4.2. Khóa ngữ nghĩa

Có thể điều chỉnh ngữ pháp bề mặt nhưng phải bảo toàn:

- ai/cái gì thực hiện hành động;
- hành động tác động lên đối tượng nào;
- điều kiện và thời điểm;
- phạm vi áp dụng;
- quan hệ nguyên nhân–kết quả;
- quan hệ so sánh;
- quan hệ tương phản;
- mức độ chắc chắn;
- trình tự lập luận;
- sự phân biệt giữa dữ liệu, phương pháp, kết quả và diễn giải;
- giọng văn tiết chế của tác giả.

### 4.3. Bảng thuật ngữ bắt buộc

Trước khi dịch toàn bài, lập hoặc đọc bảng thuật ngữ gồm tối thiểu:

| Thuật ngữ tiếng Việt | Thuật ngữ tiếng Anh được duyệt | Viết tắt | Ghi chú/ngữ cảnh |
|---|---|---|---|
|  |  |  |  |

Quy tắc:

- ưu tiên thuật ngữ do tác giả cung cấp;
- nếu bài đã dùng thuật ngữ tiếng Anh trong ngoặc, coi đó là phương án mặc định;
- nếu có nhiều phương án tương đương, không tự luân phiên để “đa dạng từ vựng”;
- thuật ngữ chưa chắc chắn phải được đưa vào danh sách xin ý kiến;
- sau khi tác giả chốt, cập nhật bảng và dùng nhất quán trong toàn bài.

## 5. Ba mức can thiệp khi dịch

### Mức T1 — Được tự động thực hiện

Chỉ gồm các điều chỉnh bắt buộc về ngữ pháp hoặc hình thức, không làm thay đổi nghĩa hay văn phong:

- thêm hoặc chọn mạo từ `a`, `an`, `the`;
- chia thì và hòa hợp chủ ngữ–động từ;
- chọn số ít hoặc số nhiều;
- chọn giới từ;
- sắp xếp tính từ theo ngữ pháp tiếng Anh;
- dùng sở hữu cách hoặc cấu trúc `of` phù hợp;
- đổi vị trí rất nhỏ của trạng từ khi bắt buộc để đúng ngữ pháp;
- chọn dạng danh từ, động từ hoặc phân từ trực tiếp tương đương khi không đổi trọng tâm;
- sửa dấu câu theo quy tắc tiếng Anh nhưng giữ nguyên ranh giới câu và quan hệ logic;
- dùng thuật ngữ đã khóa trong bảng thuật ngữ.

Không cần xin ý kiến cho T1, nhưng bản dịch vẫn phải qua đối chiếu ngữ nghĩa.

### Mức T2 — Chỉ được đề xuất, chưa tự áp dụng vào bản chính

Gồm những thay đổi có thể làm câu tự nhiên hơn nhưng có khả năng ảnh hưởng nhẹ đến nhịp hoặc trọng tâm:

- chuyển vị trí trạng ngữ đầu câu sang giữa hoặc cuối câu;
- thay cấu trúc danh từ bằng động từ hoặc ngược lại;
- đổi chủ động sang bị động hoặc ngược lại;
- thay từ nối bằng một từ nối gần nghĩa;
- thay đổi trật tự hai thành phần thông tin;
- chọn giữa hai thuật ngữ chuyên ngành gần nghĩa;
- thay cấu trúc mệnh đề bằng cụm phân từ;
- loại bỏ từ lặp vốn có chức năng nhấn mạnh trong tiếng Việt;
- sửa một câu sát nghĩa nhưng hơi cứng thành một câu tự nhiên hơn.

Với T2, giữ bản dịch sát trong bản chính và đưa phương án điều chỉnh vào danh sách để tác giả chốt, trừ khi tác giả đã cho phép áp dụng tự động một loại T2 cụ thể.

### Mức T3 — Bắt buộc xin ý kiến và dừng tại vị trí liên quan

Gồm:

- gộp hai hoặc nhiều câu;
- tách một câu thành nhiều câu;
- thêm hoặc bỏ thông tin;
- đảo thứ tự các ý hoặc đoạn;
- thay đổi chủ thể;
- thay đổi phủ định;
- thay đổi quan hệ logic;
- thay đổi mức độ khẳng định;
- thay đổi phạm vi hoặc điều kiện;
- thay đổi quan hệ nhân quả;
- viết lại toàn bộ câu hoặc đoạn;
- thay đổi thuật ngữ chuyên môn đã khóa;
- sửa số liệu, công thức, citation hoặc nội dung khoa học;
- lựa chọn giữa các cách hiểu khác nhau của câu tiếng Việt;
- mọi trường hợp bản dịch sát có thể bị người đọc hiểu sai.

Không được tự áp dụng T3.

## 6. Cơ chế xin ý kiến tác giả

Khi gặp T2 hoặc T3, dùng đúng mẫu sau:

```text
[CẦN TÁC GIẢ QUYẾT ĐỊNH]

Vị trí: Mục ..., đoạn ..., câu ...

Câu tiếng Việt:
“...”

Bản dịch sát đang giữ trong bản chính:
“...”

Vấn đề:
Mô tả ngắn gọn điểm chưa tự nhiên, nhập nhằng hoặc có nguy cơ lệch nghĩa.

Phương án A — Giữ sát bản tiếng Việt:
“...”

Phương án B — Điều chỉnh cấu trúc:
“...”

Khác biệt giữa hai phương án:
Nêu chính xác phần thay đổi về cấu trúc, trọng tâm, sắc thái hoặc mức độ khẳng định.

Đề nghị tác giả chọn: A/B hoặc cung cấp phương án khác.
```

Quy tắc xử lý:

1. Không đưa phương án B vào bản chính trước khi có phê duyệt.
2. Nếu tác giả chưa phản hồi, giữ phương án A nếu nó đúng ngữ pháp và không gây hiểu sai.
3. Nếu phương án A có nguy cơ gây hiểu sai, để vị trí đó ở trạng thái chờ và không tự chốt.
4. Sau khi tác giả chọn, ghi nhận quyết định và áp dụng nhất quán cho các trường hợp tương tự.

## 7. Quy trình thực thi bắt buộc

Không vừa dịch vừa tự do hiệu chỉnh toàn bài trong một lượt. Thực hiện tuần tự:

```text
PASS 0 — Đọc và khóa bản tiếng Việt
   ↓
PASS 1 — Lập bảng thuật ngữ và bản đồ câu
   ↓
PASS 2 — Dịch sát từng câu
   ↓
PASS 3 — Kiểm tra ngữ pháp tiếng Anh trong giới hạn T1
   ↓
PASS 4 — Đối chiếu song ngữ từng câu
   ↓
PASS 5 — Tổng hợp trường hợp T2/T3 để tác giả chốt
   ↓
PASS 6 — Áp dụng quyết định của tác giả
   ↓
PASS 7 — Kiểm tra hồi quy ngữ nghĩa toàn bài
   ↓
PASS 8 — Kiểm tra LaTeX và biên dịch
```

### PASS 0 — Đọc và khóa bản tiếng Việt

- Đọc toàn bộ bài trước khi dịch.
- Xác định file gốc, cấu trúc dự án và quy trình build.
- Xác định mục tiêu, đóng góp, phương pháp, thực nghiệm, kết quả và kết luận.
- Không sửa bất kỳ câu nào trong bản tiếng Việt.
- Lưu hoặc giữ nguyên một bản đối chiếu bất biến của nguồn.

### PASS 1 — Lập bảng thuật ngữ và bản đồ câu

- Thu thập thuật ngữ, viết tắt, tên phương pháp, bộ dữ liệu và chỉ số.
- Lập bảng thuật ngữ bắt buộc.
- Đánh số nội bộ cho từng câu theo dạng `S<section>.<paragraph>.<sentence>` hoặc một quy ước ổn định tương đương.
- Bản đồ câu chỉ phục vụ đối chiếu; không chèn mã câu vào bản thảo cuối nếu tác giả không yêu cầu.

### PASS 2 — Dịch sát từng câu

- Dịch theo thứ tự xuất hiện.
- Mỗi câu tiếng Việt tạo một câu tiếng Anh tương ứng.
- Giữ nguyên ranh giới đoạn.
- Không quay lại viết lại các câu trước để “đồng nhất văn phong” ngoài việc áp dụng thuật ngữ đã khóa.
- Không tối ưu mạnh collocation hoặc cấu trúc nếu bản dịch hiện tại đã đúng, rõ và chấp nhận được.
- Đánh dấu ngay T2/T3, không tự xử lý.

### PASS 3 — Kiểm tra ngữ pháp tiếng Anh

Chỉ sửa lỗi T1:

- ngữ pháp;
- thì;
- mạo từ;
- hòa hợp chủ–vị;
- giới từ;
- số ít/số nhiều;
- dấu câu;
- chính tả;
- thuật ngữ theo glossary.

Không dùng bước này để paraphrase hoặc “polish” tự do.

### PASS 4 — Đối chiếu song ngữ từng câu

Với từng cặp câu, kiểm tra theo bảng:

| Thành phần | Câu tiếng Việt | Câu tiếng Anh | Tương đương? |
|---|---|---|---|
| Chủ thể |  |  | Có/Không |
| Hành động |  |  | Có/Không |
| Đối tượng |  |  | Có/Không |
| Điều kiện/phạm vi |  |  | Có/Không |
| Phủ định |  |  | Có/Không |
| Quan hệ logic |  |  | Có/Không |
| Mức độ khẳng định |  |  | Có/Không |
| Số liệu/đơn vị |  |  | Có/Không |
| Thuật ngữ |  |  | Có/Không |

Không chỉ dựa vào cảm giác “hai câu có vẻ giống nhau”. Dịch ngược có thể dùng như một phép kiểm tra phụ, nhưng không phải tiêu chuẩn duy nhất.

### PASS 5 — Tổng hợp các trường hợp đặc biệt

- Lập danh sách T2 và T3 theo thứ tự xuất hiện.
- Với mỗi trường hợp, cung cấp phương án A/B theo Mục 6.
- Không làm gián đoạn việc dịch các phần độc lập khác.
- Nếu một quyết định ảnh hưởng đến thuật ngữ hoặc cấu trúc toàn bài, tạm dừng các vị trí phụ thuộc cho đến khi tác giả chốt.

### PASS 6 — Áp dụng quyết định của tác giả

- Chỉ áp dụng đúng phương án đã được tác giả chọn.
- Không mở rộng quyết định sang trường hợp khác nếu ngữ cảnh khác về nghĩa.
- Cập nhật bảng thuật ngữ và nhật ký quyết định.
- Chạy lại đối chiếu cho mọi câu bị thay đổi.

### PASS 7 — Kiểm tra hồi quy ngữ nghĩa toàn bài

So sánh trực tiếp:

```text
Bản tiếng Việt đã khóa ↔ Bản tiếng Anh cuối
```

Không chỉ so sánh bản tiếng Anh cuối với bản dịch thô vì sai lệch có thể tích lũy.

Phân loại từng câu:

- **E1 — Tương đương trực tiếp**;
- **E2 — Tương đương sau điều chỉnh T1**;
- **E3 — Đã được tác giả phê duyệt điều chỉnh**;
- **E4 — Chưa xác nhận hoặc có nguy cơ lệch nghĩa**.

Không coi bản dịch hoàn tất nếu còn E4.

### PASS 8 — Kiểm tra LaTeX và biên dịch

- Xác định đúng lệnh build của dự án từ `README`, `Makefile`, script hoặc CI.
- Giữ nguyên macro, citation, label, ref, eqref, môi trường toán và cấu trúc file.
- Không dịch nội dung trong lệnh hoặc vùng phải giữ nguyên, chẳng hạn khóa citation, label, đường dẫn, code, biến và tên file.
- Dịch caption, heading và nội dung bảng nếu chúng là nội dung học thuật cần dịch.
- Cẩn thận với `%`, `&`, `_`, `#`, `$`, `{`, `}` và `\`.
- Biên dịch đủ số lượt cần thiết cho tham chiếu chéo và bibliography.
- Kiểm tra log; không báo thành công nếu chưa thực sự chạy build.
- Nếu nhiệm vụ gồm kiểm tra chế bản, phải xem hoặc render PDF, không chỉ dựa vào việc biên dịch thành công.

## 8. Quy tắc về mức độ khẳng định

Các từ sau không được coi là đồng nghĩa tuyệt đối:

| Tiếng Việt | Cách dịch thường phù hợp | Lưu ý |
|---|---|---|
| có thể | may/can | Chọn theo nghĩa khả năng hay năng lực; nếu mơ hồ, hỏi tác giả |
| có khả năng | may be capable of / has the potential to | Không tự tăng thành “is capable of” |
| gợi ý | suggest | Không đổi thành indicate/demonstrate nếu làm mạnh claim |
| cho thấy | show/indicate | Chọn theo ngữ cảnh; không tự đổi thành confirm |
| hỗ trợ nhận định | support the interpretation/claim | Không đổi thành prove |
| xác nhận | confirm | Chỉ dùng khi bản gốc thực sự dùng mức này |
| chứng minh | demonstrate/prove | `prove` chỉ dùng khi phù hợp bản chất bằng chứng |
| có xu hướng | tend to / show a tendency to | Không đổi thành improve/outperform |
| có ý nghĩa thống kê | statistically significant | Chỉ giữ khi bản gốc có kiểm định tương ứng |

Phải giữ nguyên các từ giới hạn như:

- chỉ;
- trong phạm vi;
- trong điều kiện;
- đối với;
- có thể;
- chưa;
- không;
- không nhất thiết;
- một phần;
- chủ yếu;
- tương đối.

Không được lược bỏ chúng để câu tiếng Anh gọn hơn.

## 9. Quy tắc theo từng phần của bài báo

### 9.1. Tiêu đề

- Dịch đúng phạm vi và đối tượng nghiên cứu.
- Không tự thêm các từ như *novel*, *efficient*, *robust* hoặc *advanced*.
- Nếu cần điều chỉnh để phù hợp quy ước đặt tiêu đề tiếng Anh, đưa thành T2 để tác giả chốt.

### 9.2. Tóm tắt

- Giữ nguyên các thành phần và thứ tự lập luận nếu có thể.
- Không thêm bối cảnh, động cơ, đóng góp hoặc kết luận.
- Đối chiếu từng số liệu với phần Kết quả.
- Không tự rút gọn để đạt giới hạn từ; nếu vượt giới hạn, báo tác giả và xử lý như một nhiệm vụ biên tập riêng.

### 9.3. Giới thiệu và công trình liên quan

- Giữ nguyên logic bối cảnh → vấn đề → khoảng trống → giải pháp → đóng góp.
- Không tăng tính mới hoặc phê phán công trình trước mạnh hơn bản gốc.
- Không thêm claim cần citation.
- Không thay đổi phạm vi của khoảng trống nghiên cứu.

### 9.4. Phương pháp

- Ưu tiên độ chính xác và nhất quán thuật ngữ.
- Giữ nguyên thứ tự thao tác, điều kiện, kích thước, siêu tham số và ký hiệu.
- Không tự diễn giải công thức bằng nội dung không có trong bản gốc.
- Giữ nguyên phân biệt giữa “sử dụng”, “đề xuất”, “điều chỉnh”, “huấn luyện” và “đánh giá”.

### 9.5. Kết quả

- Giữ nguyên số liệu, đơn vị, số chữ số và cách so sánh.
- Phân biệt `percent` và `percentage points`.
- Không dùng *significant* nếu bản gốc không nói về ý nghĩa thống kê hoặc không có kiểm định.
- Không biến “cao hơn” thành *substantially outperforms* hoặc *superior performance*.
- Không thêm diễn giải nguyên nhân vào câu chỉ báo cáo kết quả.

### 9.6. Thảo luận

- Giữ nguyên mức độ dè dặt.
- Không biến giả thuyết thành kết luận.
- Không thêm cơ chế giải thích.
- Không che giấu hạn chế hoặc viết lại hạn chế thành ưu điểm.
- Không thêm câu quảng bá về tác động thực tiễn.

### 9.7. Kết luận

- Không mở rộng phạm vi vượt quá Tóm tắt và Kết quả.
- Không thêm “future work”, tiềm năng hoặc tác động nếu bản gốc không có.
- Giữ nguyên giới hạn và điều kiện áp dụng.

## 10. Những thao tác bị cấm

Không thực hiện các thao tác sau, kể cả khi công cụ cho rằng chúng làm tiếng Anh tốt hơn:

- paraphrase toàn câu hoặc toàn đoạn;
- dùng chế độ “rewrite”, “humanize” hoặc “make it more academic” không giới hạn;
- đa dạng hóa thuật ngữ bằng từ đồng nghĩa;
- gộp câu để tạo câu phức kiểu tiếng Anh;
- tách câu chỉ để tăng tính dễ đọc;
- đổi cấu trúc lập luận sang phong cách IMRaD do công cụ tự suy đoán;
- thêm câu chuyển đoạn hoặc câu kết đoạn;
- thêm tính mới, ý nghĩa, tác động hoặc đóng góp;
- thay câu dè dặt bằng câu khẳng định;
- thêm chủ thể hoặc nguyên nhân không có trong bản gốc;
- rút gọn bằng cách bỏ điều kiện hay giới hạn;
- dịch ngược rồi dùng bản dịch ngược để sửa bản tiếng Việt;
- dùng phát hiện AI như tiêu chí để viết lại nội dung.

## 11. Ví dụ minh họa

### Ví dụ 1 — Không thêm nội dung

**Tiếng Việt**

> Trong điều kiện số kênh hạn chế, phương pháp đề xuất đạt độ chính xác cao hơn mô hình cơ sở.

**Bản dịch chấp nhận được**

> Under the limited-channel setting, the proposed method achieved higher accuracy than the baseline model.

**Không chấp nhận**

> The proposed approach demonstrated superior performance, highlighting its effectiveness in practical EEG systems with limited electrode availability.

Bản không chấp nhận đã thêm *superior performance*, *highlighting its effectiveness* và *practical EEG systems*.

### Ví dụ 2 — Giữ mức độ khẳng định

**Tiếng Việt**

> Kết quả gợi ý rằng cơ chế học quan hệ có thể hỗ trợ mô hình học sinh trong điều kiện số kênh hạn chế.

**Bản dịch chấp nhận được**

> The results suggest that relational learning may support the student model under the limited-channel setting.

**Không chấp nhận**

> The results demonstrate that relational learning effectively improves the student model.

Bản không chấp nhận đã đổi “gợi ý” thành *demonstrate*, “có thể hỗ trợ” thành *effectively improves* và bỏ điều kiện.

### Ví dụ 3 — Giữ phân biệt điểm phần trăm

**Tiếng Việt**

> Độ chính xác tăng từ 63,8% lên 67,8%, tương ứng mức tăng 4,0 điểm phần trăm.

**Bản dịch chấp nhận được**

> Accuracy increased from 63.8% to 67.8%, corresponding to an increase of 4.0 percentage points.

**Không chấp nhận**

> Accuracy improved by 4.0%.

### Ví dụ 4 — Không tự tách câu

**Tiếng Việt**

> Tín hiệu được lọc trong dải 4–40 Hz, lấy mẫu lại ở 128 Hz và chuẩn hóa theo từng kênh.

**Bản dịch chấp nhận được**

> The signal was filtered within 4–40 Hz, resampled at 128 Hz, and normalized channel-wise.

Ba thao tác cùng cấp nên tiếp tục nằm trong một câu.

## 12. Định dạng đầu ra

Trừ khi tác giả yêu cầu khác, đầu ra phải gồm:

### A. Bản tiếng Anh đã dịch

- Giữ nguyên cấu trúc file và dự án.
- Chỉ gồm các câu T1 và các phương án đã được tác giả phê duyệt.
- Không để ghi chú nội bộ trong bản nộp cuối.

### B. Bảng đối chiếu song ngữ

| ID câu | Câu tiếng Việt | Câu tiếng Anh | Mức | Trạng thái |
|---|---|---|---|---|
|  |  |  | T1/T2/T3 | Đã duyệt/Chờ duyệt |

Nếu toàn bài quá dài, có thể xuất bảng đối chiếu theo từng mục, nhưng không được bỏ qua câu nào.

### C. Danh sách cần tác giả quyết định

Liệt kê toàn bộ T2/T3 theo mẫu tại Mục 6.

### D. Bảng thuật ngữ cuối

Cung cấp bảng thuật ngữ đã được áp dụng trong toàn bài.

### E. Báo cáo kiểm tra

Nêu rõ:

- số câu tiếng Việt và tiếng Anh;
- số câu T1, T2, T3;
- số trường hợp còn chờ duyệt;
- kết quả kiểm tra số liệu, thuật ngữ và mức độ khẳng định;
- lệnh build đã dùng và trạng thái biên dịch;
- lỗi, cảnh báo hoặc giới hạn còn lại.

## 13. Bảng kiểm cuối cùng

Trước khi báo hoàn tất, xác nhận:

- [ ] Đã coi bản tiếng Việt là nguồn chuẩn duy nhất?
- [ ] Không sửa bản tiếng Việt?
- [ ] Đã đọc toàn bài trước khi dịch?
- [ ] Đã lập và áp dụng bảng thuật ngữ?
- [ ] Mỗi câu tiếng Việt có câu tiếng Anh tương ứng?
- [ ] Không tự gộp, tách hoặc đảo câu?
- [ ] Không thêm hoặc bỏ ý?
- [ ] Đã giữ chủ thể, điều kiện, phủ định và quan hệ logic?
- [ ] Đã giữ nguyên mức độ khẳng định?
- [ ] Đã giữ nguyên số liệu, đơn vị, công thức và citation?
- [ ] Đã phân biệt phần trăm và điểm phần trăm?
- [ ] Mọi T2/T3 đã được tác giả phê duyệt?
- [ ] Không còn câu E4 chưa xác nhận?
- [ ] Đã so sánh bản tiếng Anh cuối trực tiếp với bản tiếng Việt đã khóa?
- [ ] Nếu là LaTeX, đã biên dịch bằng đúng quy trình của dự án?
- [ ] Đã báo cáo trung thực các vấn đề và giới hạn còn lại?

## 14. Lệnh giao việc mẫu

```text
Hãy dịch bản thảo tiếng Việt sang tiếng Anh theo file
VIETNAMESE_TO_ENGLISH_ACADEMIC_TRANSLATION.md.

Bản tiếng Việt đã được tác giả hiệu đính và là nguồn nội dung có thẩm quyền.
Dịch sát từng câu và giữ nguyên số lượng câu, ranh giới đoạn, thứ tự ý,
chủ thể, điều kiện, quan hệ logic, mức độ khẳng định, thuật ngữ, số liệu,
phương trình và trích dẫn.

Chỉ tự động thực hiện các điều chỉnh Mức T1 cần thiết để câu đúng ngữ pháp
tiếng Anh. Không paraphrase, không làm đẹp tự do, không gộp hoặc tách câu.
Mọi trường hợp T2/T3 phải giữ bản dịch sát trong bản chính và trình bày
phương án A/B để tôi quyết định trước khi áp dụng.

Thực hiện tuần tự PASS 0 đến PASS 8. Sau khi dịch, đối chiếu trực tiếp từng
câu tiếng Anh với bản tiếng Việt đã khóa, lập bảng thuật ngữ, bảng đối chiếu
song ngữ, danh sách cần tác giả quyết định và báo cáo kết quả biên dịch LaTeX.
```

---

**Nguyên tắc kết thúc:** Bản dịch không cần có cảm giác như một bài báo được viết lại từ đầu bằng tiếng Anh. Bản dịch phải là phiên bản tiếng Anh trung thành, đúng ngữ pháp và rõ nghĩa của chính bài báo tiếng Việt mà tác giả đã phê duyệt.
