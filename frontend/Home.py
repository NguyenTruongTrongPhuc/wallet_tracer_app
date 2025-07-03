import streamlit as st


# Client API để giao tiếp với backend
from api import client
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Wallet Tracer - Dotoshi",
    layout="wide",
    page_icon="🏠"
)

# --- LOGIC XỬ LÝ TOKEN KHI REDIRECT VỀ ---
# Khởi tạo session state nếu chưa có
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Kiểm tra xem có token trong URL không (sau khi Google redirect về)
token = st.query_params.get("token")
if token:
    # Trong ứng dụng thực tế, bạn nên gửi token này đến backend để xác thực
    # và lấy thông tin người dùng.
    # Ở đây, chúng ta giả định token hợp lệ và đánh dấu người dùng đã đăng nhập.
    st.session_state.logged_in = True
    st.session_state.user_token = token
    
    # Xóa token khỏi URL để giao diện sạch sẽ và bảo mật hơn
    st.query_params.clear()
    
    # Hiển thị thông báo chào mừng và tải lại trang để vào giao diện chính
    st.success("Đăng nhập thành công! Đang chuyển hướng...")
    time.sleep(2)
    st.rerun()


# --- CÁC HÀM GIAO DIỆN ---

def login_form():
    """Hiển thị form đăng nhập"""
    st.markdown("<h1 style='text-align: center;'>Chào mừng đến với Wallet Tracer</h1>", unsafe_allow_html=True)
    _ , col, _ = st.columns([1, 1.8, 1])
    with col:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #f06156;'>User Login</h4>", unsafe_allow_html=True)
            
            with st.form("login_form"):
                email = st.text_input("Email", label_visibility="collapsed", placeholder="Email")
                password = st.text_input("Mật khẩu", type="password", label_visibility="collapsed", placeholder="Mật khẩu")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.checkbox("Remember me")
                with col2:
                    st.markdown("<p style='text-align: right;'><a href='#'>Forgot password?</a></p>", unsafe_allow_html=True)

                submitted = st.form_submit_button("Đăng Nhập", use_container_width=True, type="primary")

                if submitted:
                    if email == "demo@dotoshi.com" and password == "Dotoshi@2025#":
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Email hoặc mật khẩu không chính xác!")

            st.markdown(
                """<p style='text-align: center; margin-top: 1rem;'>
                Don't have an account? <a href="?page=register" target="_self" style="color:#f06156; text-decoration:underline;">Register</a>
                </p>""",
                unsafe_allow_html=True
            )

def register_page():
    """Hiển thị trang đăng ký với các nút có icon."""
    
    # CSS tùy chỉnh cho các nút đăng ký
    st.markdown("""
    <style>
        .register-button {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem 1rem;
            border: 1px solid #4a4a4a;
            border-radius: 0.5rem;
            background-color: #262730;
            color: #FAFAFA;
            text-decoration: none;
            font-weight: bold;
            font-size: 1rem;
            margin-bottom: 0.75rem;
            transition: background-color 0.2s ease, border-color 0.2s ease;
        }
        .register-button:hover {
            background-color: #3a3b42;
            border-color: #f06156;
            color: #FAFAFA;
            text-decoration: none;
        }
        .register-button svg {
            margin-right: 0.75rem;
            height: 1.5em;
            width: 1.5em;
        }
        /* Thêm style cho nút bị vô hiệu hóa */
        .disabled-button {
            background-color: #383838;
            color: #888888;
            cursor: not-allowed;
            pointer-events: none;
            border-color: #4a4a4a;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>Tạo tài khoản</h1>", unsafe_allow_html=True)
    _ , col, _ = st.columns([1, 1.8, 1])
    with col:
        with st.container(border=True):
            st.info("Chọn một phương thức để đăng ký")

            # NÚT GOOGLE
            st.markdown(
                '''
                <a href="/api/v1/auth/login/google" target="_self" class="register-button">
                    <svg xmlns="http://www.w3.org/2000/svg" x="0px" y="0px" width="100" height="100" viewBox="0 0 48 48">
                        <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"></path><path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"></path><path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"></path><path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.574l6.19,5.238C39.904,36.46,44,30.836,44,24C44,22.659,43.862,21.35,43.611,20.083z"></path>
                    </svg>
                    Đăng ký bằng Google
                </a>
                ''',
                unsafe_allow_html=True
            )

            # NÚT GITHUB (CÓ ICON)
            st.markdown(
                '''
                <a href="/api/v1/auth/login/github" target="_self" class="register-button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12,2A10,10,0,0,0,2,12c0,4.42,2.87,8.17,6.84,9.5.5.09.68-.22.68-.48s0-.85,0-1.67c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.11-1.46-1.11-1.46-.91-.62.07-.6.07-.6,1,.07,1.53,1.03,1.53,1.03.9,1.53,2.36,1.09,2.94.83.09-.65.35-1.09.63-1.34-2.25-.26-4.6-1.12-4.6-5s1.71-3.64,3.19-4.92c-.32-.78-.44-1.68.08-3.14,0,0,.85-.27,2.79,1.02A9.5,9.5,0,0,1,12,6.5a9.5,9.5,0,0,1,2.56.34c1.94-1.29,2.79-1.02,2.79-1.02.52,1.46.4,2.36.08,3.14,1.48,1.28,3.19,2.62,3.19,4.92s-2.35,4.74-4.6,5c.36.31.68.92.68,1.85,0,1.34,0,2.42,0,2.75s.18.57.68.48A10,10,0,0,0,22,12C22,6.48,17.52,2,12,2Z"/>
                    </svg>
                    Đăng ký bằng Github
                </a>
                ''',
                unsafe_allow_html=True
            )
            
            # NÚT WEB3 (TẠM VÔ HIỆU HÓA)
            st.markdown(
                '''
                <a href="#" class="register-button disabled-button">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="m16.5 12-4.5-4.5m0 0L7.5 12m4.5-4.5v11.25m6-11.25L21 7.5m-4.5 4.5v11.25m0-11.25L21 12m-4.5-4.5-4.5 4.5m4.5-4.5-4.5-4.5m0 0L7.5 12m-3-4.5L12 3m0 0 4.5 4.5M12 3v11.25" />
                    </svg>
                    Đăng ký bằng Web3 (Sắp ra mắt)
                </a>
                ''',
                unsafe_allow_html=True
            )

            st.markdown("---") 
            if st.button("Quay lại Đăng nhập", use_container_width=True, type="primary"):
                st.query_params.clear()
                st.rerun()

def main_page():
    """Hiển thị nội dung chính sau khi đăng nhập"""
    st.title("✨ Wallet Tracer & Monitoring Suite")
    st.markdown("Một bộ công cụ phân tích và giám sát ví Bitcoin chuyên sâu, kết hợp giữa phân tích dữ liệu và trí tuệ nhân tạo.")
    st.info("👈 Chọn một công cụ từ thanh điều hướng bên trái để bắt đầu!", icon="ℹ️")
    st.markdown("---")
    st.header("🚀 Các Tính Năng Chính")
    st.markdown("""
    <style>
        .grid-container { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .grid-card { border: 1px solid #e1e4e8; border-radius: 10px; padding: 20px; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .grid-card h4 { margin-top: 0; margin-bottom: 10px; }
        .grid-card ul { padding-left: 20px; margin-bottom: 0; }
    </style>
    <div class="grid-container">
        <div class="grid-card">
            <h4>📊 Phân Tích Ví (Wallet Tracer)</h4>
            <ul>
                <li><strong>Phân tích Lịch sử:</strong> Xem toàn bộ lịch sử giao dịch, dòng tiền, và các chỉ số thống kê của một ví trong khoảng thời gian tùy chọn.</li>
                <li><strong>Phát hiện Cờ Đỏ:</strong> Tự động xác định các giao dịch rủi ro dựa trên các quy tắc Heuristics (giá trị lớn, peel chain, gom/phân tán coin...).</li>
            </ul>
        </div>
        <div class="grid-card">
            <h4>🤖 Báo cáo bằng AI (AI Report)</h4>
            <ul>
                <li><strong>Trợ lý ảo Chuyên nghiệp:</strong> Tích hợp GPT-4 để đọc toàn bộ dữ liệu phân tích và viết ra một bản báo cáo tình báo tài chính chuyên sâu.</li>
                <li><strong>Phân tích đa chiều:</strong> AI sẽ đánh giá từ tổng quan, hồ sơ ví, các mẫu giao dịch cho đến các rủi ro tiềm ẩn và đưa ra đề xuất hành động.</li>
            </ul>
        </div>
        <div class="grid-card">
            <h4>📡 Giám Sát Real-time (Monitoring)</h4>
            <ul>
                <li><strong>Theo dõi Đa ví:</strong> Thêm một danh sách các địa chỉ ví quan trọng để theo dõi mọi hoạt động của chúng trong thời gian thực.</li>
                <li><strong>Cảnh báo Tức thì:</strong> Hệ thống sử dụng các thuật toán nâng cao để phát hiện giao dịch bất thường và gửi cảnh báo ngay lập tức.</li>
            </ul>
        </div>
        <div class="grid-card">
            <h4>🌊 Luồng Giao dịch Blockchain</h4>
            <ul>
                <li><strong>Cảm nhận "Nhịp đập" Mạng lưới:</strong> Hiển thị luồng giao dịch chưa xác nhận của toàn bộ mạng Bitcoin, giúp nắm bắt bối cảnh và mức độ sôi động của thị trường.</li>
                <li><strong>Lọc Thông minh:</strong> Dễ dàng lọc để chỉ xem các giao dịch liên quan đến ví bạn đang theo dõi trong luồng giao dịch chung.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- BỘ ĐỊNH TUYẾN CHÍNH CỦA GIAO DIỆN ---
# Kiểm tra nếu người dùng đã đăng nhập thì hiển thị trang chính
if st.session_state.logged_in:
    main_page()
# Nếu chưa, kiểm tra URL để quyết định hiển thị trang đăng nhập hay đăng ký
else:
    if st.query_params.get("page") == "register":
        register_page()
    else:
        login_form()