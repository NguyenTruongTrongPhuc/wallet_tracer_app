import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

def render_volume_chart(transactions: List[Dict[str, Any]], chart_type: str = 'Cột'):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: render_volume_chart                                 ##
    ##                                                                ##
    ##  - Purpose: To render a chart visualizing the daily            ##
    ##    transaction volume (in BTC). It can display the data as     ##
    ##    either a bar chart or a line chart based on user selection. ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - transactions (List[dict]): A list of transaction dicts    ##
    ##      filtered for the selected date range.                     ##
    ##    - chart_type (str): A string, either 'Cột' (Bar) or 'Đường' ##
    ##      (Line), to determine the chart type.                      ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Converts the list of transactions into a pandas DataFrame##
    ##    2. Groups the data by date and calculates the sum of        ##
    ##       `total_value` for each day.                              ##
    ##    3. Creates a Plotly Express bar or line chart based on the  ##
    ##       `chart_type` parameter.                                  ##
    ##    4. Applies custom styling for colors, layout, and hover     ##
    ##       information.                                             ##
    ##                                                                ##
    ##  - Output: Renders a Plotly chart directly into the Streamlit  ##
    ##    app using `st.plotly_chart`.                                ##
    ##                                                                ##
    ####################################################################
    st.subheader("📈 Khối Lượng Giao Dịch Hàng Ngày (BTC)")
    if not transactions:
        st.info("Không có dữ liệu để hiển thị.")
        return

    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['block_time_iso']).dt.date

    daily_volume = df.groupby('date')['total_value'].sum().reset_index()
    daily_volume['total_value_btc'] = daily_volume['total_value'] / 1e8

    if chart_type == 'Cột':
        fig = px.bar(
            daily_volume, x='date', y='total_value_btc',
            labels={'date': 'Ngày', 'total_value_btc': 'Khối lượng (BTC)'},
            color='total_value_btc',
            color_continuous_scale=px.colors.sequential.Blues_r,
            template="plotly_white"
        )
    else: 
        fig = px.line(
            daily_volume, x='date', y='total_value_btc',
            labels={'date': 'Ngày', 'total_value_btc': 'Khối lượng (BTC)'},
            template="plotly_white", markers=True
        )
        fig.update_traces(line_color='#007bff')
        
    fig.update_layout(
        title_text="Tổng giá trị giao dịch theo ngày",
        title_x=0.5,
        hovermode="x unified",
        plot_bgcolor='rgba(240, 242, 246, 0.95)',
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)

def render_frequency_chart(transactions: List[Dict[str, Any]], chart_type: str = 'Cột'):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: render_frequency_chart                              ##
    ##                                                                ##
    ##  - Purpose: To render a chart visualizing the daily            ##
    ##    transaction frequency (the count of transactions per day).  ##
    ##    Supports both bar and area chart types.                     ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - transactions (List[dict]): A list of transaction dicts.   ##
    ##    - chart_type (str): A string, either 'Cột' (Bar) or 'Đường' ##
    ##      (Area/Line), to determine the chart type.                 ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Converts the list of transactions into a pandas DataFrame##
    ##    2. Groups the data by date and calculates the number of     ##
    ##       transactions for each day using `.size()`.               ##
    ##    3. Creates a Plotly Express bar or area chart.              ##
    ##    4. Applies custom styling, including a fill color for the   ##
    ##       area chart to improve visual appeal.                     ##
    ##                                                                ##
    ##  - Output: Renders a Plotly chart directly into the Streamlit  ##
    ##    app.                                                        ##
    ##                                                                ##
    ####################################################################
    st.subheader("📊 Tần Suất Giao Dịch Hàng Ngày")
    if not transactions:
        st.info("Không có dữ liệu để hiển thị.")
        return

    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['block_time_iso']).dt.date

    tx_counts = df.groupby('date').size().reset_index(name='count')
    tx_counts = tx_counts.sort_values('date')

    if chart_type == 'Cột':
        fig = px.bar(
            tx_counts, x='date', y='count',
            labels={'date': 'Ngày', 'count': 'Số giao dịch'},
            color='count',
            color_continuous_scale=px.colors.sequential.Reds_r,
            template="plotly_white"
        )
        fig.update_layout(coloraxis_showscale=False)
    else: 
        fig = px.area(
            tx_counts, x='date', y='count',
            labels={'date': 'Ngày', 'count': 'Số giao dịch'},
            template="plotly_white", markers=True
        )
        fig.update_traces(line_color='#ef4444', fillcolor='rgba(239, 68, 68, 0.2)')
        
    fig.update_layout(
        title_text='Số lượng giao dịch mỗi ngày',
        title_x=0.5,
        hovermode="x unified",
        plot_bgcolor='rgba(240, 242, 246, 0.95)'
    )
    st.plotly_chart(fig, use_container_width=True)


def render_sankey_for_transaction(tx: Dict[str, Any], main_address: str):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: render_sankey_for_transaction                       ##
    ##                                                                ##
    ##  - Purpose: To create a detailed Sankey diagram that           ##
    ##    visualizes the flow of funds for a single, specific         ##
    ##    transaction. It clearly shows inputs, outputs, and fees.    ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - tx (dict): A dictionary representing one transaction.     ##
    ##    - main_address (str): The primary wallet address being      ##
    ##      traced, which will be highlighted in the diagram.         ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Initializes data structures for the Sankey diagram       ##
    ##       (nodes, links, colors).                                  ##
    ##    2. Creates a central node for the transaction itself.       ##
    ##    3. Iterates through the transaction's inputs (`vin`) to     ##
    ##       create source nodes, linking them to the central node.   ##
    ##    4. Iterates through the outputs (`vout`) to create target   ##
    ##       nodes, linking them from the central node.               ##
    ##    5. Highlights any input or output node that matches the     ##
    ##       `main_address` with a distinct color.                    ##
    ##    6. Creates a separate node for the transaction fee.         ##
    ##    7. Constructs the `go.Sankey` figure using the prepared data##
    ##                                                                ##
    ##  - Output: Renders a detailed Plotly Sankey diagram in the     ##
    ##    Streamlit app.                                              ##
    ##                                                                ##
    ####################################################################
    labels, node_colors, source_indices, target_indices, values, node_map = [], [], [], [], [], {}

    def add_node(label, color):
        if label not in node_map:
            node_map[label] = len(labels)
            labels.append(label)
            node_colors.append(color)
        return node_map[label]

    tx_id_short = f"Giao dịch: {tx['txid'][:8]}..."
    tx_node_idx = add_node(tx_id_short, 'rgba(147, 112, 219, 0.8)')

    for vin in tx.get('vin', []):
        if vin.get('prevout'):
            addr = vin['prevout'].get('scriptpubkey_address')
            if addr is None: addr = "Không xác định (Coinbase)"
            val_sats = vin['prevout'].get('value', 0)
            addr_label = f"IN: {addr[:8]}..." if len(addr) > 16 else f"IN: {addr}"
            color = 'rgba(255, 99, 71, 0.8)'
            if addr == main_address:
                addr_label = f"IN: {main_address[:8]}... (VÍ CHÍNH)"
                color = 'rgba(255, 69, 0, 0.9)'
            source_idx = add_node(addr_label, color)
            source_indices.append(source_idx)
            target_indices.append(tx_node_idx)
            values.append(val_sats / 1e8)

    for vout in tx.get('vout', []):
        addr = vout.get('scriptpubkey_address')
        if addr is None: addr = "Không xác định (OP_RETURN)"
        val_sats = vout.get('value', 0)
        addr_label = f"OUT: {addr[:8]}..." if len(addr) > 16 else f"OUT: {addr}"
        color = 'rgba(60, 179, 113, 0.8)'
        if addr == main_address:
            addr_label = f"OUT: {main_address[:8]}... (VÍ CHÍNH)"
            color = 'rgba(34, 139, 34, 0.9)'
        target_idx = add_node(addr_label, color)
        source_indices.append(tx_node_idx)
        target_indices.append(target_idx)
        values.append(val_sats / 1e8)

    fee = tx.get('fee', 0)
    if fee > 0:
        fee_node_idx = add_node("Phí Giao Dịch", 'rgba(128, 128, 128, 0.8)')
        source_indices.append(tx_node_idx)
        target_indices.append(fee_node_idx)
        values.append(fee / 1e8)

    fig = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels, color=node_colors),
        link=dict(source=source_indices, target=target_indices, value=values, hovertemplate='Dòng tiền: %{value:.8f} BTC<extra></extra>')
    )])
    fig.update_layout(title_text="Sơ Đồ Dòng Tiền (BTC)", font_size=12)
    st.plotly_chart(fig, use_container_width=True)