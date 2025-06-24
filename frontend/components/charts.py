import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_frequency_chart(df: pd.DataFrame):
    """Tạo biểu đồ cột thể hiện tần suất giao dịch."""
    st.subheader("📊 Tần suất giao dịch")
    df['date'] = df['time'].dt.date
    tx_counts = df.groupby('date').size().reset_index(name='count')
    tx_counts = tx_counts.sort_values('date')
    
    fig = px.bar(
        tx_counts, 
        x='date', 
        y='count', 
        title='Số lượng giao dịch mỗi ngày',
        labels={'date': 'Ngày', 'count': 'Số giao dịch'},
        template="streamlit"
    )
    fig.update_layout(bargap=0.2)
    st.plotly_chart(fig, use_container_width=True)

def create_sankey_chart_for_tx(tx: dict):
    """Tạo biểu đồ Sankey trực quan hóa dòng tiền cho MỘT giao dịch."""
    
    sources = []
    targets = []
    values = []
    labels = []
    
    node_map = {}

    def get_node_id(label):
        if label not in node_map:
            node_map[label] = len(labels)
            labels.append(label)
        return node_map[label]

    # Process inputs (vin)
    total_input_value = 0
    for vin in tx['vin']:
        if vin.get('prevout'):
            addr = vin['prevout']['scriptpubkey_address'] or "Unknown Input"
            val = vin['prevout']['value']
            source_id = get_node_id(addr)
            target_id = get_node_id(f"Transaction: {tx['txid'][:10]}...")
            sources.append(source_id)
            targets.append(target_id)
            values.append(val)
            total_input_value += val
    
    # Process outputs (vout)
    for vout in tx['vout']:
        addr = vout['scriptpubkey_address'] or "Unknown Output"
        val = vout['value']
        source_id = get_node_id(f"Transaction: {tx['txid'][:10]}...")
        target_id = get_node_id(addr)
        sources.append(source_id)
        targets.append(target_id)
        values.append(val)

    # Add fee as an output
    fee = tx.get('fee', 0)
    if fee > 0:
        source_id = get_node_id(f"Transaction: {tx['txid'][:10]}...")
        target_id = get_node_id("Transaction Fee")
        sources.append(source_id)
        targets.append(target_id)
        values.append(fee)


    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values
        ))])

    fig.update_layout(title_text=f"Sơ đồ dòng tiền cho giao dịch {tx['txid']}", font_size=10)
    st.plotly_chart(fig, use_container_width=True)
