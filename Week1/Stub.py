# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#%% Import Packages


import numpy as np
import yfinance as yf
from SP500scraper import get_SP500_list

#%% 

sp500_data = get_SP500_list()
tickerList = sp500_data['Symbol'].values
tickerList = np.char.strip(tickerList.astype('str'))

#%%

stock_data = {}

for ticker in tickerList:
    try:
        print(ticker)
        tick = yf.Ticker(ticker)
        data = tick.info
        stock_data[ticker] = data
    except:
        print(f"Ticker {ticker} no longer exists")

stock_data = {key: value for key,value in stock_data.items() if len(value) > 100}

#%%

n = len(stock_data)
current_price = np.zeros(n)
forward_Eps = np.zeros(n)
forward_PE = np.zeros(n)
forward_PE_manual = np.zeros(n) 
for i, key in enumerate(stock_data.keys()):
    stock = stock_data[key]
    try:
        current_price[i] = stock["currentPrice"]
    except KeyError:
        current_price[i] = np.nan
    try:
        forward_Eps[i] = stock["forwardEps"]
    except KeyError:
        forward_Eps[i] = np.nan
    try:
        forward_PE[i] = stock["forwardPE"]
    except KeyError:
        forward_PE[i] = np.nan
    if not np.isnan(current_price[i]) and not np.isnan(forward_Eps[i]) and forward_Eps[i] != 0:
        forward_PE_manual[i] = current_price[i] / forward_Eps[i]
    else:
        forward_PE_manual[i] = np.nan

#%%

# Current price
current_price_mean = np.nanmean(current_price)
current_price_median = np.nanmedian(current_price)
current_price_std = np.nanstd(current_price)

# Forward EPS
forward_Eps_mean = np.nanmean(forward_Eps)
forward_Eps_median = np.nanmedian(forward_Eps)
forward_Eps_std = np.nanstd(forward_Eps)

# Forward PE
forward_PE_mean = np.nanmean(forward_PE)
forward_PE_median = np.nanmedian(forward_PE)
forward_PE_std = np.nanstd(forward_PE)

# Manual Forward PE
forward_PE_manual_mean = np.nanmean(forward_PE_manual)
forward_PE_manual_median = np.nanmedian(forward_PE_manual)
forward_PE_manual_std = np.nanstd(forward_PE_manual)

print("Current Price - Mean: ", current_price_mean, "Median: ", current_price_median, "Std Dev: ", current_price_std)
print("Forward EPS - Mean: ", forward_Eps_mean, "Median: ", forward_Eps_median, "Std Dev: ", forward_Eps_std)
print("Forward PE - Mean: ", forward_PE_mean, "Median: ", forward_PE_median, "Std Dev: ", forward_PE_std)
print("Manual Forward PE - Mean: ", forward_PE_manual_mean, "Median: ", forward_PE_manual_median, "Std Dev: ", forward_PE_manual_std)

#%%

# Correlations
combined_data = np.array([current_price, forward_Eps, forward_PE, forward_PE_manual]).T

# Filter out Nan's
clean_data = combined_data[~np.isnan(combined_data).any(axis=1)]

# Separate into rays
clean_current_price = clean_data[:, 0]
clean_forward_Eps = clean_data[:, 1]
clean_forward_PE = clean_data[:, 2]
clean_forward_PE_manual = clean_data[:, 3]

correlation_matrix = np.corrcoef([clean_current_price, clean_forward_Eps, clean_forward_PE, clean_forward_PE_manual])

print("Correlation matrix | current price, forward EPS, forward PE, manual forward PE")
print(correlation_matrix)
# ^^^ Notice how forward_PE correlates perfectly with forward_PE_manual

#%%

# "Is 'market cap' and 'current price' correlated?"

market_cap_array = np.zeros(n)
for i, key in enumerate(stock_data.keys()):
    try:
        market_cap_array[i] = stock_data[key]["marketCap"]
    except KeyError:
        market_cap_array[i] = np.nan
        
# Combine the arrays
combined_data = np.array([market_cap_array, current_price]).T

# Remove rows with NaNs
clean_data = combined_data[~np.isnan(combined_data).any(axis=1)]

# Extract the clean market cap and current price data
clean_market_cap = clean_data[:, 0]
clean_current_price = clean_data[:, 1]

# Calculate the correlation coefficient
correlation_coefficient = np.corrcoef(clean_market_cap, clean_current_price)[0, 1]

print(f"The correlation coefficient between market cap and current price is: {correlation_coefficient}")