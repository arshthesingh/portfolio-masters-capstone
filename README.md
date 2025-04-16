# Master’s Capstone Project: Data-Driven Portfolio Construction
## Summary & Key Findings
### Objective:
Identify healthy and unhealthy stocks using quarterly financial data and fundamental analysis to assist in portfolio construction by predicting which stocks will over or underperform the S&P500 over the next 90 days.

### Approach:
Combine quarterly financial statements with stock price and S&P500 benchmark data. Compute financial ratios (e.g., ROE, ROA, PB Ratio) and engineer lag features, rolling averages, and additional derived metrics. Use a Random Forest classifier focused on high recall for unfavorable signals, and perform enhanced backtesting with risk management (transaction costs, slippage, stop-loss/take-profit rules).

### Results:

- The model successfully distinguishes stocks with poor financial health, achieving high recall on the negative class to minimize false positives.

- Backtesting demonstrates reasonable cumulative portfolio returns with controlled maximum drawdown and favorable Sharpe ratios.

- Feature importance analysis reveals that liquidity (e.g., cash ratio) and profitability (e.g., EPS and its lagged versions) are key drivers in predicting stock performance.

![Backtest for Financial Services after winsorization](./images/finsrvcs_win_backtest.png)

### Problem Statement & Motivation
Growing up in the New York City metropolitan area, I’ve always been fascinated by Wall Street’s dynamic interplay of market forces and corporate strategy. As an investor, even the smallest stake connects you to a company’s journey—its boardroom decisions, its operational pivots, and the market’s reaction. During my undergraduate studies in Economics, I deepened my appreciation for microeconomic theory and business dynamics. Now, as a data scientist, I’m applying that foundation to ask: Which companies are truly healthy, and which ones are financially unstable?

Most quantitative investment strategies lean heavily on price trends and technical indicators—an approach that often overlooks the fundamentals driving long‑term value. In this capstone project, I take a different tack: I merge 25 years of quarterly financial statements (income, balance sheet, and cash flow data) with adjusted closing prices to extract key ratios and signals of corporate stability. My objective is not to chase short‑term market swings but to identify “unhealthy” stocks—that is, those likely to underperform the S&P 500 over the next 90 days—and avoid them.

Given the high stakes in finance, I **prioritize recall on unfavorable outcomes: it’s more damaging to buy a weak stock than to miss a few winners**. I generate a binary “good”/“bad” signal and train a Random Forest classifier on engineered features—liquidity metrics, profitability ratios, and trend-based lags and rolling averages. An enhanced backtest then simulates a conservative portfolio strategy under realistic trading conditions (transaction costs, slippage, stop‑loss/take‑profit rules, and holding‑period limits). The result is a data‑driven framework for constructing a robust, risk‑aware portfolio that steers clear of financial underperformers.

### Data Sources and Description
This project leverages two primary data sources to build a comprehensive and robust dataset:
    • Quarterly Financial Statements
        ○ Source: Financial Modeling Prep API (financialmodelingprep.com)
        ○ Content: Provides detailed quarterly financial data, including variables such as net income, total assets, liabilities, revenue, and operating cash flow, among others.
        ○ Scope: Covers several decades of historical data across a diverse range of publicly traded companies.
    • Market Prices and Benchmark Data
        ○ Source: yfinance Python package (pypi.org/project/yfinance)
        ○ Content: Supplies adjusted closing prices and additional market details necessary for calculating market capitalization, historical returns, and future price movements.
        ○ Benchmark Integration: Includes historical price data for the S&P 500 index, enabling comparison and benchmarking of individual stock performance.
        ○ Methodology: An as-of merge technique was used to accurately align quarterly financial data with the relevant price and benchmark data, ensuring realistic modeling conditions.
        
Sincere appreciation to the developers and maintainers of these valuable resources.
