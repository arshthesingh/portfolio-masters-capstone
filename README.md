# Master’s Capstone Project: Data-Driven Portfolio Construction
## Summary & Key Findings
### Objective:
Identify healthy and unhealthy stocks using quarterly financial data and fundamental analysis to assist in portfolio construction by predicting which stocks will over or underperform the S&P500 over the next 90 days.

### Approach:
Combine quarterly financial statements with stock price and S&P500 benchmark data. Compute financial ratios (e.g., ROE, ROA, PB Ratio) and engineer lag features, rolling averages, and additional derived metrics. Use a Random Forest classifier focused on high recall for unfavorable signals, and perform enhanced backtesting with risk management (transaction costs, slippage, stop-loss/take-profit rules).

### Results:

The model successfully distinguishes stocks with poor financial health, achieving high recall on the negative class to minimize false positives.

Backtesting demonstrates reasonable cumulative portfolio returns with controlled maximum drawdown and favorable Sharpe ratios.

Feature importance analysis reveals that liquidity (e.g., cash ratio) and profitability (e.g., EPS and its lagged versions) are key drivers in predicting stock performance.

![Backtest for Financial Services after winsorization](./images/finsrvcs_win_backtest.png)

### Data Sources
- The trading day price data was obtained via the yfinance package for Python. Sincere appreciation for their work!
https://pypi.org/project/yfinance/

- Quarterly financial documentation information was retrieved from the Financial Modeling Prep API.
https://site.financialmodelingprep.com/