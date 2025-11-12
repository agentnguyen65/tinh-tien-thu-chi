import streamlit as st
import pandas as pd

# --- API Logic từ Bước 2 (Giả lập hàm xử lý logic) ---
# Lưu ý: Trong một ứng dụng thực tế, 'current_state' sẽ được quản lý bằng st.session_state
def initialize_state():
    """Khởi tạo trạng thái phiên (session state) ban đầu."""
    if 'state' not in st.session_state:
        st.session_state['state'] = {
            'initial_capital': None,
            'current_capital': 0,
            'total_income': 0,
            'total_expense': 0,
            'transactions': []
        }

def generate_finance_report(input_data):
    """Bao bọc logic SPG và cập nhật trạng thái."""
    state = st.session_state['state']
    
    # 1. Xử lý Tổng Vốn Ban Đầu
    capital_input = input_data.get('capital_input')
    if state['initial_capital'] is None and capital_input is not None and capital_input > 0:
        state['initial_capital'] = capital_input
        state['current_capital'] = capital_input
        state['transactions'].append({
            'type': 'Thu vào', 
            'value': capital_input, 
            'description': 'Vốn Ban Đầu'
        })
        return
        
    # 2. Xử lý Giao Dịch (nếu Vốn Ban Đầu đã được nhập)
    if state['initial_capital'] is not None:
        transaction_type = input_data.get('type')
        transaction_value = input_data.get('value', 0)
        transaction_description = input_data.get('description', '')

        if transaction_type and transaction_value > 0:
            state['transactions'].append({
                'type': transaction_type, 
                'value': transaction_value, 
                'description': transaction_description
            })

            # Thực hiện Logic Tính Toán
            if transaction_type == 'Thu vào':
                state['current_capital'] += transaction_value
                state['total_income'] += transaction_value
            elif transaction_type == 'Chi ra':
                state['current_capital'] -= transaction_value
                state['total_expense'] += transaction_value
    
# --- Thiết Kế UI Streamlit ---

initialize_state()
st.title("💰 Ứng Dụng Web: Bảng Tính Tiền Thu Chi")
st.markdown("---")

# --- KHU VỰC NHẬP LIỆU (INPUT_SCHEMA) ---

with st.sidebar:
    st.header("Nhập Liệu Giao Dịch")
    
    # 1. Nhập Vốn Ban Đầu (Chỉ hiện khi chưa nhập)
    if st.session_state['state']['initial_capital'] is None:
        st.subheader("Bước 1: Thiết Lập Vốn")
        initial_cap = st.number_input(
            "1. Tổng Vốn Ban Đầu (Khóa sau khi nhập):", 
            min_value=0, 
            step=1000, 
            key="vốn_ban_đầu"
        )
        if st.button("Lập Bảng & Thiết Lập Vốn", key="btn_vốn"):
            generate_finance_report({'capital_input': initial_cap})
            st.success("Đã thiết lập vốn! Hãy nhập giao dịch.")
            st.rerun() # Tải lại để ẩn ô vốn

    # 2. Nhập Giao Dịch (Chỉ hiện khi đã có vốn)
    if st.session_state['state']['initial_capital'] is not None:
        st.subheader("Bước 2: Giao Dịch Hàng Ngày")
        
        # 2.1 Loại Giao Dịch
        transaction_type = st.radio(
            "2. Loại Giao Dịch:",
            ('Thu vào', 'Chi ra')
        )
        # 2.2 Giá Trị Giao Dịch
        transaction_value = st.number_input(
            "3. Giá Trị (Số tiền):", 
            min_value=1, 
            step=1000, 
            key="giá_trị"
        )
        # 2.3 Mô Tả Giao Dịch
        transaction_desc = st.text_input(
            "4. Mô Tả Giao Dịch:", 
            key="mô_tả"
        )
        
        # Nút "Tạo kết quả" (Thực hiện giao dịch)
        if st.button("Thực Hiện Giao Dịch", key="btn_giao_dịch"):
            if transaction_value > 0 and transaction_desc:
                input_data = {
                    'type': transaction_type,
                    'value': transaction_value,
                    'description': transaction_desc
                }
                generate_finance_report(input_data)
                st.success(f"Đã ghi nhận giao dịch: {transaction_type} {transaction_value} VNĐ")
                st.rerun() # Tải lại để cập nhật kết quả

# --- KHU VỰC HIỂN THỊ KẾT QUẢ (OUTPUT_SCHEMA) ---

state = st.session_state['state']

if state['initial_capital'] is None:
    st.info("Vui lòng nhập **Tổng Vốn Ban Đầu** ở thanh bên (Sidebar) để bắt đầu.")
else:
    st.header("📊 Bảng Hoàn Tính Hoàn Chỉnh")
    
    col1, col2, col3 = st.columns(3)
    
    # Tổng Vốn Hiện Tại
    col1.metric("Tổng Vốn Hiện Tại", f"{state['current_capital']:,} VNĐ")
    
    # Tổng Thu Cộng Dồn
    col2.metric("Tổng Thu Cộng Dồn", f"{state['total_income']:,} VNĐ")

    # Tổng Chi Cộng Dồn
    col3.metric("Tổng Chi Cộng Dồn", f"{state['total_expense']:,} VNĐ")

    st.markdown("---")
    st.subheader("📜 Bảng Lịch Sử Thu/Chi Chi Tiết")
    
    # Bảng Lịch sử Thu/Chi chi tiết
    if state['transactions']:
        df = pd.DataFrame(state['transactions'])
        # Đảo ngược thứ tự để giao dịch mới nhất hiện lên đầu
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    else:
        st.warning("Chưa có giao dịch nào được ghi nhận.")


# Giao diện luôn gồm: Ô nhập thông tin (sidebar), Nút “Tạo kết quả”, Khung hiển thị kết quả.
