import pandas as pd

# Load your Excel files
deposits = pd.read_excel('BINANCE TO COINDCX.xlsx')
sells = pd.read_excel('COINDCX SPOT TRADE.xlsx')

# --- Step 1: Format the DateTime columns properly ---
deposits['Deposit DateTime'] = pd.to_datetime(deposits['Deposit DateTime'])
sells['Sell DateTime'] = pd.to_datetime(sells['Sell DateTime'])

# --- Step 2: Sort both dataframes by DateTime ---
deposits = deposits.sort_values(by='Deposit DateTime').reset_index(drop=True)
sells = sells.sort_values(by='Sell DateTime').reset_index(drop=True)

# --- Step 3: Create an empty list for results ---
fifo_results = []

# --- Step 4: FIFO Matching ---
for _, sell_row in sells.iterrows():
    sell_coin = sell_row['Coin']
    sell_qty = sell_row['Quantity Sold']
    sell_datetime = sell_row['Sell DateTime']
    sell_price = sell_row['Sell Price (INR)']
    
    for idx, dep_row in deposits.iterrows():
        dep_coin = dep_row['Coin']
        dep_qty = dep_row['Quantity Deposited']
        dep_datetime = dep_row['Deposit DateTime']

        # Match only same coin and deposit earlier than sell
        if dep_coin == sell_coin and dep_qty > 0 and dep_datetime <= sell_datetime:
            qty_used = min(dep_qty, sell_qty)
            
            fifo_results.append({
                'Coin': sell_coin,
                'Deposit DateTime': dep_datetime,
                'Sell DateTime': sell_datetime,
                'Quantity Sold': qty_used,
                'Sell Price (INR)': sell_price,
                'Total Sale Value (INR)': qty_used * sell_price
            })
            
            # Update quantities
            deposits.at[idx, 'Quantity Deposited'] -= qty_used
            sell_qty -= qty_used
            
            if sell_qty <= 0:
                break  # move to next sell

# --- Step 5: Create result DataFrame ---
fifo_df = pd.DataFrame(fifo_results)

# --- Step 6: Save to Excel ---
fifo_df.to_excel('FIFO_Selling_Report.xlsx', index=False)

print("✅ FIFO Selling Report Generated: 'FIFO_Selling_Report.xlsx'")
