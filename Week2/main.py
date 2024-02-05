# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

"""
1. Access data on WRDS
a. Log in to WRDS on a browser and check out what products are available
b. Using Python, create a connection object and browse the Libraries just to see what’s
    around. How does this compare with what you see on the web browser?

    Web browser has many access points and has many webpages that lead to query input fields. 
    SQL query locally with Python has one access point to data.
    
    Web browser is more opt in.

c. For both the browser, and Python, open up the CRSP library/database. How do these
    compare? WHY do we bother figuring out how to access data through Python? What are
    the advantages and disadvantages of each approach, and when might you want to use
    one over the other?
    
    Python local access may simplify the process of accessing data because queries can be structured locally rather then using the web GUI which is simplified but opinionatedly slower.
    
2. Getting S&P 500 returns
    a. Monthly stock returns are stored in the table stkmthsecuritydata. Using the S&P 500
    scraper we used last week, get the list of companies, then download returns for these
    companies into a Pandas DataFrame object (this is the default).
    
    i. You will need to think about structuring a SQL query to do this, which will
        require manipulating a string. I CAN HELP WITH THIS!
        
    ii. You will need to use the IN syntax in SQL, which looks like SELECT * FROM *
        WHERE ticker IN ({list}). I CAN HELP WITH THIS TOO!

    b. Take a look at the data for the ticker “AMT”
    
    i. What different variables are included in this data and what does each mean?
    
1. permno: A unique identifier for each security in the database.
2. yyyymm: Year and month, typically indicating the period for the data row.
3. mthcaldt: The calendar date for the month, possibly the end date for monthly data.
4. mthcompflg: Monthly computation flag, may indicate if monthly data was computed or estimated.
5. mthcompsubflg: Sub-flag for monthly computation, providing additional details on how data was computed or adjusted.
6. mthprc: Monthly price, likely the closing price of the security for the month.
7. mthprcflg: Flag indicating the status or reliability of the monthly price.
8. mthprcdt: Date corresponding to the monthly price.
9. mthdtflg: Date flag, may indicate validity or source of the date information.
10. mthdelflg: Deletion flag, indicating if the security was deleted from the database in that month.
11. mthcap: Monthly market capitalization.
12. mthprevprc: Price of the security in the previous month.
13. mthprevprcflg: Flag for the previous month's price, similar to mthprcflg.
14. mthprevdt: Date of the previous month's price.
15. mthprevdtflg: Flag indicating the status or source of the previous month's date.
16. mthprevcap: Market capitalization in the previous month.
17. mthret: Monthly return, possibly the total return including dividends.
18. mthretx: Monthly return excluding dividends.
19. mthretflg: Flag for the monthly return, indicating calculation method or reliability.
20. mthdiscnt: Discount rate or factor applied for the month, possibly in valuation models.
21. mthvol: Monthly volume, representing the quantity of shares traded.
22. mthvolflg: Flag indicating the status or reliability of the trading volume data.
23. mthprcvol: Price volatility for the month.
24. mthfacshrflg: Factor share flag, possibly indicating adjustments to share counts or splits.
25. mthprcvolmisscnt: Count of missing price/volume data points in the month.
26. cusip: Committee on Uniform Securities Identification Procedures number, a unique identifier for U.S. and Canadian securities.
27. ticker: Stock ticker symbol.
28. issuernm: Name of the issuing company or entity.
29. usincflg: U.S. income flag, possibly indicating if the issuer is subject to U.S. income taxes.
30. issuertype: Type of issuer, such as corporation, government, etc.
31. securitytype: Broad category of the security, e.g., stock, bond.
32. securitysubtype: More specific category of the security within its type.
33. sharetype: Type of shares, e.g., common, preferred.
34. exchangetier: Classification or tier of the exchange where the security is traded.
35. primaryexch: Primary exchange where the security is listed.
36. tradingstatusflg: Flag indicating the trading status of the security, e.g., active, halted.
37. conditionaltype: Specifies any conditions applied to the trading or data for the security.
    
    ii. What do you notice about the data? Why might you see something like this?
    
    Lots of discrete/categorical datatypes. Used to help explain, segment, bucket data from its source + other attributes.

    c. Try setting a multi-level index using the set_index() function, where ticker is the first
    index and mthcaldt is the second (feel free to rename any column, btw).

    i. Now try using the unstack() method on the mthret column. What error is
        returned and why?
        
        'Level mthret not found' --> There is no index on mthret which is why it can't be unstacked
        
        ii. What other identifier (besides ticker) might be useful here?
        
        yyymmm, mthcaldt for indexes. Most attributes data are usefull identifiers though not all are usefull for analyzing the data or being used as an index.
        
        iii. Set a new multilevel index using the other identifier.

    d. Calculate the variance-covariance matrix for returns. This is the pairwise covariance
    across all companies. What does this matrix tell us? Where else in Finance might we
    have used similar quantities?

3. Other Data Sources
a. If you’ve not already installed the yfinance package, do so now (this should have been
done last week).
b. Download the data for each of the S&P 500 firms from Yahoo! Finance as well. Referring
to last week’s exercise is fine (and in fact good! This is one way we learn...review!). You
may also need to refer to the documentation for yfinance.
c. Create a Pandas dataframe that has the returns for each company. You may organize this
in “long” format (one column of returns, with each observation identified by date and

ticker) or in “wide” format, where many columns of returns, each column representing a
single company’s return. You might want to check out the download() function of the
yfinance package.
d. Calculate the returns for these companies and the variance-covariance matrix. Calculate
a sum of the vcv (across ALL elements) for both the CRSP and Yahoo! Finance vcv’s. Why
do you see a difference? What’s driving this? Don’t just say “different data sources.”
What about those data sources is driving the difference?

4. Pandas datareader is another great resource for accessing external data sources. Please visit the
documentation and read about the different data sources available through pandas datareader.
Summarize what’s available and who is collecting data for THREE different data sources available
through pandas datareader, other than Yahoo! Finance and CRSP.
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

#%% b.

print(res.shape)

AMT_data = res.loc[(res.ticker == 'AMT')]

#%%

copy_res = res.copy()
copy_res.set_index(['ticker','mthcaldt'], inplace=True)

#%%

# error = copy_res.unstack(level='mthret') # Error! 

#%%

# 2.c.iii

copy_res = res.copy()
copy_res.set_index(['ticker','yyyymm'], inplace=True)





