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
st.markdown("Important: This tool supports either US stocks/ETFs or Indian stocks/ETFs (NSE/BSE) in a single run. Do not mix both — currency differences (USD vs INR) will produce misleading results.")
st.markdown("Indian stocks: append .NS (NSE) or .BO (BSE) — e.g. RELIANCE.NS, HDFCBANK.NS")
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
        '^NSEI — NIFTY 50',
        '^BSESN — BSE SENSEX',
        'NIFTYMIDCAP150.NS — NIFTY Midcap 150',
        'NIFTYSMLCAP250.NS — NIFTY Smallcap 250',
        '^CRSLDX — NIFTY 500',
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
    
    invalid_tickers = [t for t in all_tickers if t in prices.columns and prices[t].isna().all()]
    missing_tickers = [t for t in all_tickers if t not in prices.columns]
    bad_tickers = invalid_tickers + missing_tickers
    
    if bad_tickers:
        st.error(f"⚠️ The following tickers could not be found: {', '.join(bad_tickers)}. Please check and try again.")
        st.stop()
    
    if prices.empty:
        st.error("⚠️ No data returned. Please check your tickers and date range.")
        st.stop()
    
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
    
    st.subheader("📈 Cumulative Returns")

    colormap = plt.colormaps['tab20'].resampled(len(tickers))
    holding_colors = [colormap(i) for i in range(len(tickers))]
    
    fig1 = go.Figure()
    
    for i, ticker in enumerate(tickers):
        r, g, b, _ = holding_colors[i]
        color = f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'
        fig1.add_trace(go.Scatter(
            x=cumulative.index,
            y=cumulative[ticker],
            name=ticker,
            line=dict(color=color, width=1.5),
            opacity=0.75
        ))

    fig1.add_trace(go.Scatter(
        x=cumulative.index,
        y=benchmark_cumulative,
        name=f'Benchmark ({benchmark})',
        line=dict(color='#D85A30', width=2.5)
    ))
    
    fig1.add_trace(go.Scatter(
        x=cumulative.index,
        y=portfolio_cumulative,
        name='My Portfolio',
        line=dict(color='#1D9E75', width=4)
    ))
    
    fig1.update_layout(
        title='Portfolio vs Benchmark — Cumulative Returns',
        yaxis_title='Growth of $1',
        xaxis_title='Date',
        hovermode='x unified',
        height=500,
        dragmode=False,
    xaxis=dict(fixedrange=True),
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    st.divider()
    
    st.subheader("📉 Drawdown from Peak")

    fig2 = go.Figure()
    
    for i, ticker in enumerate(tickers):
        r, g, b, _ = holding_colors[i]
        color = f'rgb({int(r*255)},{int(g*255)},{int(b*255)})'
        fig2.add_trace(go.Scatter(
            x=drawdown.index,
            y=drawdown[ticker],
            name=ticker,
            line=dict(color=color, width=1.5),
            opacity=0.75
        ))
    
    fig2.add_trace(go.Scatter(
        x=portfolio_drawdown_series.index,
        y=portfolio_drawdown_series,
        name='My Portfolio',
        line=dict(color='#1D9E75', width=4)
    ))
    
    fig2.update_layout(
        title='Drawdown from Peak',
        yaxis_title='Drawdown',
        xaxis_title='Date',
        yaxis_tickformat='.0%',
        hovermode='x unified',
        height=500,
        dragmode=False,
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    st.divider()
    
    st.subheader("📊 Summary Metrics")

    colors_bar = [
        '#1D9E75' if x == 'My Portfolio'
        else '#D85A30' if x == benchmark
        else '#378ADD'
        for x in summary_full.index
    ]
    
    metrics = ['Total Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown']
    
    for metric in metrics:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=summary_full.index.tolist(),
            y=summary_full[metric].tolist(),
            marker_color=colors_bar,
            text=[f'{v:.2%}' if metric != 'Sharpe Ratio' else f'{v:.2f}'
                  for v in summary_full[metric]],
            textposition='outside'
        ))
        fig.update_layout(
            title=metric,
            height=350,
            dragmode=False,
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    st.subheader("🔥 Correlation Heatmap")

    correlation = returns[tickers].corr()
    
    fig4 = go.Figure(data=go.Heatmap(
        z=correlation.values,
        x=correlation.columns.tolist(),
        y=correlation.index.tolist(),
        colorscale='RdYlGn',
        zmin=-1,
        zmax=1,
        text=correlation.round(2).values,
        texttemplate='%{text}',
        showscale=True
    ))
    
    fig4.update_layout(
        title='Correlation Heatmap',
        height=500,
        dragmode=False,
        xaxis=dict(fixedrange=True),
        yaxis=dict(fixedrange=True)
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    st.divider()
    st.caption("Data sourced from Yahoo Finance via yfinance | Built with Python & Streamlit")
