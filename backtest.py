import pandas as pd
import numpy as np

def simulate_trades_for_stock_baseline(stock_df, transaction_cost, slippage):
    """
    Baseline simulation:
      - Buy on signal 1 when no position is open.
      - Sell when signal turns 0.
      - Close any open trade at the end.
    """
    trades = []
    open_trade = None
    
    for i, row in stock_df.iterrows():
        date = row['accepted_date']
        price = row['Adj Close']
        signal = row['predicted_signal']
        
        if open_trade is None:
            if signal == 1:
                open_trade = {'entry_date': date, 'entry_price': price}
        else:
            if signal == 0:
                exit_price = price
                raw_return = exit_price / open_trade['entry_price'] - 1
                net_return = raw_return - 2 * (transaction_cost + slippage)
                trades.append({
                    'symbol_stock': row['symbol_stock'],
                    'entry_date': open_trade['entry_date'],
                    'exit_date': date,
                    'trade_return': net_return
                })
                open_trade = None
                
    # Close any open trade at the end of the data
    if open_trade is not None:
        last_row = stock_df.iloc[-1]
        exit_price = last_row['Adj Close']
        raw_return = exit_price / open_trade['entry_price'] - 1
        net_return = raw_return - 2 * (transaction_cost + slippage)
        trades.append({
            'symbol_stock': last_row['symbol_stock'],
            'entry_date': open_trade['entry_date'],
            'exit_date': last_row['accepted_date'],
            'trade_return': net_return
        })
    return trades

def simulate_trades_for_stock_enhanced(stock_df, transaction_cost, slippage,
                                       stop_loss=-0.05, take_profit=0.10, max_hold_periods=4,
                                       risk_per_trade=1000, account_balance=100000):
    """
    Enhanced simulation with risk management:
      - Buys on signal 1 and holds if signals remain positive.
      - Exits on stop-loss, take-profit, fundamentals deterioration, maximum holding period, or when the signal turns negative.
      - Position sizing is based on fixed risk per trade.
    """
    trades = []
    open_trade = None
    hold_periods = 0
    
    def calculate_position_size(entry_price):
        risk_per_share = entry_price * abs(stop_loss)
        return risk_per_trade / risk_per_share if risk_per_share else 0
    
    for i, row in stock_df.iterrows():
        date = row['accepted_date']
        price = row['Adj Close']
        signal = row['predicted_signal']
        current_fundamentals = row.get('ROE', None)
        
        if open_trade is None:
            if signal == 1:
                position_size = calculate_position_size(price)
                open_trade = {
                    'entry_date': date,
                    'entry_price': price,
                    'position_size': position_size,
                    'entry_fundamentals': current_fundamentals
                }
                hold_periods = 1
        else:
            hold_periods += 1
            current_return = price / open_trade['entry_price'] - 1
            
            # Check stop-loss or take-profit conditions
            if current_return <= stop_loss or current_return >= take_profit:
                exit_price = price
                raw_return = exit_price / open_trade['entry_price'] - 1
                net_return = raw_return - 2 * (transaction_cost + slippage)
                trades.append({
                    'symbol_stock': row['symbol_stock'],
                    'entry_date': open_trade['entry_date'],
                    'exit_date': date,
                    'trade_return': net_return,
                    'position_size': open_trade['position_size'],
                    'hold_periods': hold_periods,
                    'exit_reason': 'stop_loss/take_profit'
                })
                open_trade = None
                hold_periods = 0
                continue
            
            # Exit if fundamentals deteriorate (e.g., ROE drops >20%)
            if signal == 1 and open_trade['entry_fundamentals'] is not None and current_fundamentals is not None:
                if current_fundamentals < 0.8 * open_trade['entry_fundamentals']:
                    exit_price = price
                    raw_return = exit_price / open_trade['entry_price'] - 1
                    net_return = raw_return - 2 * (transaction_cost + slippage)
                    trades.append({
                        'symbol_stock': row['symbol_stock'],
                        'entry_date': open_trade['entry_date'],
                        'exit_date': date,
                        'trade_return': net_return,
                        'position_size': open_trade['position_size'],
                        'hold_periods': hold_periods,
                        'exit_reason': 'fundamentals_change'
                    })
                    open_trade = None
                    hold_periods = 0
                    continue
            
            # Force exit if maximum holding period is reached
            if hold_periods >= max_hold_periods:
                exit_price = price
                raw_return = exit_price / open_trade['entry_price'] - 1
                net_return = raw_return - 2 * (transaction_cost + slippage)
                trades.append({
                    'symbol_stock': row['symbol_stock'],
                    'entry_date': open_trade['entry_date'],
                    'exit_date': date,
                    'trade_return': net_return,
                    'position_size': open_trade['position_size'],
                    'hold_periods': hold_periods,
                    'exit_reason': 'max_hold_period'
                })
                open_trade = None
                hold_periods = 0
                continue
            
            # Exit trade if signal turns negative
            if signal == 0:
                exit_price = price
                raw_return = exit_price / open_trade['entry_price'] - 1
                net_return = raw_return - 2 * (transaction_cost + slippage)
                trades.append({
                    'symbol_stock': row['symbol_stock'],
                    'entry_date': open_trade['entry_date'],
                    'exit_date': date,
                    'trade_return': net_return,
                    'position_size': open_trade['position_size'],
                    'hold_periods': hold_periods,
                    'exit_reason': 'signal_change'
                })
                open_trade = None
                hold_periods = 0
                
    # Close any open trade at the end of the data
    # if open_trade is not None:
    #     last_row = stock_df.iloc[-1]
    #     exit_price = last_row['Adj Close']
    #     raw_return = exit_price / open_trade['entry_price'] - 1
    #     net_return = raw_return - 2 * (transaction_cost + slippage)
    #     trades.append({
    #         'symbol_stock': last_row['symbol_stock'],
    #         'entry_date': open_trade['entry_date'],
    #         'exit_date': last_row['accepted_date'],
    #         'trade_return': net_return,
    #         'position_size': open_trade['position_size'],
    #         'hold_periods': hold_periods,
    #         'exit_reason': 'end_of_data'
    #     })


    if open_trade is not None:
        # Use the last row of the provided DataFrame for the symbol
        last_row = stock_df.iloc[-1]
        exit_price = last_row['Adj Close']
        # Calculate raw return: price change from entry to exit
        raw_return = exit_price / open_trade['entry_price'] - 1
        # Subtract fees: assume both entry and exit incur costs
        net_return = raw_return - 2 * (transaction_cost + slippage)
        trades.append({
            'symbol_stock': last_row['symbol_stock'],
            'entry_date': open_trade['entry_date'],
            'exit_date': last_row['accepted_date'],
            'trade_return': net_return,
            'position_size': open_trade.get('position_size', None),
            'hold_periods': hold_periods,
            'exit_reason': 'end_of_data'
        })

    return trades
