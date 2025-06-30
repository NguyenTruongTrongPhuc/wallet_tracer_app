# 🕵️‍♂️ Wallet Tracer & Monitoring Suite

**Wallet Tracer & Monitoring Suite** là một bộ công cụ phân tích và giám sát ví Bitcoin chuyên sâu, được xây dựng bằng Python. Ứng dụng kết hợp giữa phân tích dữ liệu on-chain, các thuật toán Heuristics để phát hiện rủi ro, và sức mạnh của Trí tuệ Nhân tạo (GPT-4) để cung cấp các báo cáo tình báo tài chính chi tiết.

---

## 🚀 Các Tính Năng Chính

Ứng dụng được chia thành hai công cụ chính, mỗi công cụ có những tính năng mạnh mẽ riêng:

### 1. 📊 Wallet Tracer (Phân Tích Chi Tiết)
- **Phân tích Lịch sử Giao dịch:** Xem toàn bộ lịch sử giao dịch của một địa chỉ ví trong một khoảng thời gian tùy chọn.
- **Thống kê Toàn diện:** Cung cấp các chỉ số quan trọng như tổng nhận, tổng gửi, số dư hiện tại, và tổng số giao dịch.
- **Phát hiện Cờ Đỏ (Red Flags):** Tự động xác định và cảnh báo các giao dịch có dấu hiệu rủi ro dựa trên các quy tắc Heuristics đã được nghiên cứu:
  - Giao dịch giá trị lớn.
  - Chuỗi lột vỏ (Peeling Chain).
  - Giao dịch gom/phân tán coin (Consolidation/Distribution).
  - Giao dịch có cấu trúc phức tạp (Nhiều vào/Nhiều ra).
- **Trực quan hóa Dữ liệu:** Hiển thị biểu đồ khối lượng và tần suất giao dịch, cùng sơ đồ dòng tiền (Sankey) chi tiết cho từng giao dịch.
- **Báo cáo bằng AI:** Tích hợp GPT-4 để đọc toàn bộ dữ liệu phân tích và tự động viết ra một bản báo cáo tình báo tài chính chuyên sâu, dễ hiểu.

### 2. 📡 Dashboard Giám Sát (Monitoring)
- **Giám sát Real-time:** Theo dõi nhiều ví Bitcoin cùng lúc và nhận thông báo tức thì cho các giao dịch mới liên quan.
- **Hệ thống Cảnh báo Thông minh:** Sử dụng các thuật toán nâng cao để phân tích các giao dịch mới trong thời gian thực và gửi cảnh báo nếu phát hiện hành vi bất thường.
- **Luồng Giao dịch Blockchain:** Hiển thị luồng giao dịch chưa xác nhận của toàn bộ mạng Bitcoin, giúp nắm bắt "nhịp đập" và bối cảnh của thị trường.
- **Phân tích Định kỳ bằng AI (Polling):** Tự động chạy một phân tích nhanh bằng AI cho các ví được chọn sau mỗi 5 phút để đưa ra các nhận định cập nhật.

---

## 🛠️ Công nghệ sử dụng

- **Backend:** Python, FastAPI, Uvicorn, Gunicorn, Pydantic.
- **Frontend:** Python, Streamlit, Pandas, Plotly, Requests.
- **Triển khai:** Docker, Docker Compose, Nginx (Reverse Proxy).
- **APIs:** Mempool.space, Blockchain.com (WebSocket), OpenAI.

---

## 🏃 Hướng dẫn Cài đặt & Khởi chạy bằng Docker

Cách dễ nhất và ổn định nhất để chạy ứng dụng này là sử dụng Docker.

### Yêu cầu
- [Docker](https://www.docker.com/products/docker-desktop/) đã được cài đặt trên máy của bạn.
- [Docker Compose](https://docs.docker.com/compose/install/) (thường đi kèm với Docker Desktop).

### Các bước cài đặt

**1. Sao chép (Clone) Repository:**
Mở terminal và chạy lệnh sau:
```bash
git clone [https://github.com/NguyenTruongTrongPhuc/wallet_tracer_app](https://github.com/NguyenTruongTrongPhuc/wallet_tracer_app)
cd your-repository-name

2. Tạo file Biến Môi trường (.env):
Đây là bước quan trọng nhất để cung cấp API key cho ứng dụng.

Ở thư mục gốc của dự án, hãy tạo một file mới và đặt tên là .env.

Mở file .env và thêm vào nội dung sau, thay thế sk-your-key bằng API key của bạn từ OpenAI:

OPENAI_API_KEY=sk-your-key-goes-here
CLIENT_ID=your-key-goes-here
CLIENT_SECRET=your-key-goes-here

Lưu ý: File .env đã được thêm vào .gitignore để đảm bảo bạn không vô tình đưa API key của mình lên GitHub.

3. Xây dựng (Build) và Chạy (Run) với Docker Compose:
Mở terminal ở thư mục gốc của dự án và chạy lệnh duy nhất sau:

docker compose up --build

Lệnh này sẽ tự động:

Xây dựng các "ảnh" (images) cho backend và frontend dựa trên Dockerfile tương ứng.

Tải về ảnh của Nginx.

Khởi chạy cả 3 container (backend, frontend, nginx) và kết nối chúng lại với nhau.

Quá trình build lần đầu có thể mất vài phút.

4. Truy cập Ứng dụng:
Sau khi các container đã khởi động thành công, bạn hãy mở trình duyệt và truy cập vào địa chỉ:
http://localhost

Nginx sẽ tự động điều hướng bạn đến giao diện của Streamlit.

Thông tin đăng nhập mặc định:

Email: demo@dotoshi.com

Mật khẩu: Dotoshi@2025#

5. Dừng Ứng dụng:
Để dừng tất cả các container, quay lại cửa sổ terminal đang chạy docker-compose và bấm Ctrl + C.

📁 Cấu trúc Dự án
.
├── backend/        
├── frontend/       
├── nginx/          
├── .env            
└── docker-compose.yml 
