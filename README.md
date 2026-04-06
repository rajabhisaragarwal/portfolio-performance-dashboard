# 📈 Portfolio Performance Dashboard
A Python-based tool that pulls real historical market data and calculates institutional-grade performance metrics for any portfolio of stocks. 
Built as part of my journey learning quantitative finance and Python.
## Features
- User inputs any tickers and date range at runtime — no code changes required
- Pulls real adjusted closing prices via Yahoo Finance
- Calculates Total Return, Annualized Volatility, Sharpe Ratio, and Max Drawdown
- Compares every holding against the S&P 500 benchmark
- Generates 3 visualizations: cumulative returns, drawdown chart, and summary dashboard
## Illustration of the Final Output

### Cumulative Returns
![Cumulative Returns](cumulative_returns.png)

### Drawdown Chart
![Drawdown](drawdown.png)

### Summary Metrics
![Summary Metrics](summary_metrics.png)

## How to Run

1. Clone this repository or download the files
2. Install the required libraries:
pip install yfinance pandas numpy matplotlib
3. Open `portfolio_dashboard.ipynb` in Jupyter Notebook
4. Run all cells from top to bottom
5. Enter your tickers when prompted (e.g. AAPL, MSFT, SPY)
6. Enter your start and end dates (e.g. 2020-01-01 to 2024-12-31)

## Tech Stack

- **Python 3**
- **yfinance** — historical market data via Yahoo Finance
- **pandas** — data manipulation and analysis
- **numpy** — financial calculations and statistics
- **matplotlib** — data visualization
