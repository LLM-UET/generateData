generateData – Sinh dữ liệu hội thoại phân loại cảm xúc tiếng Việt (Viettel Customer Support)

Dự án này dùng để tạo bộ dữ liệu văn bản tiếng Việt phục vụ huấn luyện mô hình phân loại cảm xúc (Neutral, Negative, Positive) trong bối cảnh hội thoại chăm sóc khách hàng của Viettel. Bộ dữ liệu được sinh tự động thông qua API OpenAI, dựa trên các quy tắc rõ ràng về ngữ cảnh, chủ đề và phân bố cảm xúc.

1. Mục đích

Người dùng cần một bộ dữ liệu lớn mô phỏng tin nhắn thật của khách hàng khi trò chuyện với chatbot Viettel. Dữ liệu phải tự nhiên, đa dạng về cấu trúc câu, có thể chứa emoji, từ viết tắt, và phản ánh cảm xúc của khách hàng khi hỏi hoặc phàn nàn về các gói cước di động.

Script trong repo hỗ trợ sinh dữ liệu quy mô lớn (hàng nghìn đến hàng chục nghìn dòng) dựa trên mô hình GPT.

2. Mô tả file generate_data_hybrid.py

File generate_data_hybrid.py thực hiện ba nhiệm vụ chính:

2.1 Tạo prompt chuẩn sinh dữ liệu

Script chứa một mẫu mô tả dữ liệu chi tiết (PROMPT_BASE), bao gồm:

Mục đích của dữ liệu

Danh sách các gói cước Viettel (V90B, ST70K, MXH100, SD70, F90, Umax, Mimax70)

Phong cách diễn đạt của người dùng

Phân bố cảm xúc (40% Neutral, 40% Negative, 20% Positive)

Yêu cầu định dạng CSV (không header)

2.2 Gọi API OpenAI để sinh dữ liệu

Script sử dụng hai mô hình:

GPT-4o: cho 100 dòng đầu tiên, nhằm tạo các mẫu tự nhiên và chất lượng cao

GPT-4o-mini: cho phần còn lại để tăng tốc và giảm chi phí

Mỗi lần chạy API chỉ sinh ra chunk dòng, sau đó nối thêm vào file CSV.

2.3 Lọc sạch dữ liệu và ghi ra file CSV

Script chỉ giữ lại các dòng có dạng hợp lệ:

"văn bản",Positive
"văn bản",Negative
"văn bản",Neutral


Các đoạn thừa, ghi chú của mô hình, lời chào,… sẽ bị loại bỏ.

Script cũng tự động thêm UTF-8 BOM để tránh lỗi tiếng Việt khi mở bằng Excel.

3. Cách sử dụng
3.1 Cài đặt biến môi trường API key

Trên Windows PowerShell:

setx OPENAI_API_KEY "sk-xxxx"


Trên macOS / Linux:

export OPENAI_API_KEY="sk-xxxx"

3.2 Chạy script

Ví dụ sinh thêm 1000 dòng dữ liệu:

python generate_data_hybrid.py --outfile data.csv --total 1000 --chunk 200


Giải thích:

--outfile: tên file CSV sẽ được tạo hoặc nối thêm

--total: tổng số dòng cần sinh thêm

--chunk: số dòng sinh ra trong mỗi lần gọi API

--temperature: độ sáng tạo của mô hình (mặc định 0.8)

Tất cả dữ liệu sinh mới sẽ được nối vào cuối file.

4. Định dạng dữ liệu đầu ra

File CSV không có header, mỗi dòng gồm:

"text",label


Ví dụ:

"Đăng ký gói V90B thế nào vậy?",Neutral
"Mạng yếu kinh khủng",Negative
"Gói ST70K dùng ổn nha",Positive

5. Ghi chú

Kích thước file lớn (ví dụ 10.000–50.000 dòng) có thể tiêu tốn khá nhiều token nếu dùng GPT-4o.

Nếu bộ dữ liệu quá lớn, nên chia thành nhiều lần sinh để tránh lỗi quota.

File CSV được lưu dạng UTF-8 có BOM để Excel đọc đúng tiếng Việt.

6. Thông tin thêm

Nếu bạn muốn mở rộng dữ liệu theo chủ đề viễn thông khác (thiết bị, eSIM, thanh toán hóa đơn), có thể chỉnh phần PROMPT_BASE để phù hợp hơn.
