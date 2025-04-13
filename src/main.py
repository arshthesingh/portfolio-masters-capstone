import os
import pandas as pd
import numpy as np
import logging
from src.preprocessing import (
    load_financial_data,
    fix_financial_columns,
    calculate_financial_metrics,
    load_sp500_data,
    merge_sp500,
    add_target_and_features,
    merge_with_future_prices,
    calculate_final_returns,
    clean_final_df,
    load_stock_prices,
    add_market_cap_categories,
    filter_stock_prices,
    filter_final_data_by_symbols
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def preprocess() -> pd.DataFrame:
    # Define file paths
    financial_filepath = os.path.join("data", "merged_fullstock_data.csv")
    sp500_filepath = os.path.join("data", "sp.csv")
    stock_prices_filepath = os.path.join("data", "adjclose_stock.csv")
    
    # Load raw data
    df = load_financial_data(financial_filepath)
    sp_df = load_sp500_data(sp500_filepath)
    
    # Preprocess financial data
    df = fix_financial_columns(df)
    df = calculate_financial_metrics(df)
    df = merge_sp500(df, sp_df)
    df = add_target_and_features(df)
    df_model = merge_with_future_prices(df)
    df_model = calculate_final_returns(df_model)
    final_df = clean_final_df(df_model)
    
    # Load and process stock prices for market cap filtering
    sp_prices_df = load_stock_prices(stock_prices_filepath)
    sp_prices_df = add_market_cap_categories(sp_prices_df)
    filtered_stock_prices = filter_stock_prices(sp_prices_df)
    symbols_to_keep = filtered_stock_prices['Stock'].unique().tolist()
    final_df = filter_final_data_by_symbols(final_df, symbols_to_keep)
    
    # Additional filtering based on criteria
    final_df = final_df[final_df.groupby('symbol_stock')['quarter_number'].transform(lambda x: (x > 20).any())]
    final_df = final_df.reset_index(drop=True)

    final_df = final_df[final_df.groupby('symbol_stock')['Adj Close'].transform(lambda x: (x > 14).any())]
    final_df = final_df.reset_index(drop=True)
    
    # Return the DataFrame
    return final_df

if __name__ == "__main__":
    df_final = preprocess()
    print("Final processed DataFrame shape:", df_final.shape)