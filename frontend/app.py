import streamlit as st

st.set_page_config(
    page_title="Crypto Tracing Home",
    page_icon="🏠",
    layout="wide"
)

st.title("Chào mừng đến với Công cụ Truy vết Ví Crypto")
st.markdown(
    """
    Đây là một ứng dụng mạnh mẽ được xây dựng để phân tích và truy vết các giao dịch
    trên blockchain Bitcoin.
    
    **👈 Hãy chọn trang `Wallet Tracer` từ thanh bên để bắt đầu!**

    ### Các tính năng chính:
    - **Truy vết giao dịch:** Xem chi tiết các giao dịch trong một khoảng thời gian nhất định.
    - **Trực quan hóa dòng tiền:** Sử dụng biểu đồ Sankey để hiểu rõ các giao dịch phức tạp.
    - **Phân cụm ví:** Tự động tìm các địa chỉ có khả năng thuộc cùng một chủ sở hữu.
    - **Phân tích bằng AI:** Nhận các nhận định chuyên sâu từ mô hình GPT-4.
    """
)
