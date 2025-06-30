import streamlit as st

st.set_page_config(
    page_title="Wallet Tracer - Đăng Nhập",
    layout="wide",
    page_icon="🏠"
)

def login_form():
    st.markdown("<h1 style='text-align: center;'>Chào mừng đến với Wallet Tracer</h1>", unsafe_allow_html=True)
    _ , col, _ = st.columns([1, 1.8, 1])
    with col:
        with st.container(border=True):
            st.markdown("<h4 style='text-align: center; color: #f06156;'>User Login</h4>", unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("Email", label_visibility="collapsed", placeholder="Email")
                password = st.text_input("Mật khẩu", type="password", label_visibility="collapsed", placeholder="Mật khẩu")
                
                submitted = st.form_submit_button("Đăng Nhập", use_container_width=True, type="primary")

                if submitted:
                    if email == "demo@dotoshi.com" and password == "Dotoshi@2025#":
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Email hoặc mật khẩu không chính xác!")

def main_page():
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

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    login_form()
else:
    main_page()