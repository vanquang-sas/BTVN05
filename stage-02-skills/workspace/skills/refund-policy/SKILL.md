---
name: refund-policy
description: Tra cứu, đối chiếu và tư vấn điều kiện hoàn tiền cho khách hàng dựa trên chính sách theo ngày mua. Sử dụng khi người dùng hỏi về hoàn tiền, hủy đơn, trả hàng hoặc đối soát phí hoàn tiền sản phẩm.
---

## Tổng quan

Skill này hướng dẫn Agent xác định chính sách hoàn tiền chính xác cho đơn hàng dựa trên thời điểm mua hàng, kiểm tra tính hợp lệ và trả lời theo biểu mẫu chuẩn. Toàn bộ thao tác đọc tài liệu được thực hiện thông qua các tool file (`list_files`, `read_file`), tuyệt đối không dùng shell/script.

## Quy trình thực hiện

### Bước 1: Thu thập đủ thông tin tiên quyết
Trước khi tra cứu hoặc đưa ra kết luận, bắt buộc phải có đầy đủ 3 thông tin sau:
1. **Ngày mua hàng (Purchase Date)**
2. **Ngày yêu cầu hoàn tiền (Request Date)**
3. **Trạng thái kích hoạt/sử dụng sản phẩm (Activation Status - đã kích hoạt hay chưa)**

> **QUAN TRỌNG:** Nếu người dùng cung cấp thiếu bất kỳ thông tin nào trong 3 thông tin trên, dừng lại và đặt câu hỏi làm rõ trước khi kết luận. Không tự giả định các mốc thời gian hay trạng thái kích hoạt.

### Bước 2: Tìm và chọn tài liệu chính sách
1. Sử dụng tool `list_files(path="data/policies")` để liệt kê các file chính sách đang có.
2. Dùng tool `read_file` để đọc phần **Phạm vi hiệu lực (Effective Date / Validity Period)** của các tài liệu tìm được.
3. Đối chiếu **Ngày mua hàng** của khách với phạm vi hiệu lực của từng tài liệu để chọn ra duy nhất tài liệu chính sách áp dụng cho thời điểm mua đó.

### Bước 3: Tính toán và đối chiếu điều kiện
1. Tính số ngày đã trôi qua kể từ ngày mua:
   $$\text{Số ngày đã qua} = \text{Ngày yêu cầu} - \text{Ngày mua}$$
2. Đối chiếu số ngày đã qua và trạng thái kích hoạt với các mốc quy định trong tài liệu chính sách đã chọn:
   - Đủ điều kiện hoàn tiền hay không.
   - Mức phí hoàn tiền (hoặc tỷ lệ hoàn tiền/khấu trừ) nếu đủ điều kiện.

### Bước 4: Định dạng câu trả lời
- Đọc file mẫu tại `skills/refund-policy/references/answer-template.md`.
- Trình bày câu trả lời theo đúng cấu trúc và các trường thông tin được quy định trong template.