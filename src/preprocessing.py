# src/preprocessing.py
import os
import pandas as pd
import numpy as np

def load_financial_data(filepath: str) -> pd.DataFrame:
    """Load financial data from a CSV file."""
    return pd.read_csv(filepath)

def fix_financial_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix discrepancies in columns.
    Fill missing totalCurrentLiabilities with totalLiabilities and compute totalEquity.
    """
    df['totalCurrentLiabilities'] = df['totalCurrentLiabilities'].fillna(df['totalLiabilities'])
    df['totalEquity'] = df['totalLiabilitiesAndTotalEquity'] - df['totalLiabilities']
    return df

def calculate_financial_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate various financial ratios and metrics.
    """
    df['ROE'] = df['netIncome_x'] / df['totalEquity']
    df['ROA'] = df['netIncome_x'] / df['totalAssets']
    df['ROI'] = df['netIncome_x'] / df['totalInvestments']
    df['log_return'] = np.log(df['Adj Close'] / df.groupby('symbol_stock')['Adj Close'].shift(1))
    
    # Debt ratios
    df['debtToEquity'] = df['totalDebt'] / df['totalEquity']
    df['netDebtRatio'] = df['netDebt'] / df['totalAssets']
    df['debt_ratio'] = df['totalLiabilities'] / df['totalAssets']
    
    # Cash flow ratios
    df['free_cash_flow_yield'] = df['freeCashFlow'] / df['totalEquity']
    df['Op_Cash_Flow_to_Revenue'] = df['operatingCashFlow'] / df['revenue']
    df['Op_Cash_Flow_to_Liabilities'] = df['operatingCashFlow'] / df['totalCurrentLiabilities']
    
    # Inventory, interest, investment ratios
    df['inventoryTurnover'] = df['costOfRevenue'] / df['inventory_x']
    df['inventory_to_assets'] = df['inventory_x'] / df['totalAssets']
    df['interest_coverage'] = df['operatingIncome'] / df['interestExpense']
    df['longinvest_to_assets'] = df['longTermInvestments'] / df['totalAssets']
    df['longinvest_to_equity'] = df['longTermInvestments'] / df['totalEquity']
    df['totalInvestments_to_assets'] = df['totalInvestments'] / df['totalAssets']
    
    # Other important ratios
    df['Profit_Margin'] = df['netIncome_x'] / df['revenue']
    df['retained_earnings'] = df['netIncome_x'] - df['dividendsPaid']
    df['re_ratio'] = df['retained_earnings'] / df['netIncome_x']
    df['currentRatio'] = df['totalCurrentAssets'] / df['totalCurrentLiabilities']
    df['cash_ratio'] = df['cashAndShortTermInvestments'] / df['totalCurrentLiabilities']
    df['capital_light'] = df['capitalExpenditure'] / df['operatingCashFlow']
    df['liabilitiesToEquity'] = df['totalLiabilities'] / df['totalEquity']
    df['taxAssetsRatio'] = df['taxAssets'] / df['totalAssets']
    df['Deferred_Revenue_to_Revenue'] = df['deferredRevenue'] / df['revenue'].replace(0, np.nan)
    df['Deferred_Revenue_to_Current_Liabilities'] = df['deferredRevenue'] / df['totalCurrentLiabilities'].replace(0, np.nan)
    df['goodwillIntangible_to_assets'] = df['goodwillAndIntangibleAssets'] / df['totalAssets']
    df['sellingMarketing_to_revenue'] = df['sellingAndMarketingExpenses'] / df['revenue']
    df['rnd_to_revenue'] = df['researchAndDevelopmentExpenses'] / df['revenue']
    
    # Valuation metrics
    df['Book_Value_per_share'] = df['totalStockholdersEquity'] / df['weightedAverageShsOut']
    df['PE_ratio'] = df['Adj Close'] / df['eps'].replace(0, np.nan)
    df['PB_ratio'] = df['Adj Close'] / df['Book_Value_per_share'].replace(0, np.nan)
    return df

def date_parser(date_str: str, max_year: int = 2025) -> pd.Timestamp:
    """
    Parse a date string with two-digit year format.
    If the year is greater than max_year, assume it belongs to the previous century.
    """
    dt = pd.to_datetime(date_str, format="%m/%d/%y")
    if dt.year > max_year:
        dt = dt.replace(year=dt.year - 100)
    return dt

def load_sp500_data(filepath: str) -> pd.DataFrame:
    """
    Load S&P500 data from a CSV file.
    """
    df = pd.read_csv(filepath)
    df['Date'] = df['Date'].apply(date_parser)
    df = df[df['Date'] >= pd.Timestamp('1999-01-01')]
    df.rename(columns={'Date': 'acceptedDate'}, inplace=True)
    df['acceptedDate'] = pd.to_datetime(df['acceptedDate'])
    return df

def merge_sp500(df: pd.DataFrame, sp_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the financial DataFrame with the S&P500 data using an asof merge.
    Ensure both 'acceptedDate' columns are datetime types.
    """
    df['acceptedDate'] = pd.to_datetime(df['acceptedDate'], errors='coerce')
    sp_df['acceptedDate'] = pd.to_datetime(sp_df['acceptedDate'], errors='coerce')
    
    merged_df = pd.merge_asof(
        df.sort_values('acceptedDate'),
        sp_df.sort_values('acceptedDate'),
        on='acceptedDate',
        direction='backward',
        suffixes=('', '_sp')
    )
    return merged_df

def add_target_and_features(df: pd.DataFrame, horizon_days: int = 90) -> pd.DataFrame:
    """
    Add target dates, growth rates, lag features, and rolling averages.
    """
    df['accepted_date'] = pd.to_datetime(df['acceptedDate'], errors='coerce')
    df['target_date'] = df['accepted_date'] + pd.Timedelta(days=horizon_days)
    df = df.sort_values(by=['symbol_stock', 'accepted_date'])
    
    # Growth rates
    df['revenue_growth_quarterly'] = df.groupby('symbol_stock')['revenue'].pct_change(periods=1)
    df['revenue_growth_annual'] = df.groupby('symbol_stock')['revenue'].pct_change(periods=4)
    df['eps_growth_quarterly'] = df.groupby('symbol_stock')['epsdiluted'].pct_change(periods=1)
    df['eps_growth_annual'] = df.groupby('symbol_stock')['epsdiluted'].pct_change(periods=4)
    
    # Lag features
    lag_features = ['ROE', 'ROA', 'free_cash_flow_yield', 're_ratio', 'Profit_Margin',
                    'debtToEquity', 'eps', 'epsdiluted', 'ebitda', 'goodwillIntangible_to_assets',
                    'sellingMarketing_to_revenue', 'totalInvestments_to_assets', 'rnd_to_revenue',
                    'inventory_to_assets']
    for feature in lag_features:
        df[f'{feature}_lag1'] = df.groupby('symbol_stock')[feature].shift(1)
        df[f'{feature}_lag4'] = df.groupby('symbol_stock')[feature].shift(4)
    
    # Rolling averages over 4 and 8 quarters
    for feature in lag_features:
        df[f'{feature}_roll4'] = df.groupby('symbol_stock')[feature].transform(lambda x: x.rolling(window=4, min_periods=1).mean())
        df[f'{feature}_roll8'] = df.groupby('symbol_stock')[feature].transform(lambda x: x.rolling(window=8, min_periods=1).mean())
    return df

def merge_with_future_prices(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use an asof merge on the target date to attach future stock prices.
    """
    df_prices = df[['symbol_stock', 'accepted_date', 'Adj Close', 'Close']].rename(
        columns={'accepted_date': 'future_date', 'Adj Close': 'future_price', 'Close': 'future_dji'}
    ).sort_values('future_date')
    
    df = df.dropna(subset=['accepted_date'])
    df['target_date'] = df['accepted_date'] + pd.Timedelta(days=90)
    df_prices = df_prices.dropna(subset=['future_date'])
    
    df_model = pd.merge_asof(
        left=df.sort_values('target_date'),
        right=df_prices,
        left_on='target_date',
        right_on='future_date',
        by='symbol_stock',
        direction='forward'
    )
    return df_model

def calculate_final_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate log returns, relative log returns, and create a binary target.
    """
    df['log_dji_return'] = np.log(df['future_dji'] / df['Close'])
    df['log_return_future'] = np.log(df['future_price'] / df['Adj Close'])
    df = df.dropna(subset=['log_return_future']).copy()
    df['relative_log_return'] = df['log_return_future'] - df['log_dji_return']
    threshold = np.log(1 + 0.02)
    df['good_stock'] = (df['relative_log_return'] > threshold).astype(int)
    return df

def clean_final_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop rows with NaN or infinite values in key columns and reset the index.
    """
    cols_to_check = ['Book_Value_per_share', 'PE_ratio', 'PB_ratio']
    df = df[np.isfinite(df[cols_to_check]).all(axis=1)]
    df.reset_index(drop=True, inplace=True)
    return df

def load_stock_prices(filepath: str) -> pd.DataFrame:
    """Load stock prices data from a CSV file."""
    return pd.read_csv(filepath)

def add_market_cap_categories(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate market cap and assign market cap categories.
    """
    df['Market Cap'] = df['Adj Close'] * df['Volume']
    def categorize_market_cap(market_cap):
        if market_cap >= 200_000_000_000:
            return 'Mega-cap'
        elif market_cap >= 10_000_000_000:
            return 'Big-cap'
        elif market_cap >= 2_000_000_000:
            return 'Mid-cap'
        elif market_cap >= 250_000_000:
            return 'Small-cap'
        elif market_cap >= 50_000_000:
            return 'Micro-cap'
        else:
            return 'Nano-cap'
    df['Market Cap Category'] = df['Market Cap'].apply(categorize_market_cap)
    return df

def filter_stock_prices(df: pd.DataFrame, categories_to_keep=None) -> pd.DataFrame:
    """
    Filter the stock prices DataFrame by specified market cap categories.
    """
    if categories_to_keep is None:
        categories_to_keep = ['Mega-cap', 'Big-cap', 'Mid-cap', 'Small-cap', 'Micro-cap']
    return df[df['Market Cap Category'].isin(categories_to_keep)]

def filter_final_data_by_symbols(final_df: pd.DataFrame, symbols: list) -> pd.DataFrame:
    """
    Filter the final DataFrame to only include rows for the given symbols.
    """
    return final_df[final_df['symbol_stock'].isin(symbols)]


def winsorize_columns(
    df: pd.DataFrame,
    columns: list,
    lower_quantile: float = 0.01,
    upper_quantile: float = 0.99,
    suffix: str = '_win'
    ) -> (pd.DataFrame, list):
    """
    Winsorize specified columns of the DataFrame by capping values below the lower quantile 
    and above the upper quantile.
    
    Parameters:
        df: The input DataFrame.
        columns: List of column names to winsorize.
        lower_quantile: The lower quantile threshold (default is 0.01).
        upper_quantile: The upper quantile threshold (default is 0.99).
        suffix: Suffix to append to the winsorized column names.
    
    Returns:
        A tuple of:
          - A new DataFrame with winsorized columns added.
          - A list of the winsorized column names.
    """
    df_copy = df.copy()
    winsorized_columns = []
    for col in columns:
        if col in df_copy.columns:
            lower_bound = df_copy[col].quantile(lower_quantile)
            upper_bound = df_copy[col].quantile(upper_quantile)
            new_col = f"{col}{suffix}"
            df_copy[new_col] = df_copy[col].clip(lower=lower_bound, upper=upper_bound)
            winsorized_columns.append(new_col)
        else:
            print(f"Warning: Column '{col}' not found in DataFrame.")
    return df_copy, winsorized_columns

