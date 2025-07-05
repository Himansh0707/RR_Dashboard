import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Trade Log Analyzer + RR Tracker", layout="wide", page_icon="📊")
st.title("Trade Log Analyzer + RR Tracker")

uploaded_file = st.file_uploader("Upload your Trade Log CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Trade log loaded successfully!")

    # Required columns check
    required_cols = ["Symbol", "TF", "Type", "Direction", "TP Level Hit", "Max RR", "Risk Pips"]
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV must contain columns: {', '.join(required_cols)}")
    else:
        with st.sidebar:
            st.header("Filters")
            symbols = st.multiselect("Select Symbols", sorted(df['Symbol'].unique()), default=df['Symbol'].unique())
            tfs = st.multiselect("Select Timeframes", sorted(df['TF'].unique()), default=df['TF'].unique())
            types = st.multiselect("OB Type", sorted(df['Type'].unique()), default=df['Type'].unique())

        filtered_df = df[
            df['Symbol'].isin(symbols) &
            df['TF'].isin(tfs) &
            df['Type'].isin(types)
        ]

        st.markdown("### Filtered Trade Log")
        st.dataframe(filtered_df, use_container_width=True)

        # --- Key Metrics ---
        st.markdown("### 📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Trades", len(filtered_df))

        win_df = filtered_df[~filtered_df['TP Level Hit'].str.contains("SL")]
        win_rate = round(len(win_df) / len(filtered_df) * 100, 2) if len(filtered_df) > 0 else 0
        col2.metric("Win Rate", f"{win_rate}%")

        avg_rr = round(filtered_df['Max RR'].mean(), 2) if len(filtered_df) > 0 else 0
        col3.metric("Avg Max RR", avg_rr)

        avg_risk = round(filtered_df['Risk Pips'].mean(), 1) if len(filtered_df) > 0 else 0
        col4.metric("Avg Risk (pips)", avg_risk)

        # --- TP Hit Distribution ---
        st.markdown("### 🌐 TP Level Hit Distribution")
        tp_counts = filtered_df['TP Level Hit'].value_counts().reset_index()
        tp_counts.columns = ["TP Level", "Count"]
        tp_pie = px.pie(tp_counts, names='TP Level', values='Count', title="TP Level Ratio")
        st.plotly_chart(tp_pie, use_container_width=True)

        # --- High Probability OBs Performance ---
        st.markdown("### 🔄 High-Probability OB Performance")
        high_prob_df = filtered_df[filtered_df['Type'].str.contains("Strong")]
        strong_win_rate = 0
        if len(high_prob_df) > 0:
            strong_win_df = high_prob_df[~high_prob_df['TP Level Hit'].str.contains("SL")]
            strong_win_rate = round(len(strong_win_df) / len(high_prob_df) * 100, 2)

        col5, col6 = st.columns(2)
        col5.metric("Strong OB Trades", len(high_prob_df))
        col6.metric("Strong OB Win Rate", f"{strong_win_rate}%")

        # --- Download Filtered Results ---
        st.markdown("### 📂 Download Filtered Results")
        st.download_button("Download CSV", data=filtered_df.to_csv(index=False), file_name="filtered_trade_log.csv", mime="text/csv")
else:
    st.info("Please upload a Trade Log CSV file.")
