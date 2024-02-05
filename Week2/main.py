# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#%% 
import pandas as pd
import numpy as np
import yfinance as yf
import wrds
from SP500scraper import get_SP500_list as getsp

#%%

# Get list of companies and create SQL string for accessing data about those companies
splist = getsp()
# spstr = ','.join([f"'{element}'" for element in splist['Symbol']])
list_ = "'AMT','APPL','MMM','DIS'"

q = f"SELECT * FROM crsp.stkmthsecuritydata WHERE ticker IN ({list_}) "
         
         
#%%
wrds_connection = wrds.Connection(wrds_username = 'rolan093', wrds_password = 'Datrockydog2020!')
libraries = wrds_connection.list_libraries()

res = wrds_connection.raw_sql(q, date_cols='mthcaldt')
if type(res) != pd.DataFrame:
    try:
        print(res)
    except:
        pass
    raise TypeError

wrds_connection.close()

print(res.shape)

AMT_data = res.loc[['ticker'] == 'AMT']

# data.columns=['ticker', 'permno','date', 'price','mktcap','ret']    # notice I am renaming my columns
# data.set_index(['ticker', 'date'],inplace=True)                     # What does the inplace do?

#%%
