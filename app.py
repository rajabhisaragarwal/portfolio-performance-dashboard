import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import plotly.graph_objects as go

st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Portfolio Performance Dashboard")
st.markdown("Analyze any portfolio of stocks & ETFs with institutional-grade metrics.")
st.markdown("📊 Cumulative Returns &nbsp;·&nbsp; 📉 Max Drawdown &nbsp;·&nbsp; ⚡ Sharpe Ratio &nbsp;·&nbsp; 🌊 Volatility &nbsp;·&nbsp; 🔥 Correlation Heatmap")
st.divider()

st.subheader("⚙️ Configure Your Portfolio")

tickers_input = st.text_input(
    "Tickers",
    placeholder="Enter tickers separated by commas (e.g. AAPL, MSFT, GOOGL, JPM)"
)
tickers = [t.strip().upper() for t in tickers_input.split(',')]

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=pd.Timestamp('2020-01-01'))
with col2:
    end_date = st.date_input("End Date", value=pd.Timestamp('2025-12-31'))

weights_input = st.text_input(
    "Portfolio Weights",
    placeholder="Enter weights as percentages matching ticker order (e.g. 25, 25, 25, 25)"
)

weights_pct = [float(w.strip()) for w in weights_input.split(',') if w.strip()]

col3, col4 = st.columns(2)
with col3:
    benchmark_choice = st.selectbox("Benchmark", [
        'SPY — S&P 500',
        'QQQ — Nasdaq-100',
        'IWM — Russell 2000',
        'VTI — Total US Market',
        'IWD — Russell 1000 Value',
        'IWF — Russell 1000 Growth',
        'Other (enter manually)'
    ])
    if benchmark_choice == 'Other (enter manually)':
        benchmark = st.text_input("Enter benchmark ticker", placeholder="e.g. IWV, SPYG").strip().upper()
    else:
        benchmark = benchmark_choice.split(' — ')[0]
with col4:
    risk_free = st.number_input("Risk-Free Rate (%)", min_value=0.0, max_value=15.0, value=4.5, step=0.05) / 100

st.divider()

if st.button("🚀 Run Analysis"):
    if not tickers_input.strip():
        st.error("⚠️ Please enter at least one ticker.")
        st.stop()
    if not weights_input.strip():
        st.error("⚠️ Please enter portfolio weights.")
        st.stop()
    if round(sum(weights_pct), 2) != 100.0:
        st.error(f"⚠️ Weights sum to {sum(weights_pct)}%. Must equal 100%.")
        st.stop()
    if benchmark_choice == 'Other (enter manually)' and not benchmark:
        st.error("⚠️ Please enter a custom benchmark ticker.")
        st.stop()

    weights = [w / 100 for w in weights_pct]
    all_tickers = list(dict.fromkeys(tickers + [benchmark]))

    with st.spinner('⏳ Fetching market data...'):
        import time
        time.sleep(2)
        prices = yf.download(all_tickers, start=start_date, end=end_date, auto_adjust=False)['Adj Close']

    st.success("✅ Analysis complete!")

    returns = prices.pct_change().dropna()

    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max

    portfolio_returns = returns[tickers].dot(weights)
    portfolio_cumulative = (1 + portfolio_returns).cumprod()
    benchmark_cumulative = cumulative[benchmark]
    portfolio_drawdown_series = (portfolio_cumulative - portfolio_cumulative.cummax()) / portfolio_cumulative.cummax()

    total_return = (1 + returns).prod() - 1
    volatility = returns.std() * np.sqrt(252)
    sharpe = (returns.mean() * 252 - risk_free) / volatility
    max_drawdown = drawdown.min()
    
    summary = pd.DataFrame({
        'Total Return': total_return.round(4),
        'Volatility': volatility.round(4),
        'Sharpe Ratio': sharpe.round(4),
        'Max Drawdown': max_drawdown.round(4)
    })

    portfolio_row = pd.DataFrame({
        'Total Return': [round((1 + portfolio_returns).prod() - 1, 4)],
        'Volatility': [round(portfolio_returns.std() * np.sqrt(252), 4)],
        'Sharpe Ratio': [round((portfolio_returns.mean() * 252 - risk_free) / (portfolio_returns.std() * np.sqrt(252)), 4)],
        'Max Drawdown': [round(portfolio_drawdown_series.min(), 4)]
    }, index=['My Portfolio'])
    
    summary_full = pd.concat([summary, portfolio_row])
    
    st.subheader("Portfolio Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Return", f"{round(portfolio_row['Total Return'].values[0] * 100, 2)}%")
    with col2:
        st.metric("Volatility", f"{round(portfolio_row['Volatility'].values[0] * 100, 2)}%")
    with col3:
        st.metric("Sharpe Ratio", f"{round(portfolio_row['Sharpe Ratio'].values[0], 2)}")
    with col4:
        st.metric("Max Drawdown", f"{round(portfolio_row['Max Drawdown'].values[0] * 100, 2)}%")
    
    st.divider()
    
    st.subheader("Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Cumulative Returns", "Drawdown", "Summary Metrics", "Correlation Heatmap"])
    
    with tab1:
        colormap = plt.colormaps['tab20'].resampled(len(tickers))
        holding_colors = [colormap(i) for i in range(len(tickers))]
    
        fig, ax = plt.subplots(figsize=(14, 6))
        for i, ticker in enumerate(tickers):
            ax.plot(cumulative.index, cumulative[ticker],
                    color=holding_colors[i], linewidth=1.5, alpha=0.75, label=ticker)
        ax.plot(cumulative.index, benchmark_cumulative,
                color='#D85A30', linewidth=2.5, label=f'Benchmark ({benchmark})')
        ax.plot(cumulative.index, portfolio_cumulative,
                color='#1D9E75', linewidth=3.5, label='My Portfolio')
        ax.set_title('Cumulative Returns')
        ax.set_ylabel('Growth of $1')
        ax.axhline(y=1, color='#2C2C2A', linestyle='--', linewidth=0.8)
        ax.legend(loc='upper left', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab2:
        fig, ax = plt.subplots(figsize=(14, 6))
        drawdown.plot(ax=ax, linewidth=1.2, alpha=0.75)
        portfolio_drawdown_series.plot(ax=ax, color='#1D9E75', linewidth=3, label='My Portfolio')
        ax.set_title('Drawdown from Peak')
        ax.set_ylabel('Drawdown')
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))
        ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8)
        ax.legend(loc='lower left', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab3:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        metrics = ['Total Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown']
        for i, metric in enumerate(metrics):
            ax = axes[i // 2, i % 2]
            summary_full[metric].plot(kind='bar', ax=ax,
                                       color=['#1D9E75' if x == 'My Portfolio'
                                              else '#D85A30' if x == benchmark
                                              else '#378ADD' for x in summary_full.index],
                                       edgecolor='white')
            ax.set_title(metric)
            ax.set_xlabel('')
            ax.tick_params(axis='x', rotation=45)
            ax.axhline(y=0, color='black', linewidth=0.8)
        plt.suptitle('Portfolio Summary Metrics', fontsize=16, fontweight='bold', y=1.01)
        plt.tight_layout()
        st.pyplot(fig)
    
    with tab4:
        correlation = returns[tickers].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(correlation, cmap='RdYlGn', vmin=-1, vmax=1)
        ax.set_xticks(range(len(tickers)))
        ax.set_yticks(range(len(tickers)))
        ax.set_xticklabels(tickers, rotation=45, ha='right')
        ax.set_yticklabels(tickers)
        for i in range(len(tickers)):
            for j in range(len(tickers)):
                ax.text(j, i, round(correlation.iloc[i, j], 2),
                        ha='center', va='center', fontsize=9)
        plt.colorbar(im, ax=ax)
        ax.set_title('Correlation Heatmap')
        plt.tight_layout()
        st.pyplot(fig)
    
    st.divider()
    st.caption("Data sourced from Yahoo Finance via yfinance | Built with Python & Streamlit")
