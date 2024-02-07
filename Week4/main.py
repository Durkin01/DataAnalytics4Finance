# -*- coding: utf-8 -*-

"""
Week 4 – In-class Exercise
Complete the following steps and answer the ques>ons.
You can download the data you will need (put it in your current/working directory) from the
course homepage, via this link. It’s a pickle! You will need to load it using the d.read_pickle()
func>on. Take a look at the Pandas documenta>on (or ask ChatGPT) how to use it.
In this exercise, we are going to create a trading strategy, where at the end of each year, we
calculate the Minimum Variance PorOolio (like last week) and then find porOolio returns for
each month. This would be an example of ‘backtes>ng’, where we can go back and look at how
a porOolio would have performed over >me.
There are a few things to think about. First, we need to be careful to use informa>on ONLY
available at, or before, a par>cular point in >me. If we DO include future informa>on, this would
induce what’s called ‘look-ahead bias.’ For example, we don’t want to use a return at >me � + 1
to find a weight at >me �. While this sounds obvious, some>mes this can be tricky and you
might be off by a month.
Another considera>on is what to do when a stock falls out of the sample. Meaning AMT might
be in the sample in January of 1996, but then gone from the sample in February 1996. What
does it mean to have a return for January, but then not in February? How should you handle
that? The answers depend on how CRSP records past events. Not all databases will have the
same policies for this sort of thing (For CRSP, if there is a return for January but not February,
then the stock was delisted AT SOME POINT in January, so if you allocated weight in your
porOolio for AMT, you would get a return for January, but then that stock wouldn’t be available
for February).
Lastly, how are the weights of the porOolio going to evolve during the year (remember, we are
sebng the porOolio at the end of December, then holding that porOolio for the following year).
Answering these ques>ons and avoiding ‘look-ahead bias’ can be difficult, so pay aden>on to
these things.
"""

"""
1. Download the file pricedata.pkl from the course homepage. This is basically the CRSP
    monthly return data we worked with last week, but for all firms, not just firms currently
    in the S&P 500.
        • With this data, we are going to make a minimum variance porOolio once per year
            → On the last day of December we are going to calculate a MVP for the prior 15
            years, and then we are going to ‘buy’ that porOolio and hold it for a year
        • Aier a year, we are going to recalculate the MVP, ‘rebalance’, and hold the new
            porOolio for a year. We are going to do this from 1990 through the most recent
            data
"""


"""
2. For each year, we are only going to consider the largest 100 companeis by market cap at
the end of each year. Using the data above, find the companies that may be in the
minimum variance porOolio for each year on the last day of December.
• You might check the nlargest() method of a Pandas.groupby object for this
• This will tell us which firms we are considering for the porOolio for each year.
• You need to create a new indicator variable to tell you if the firm is poten>ally in
the porOolio.
• Think about which year these companies are going to be part of the porOolio. Is
it the year in which observa>on is originally contained (12/31/XXXX)? Or the
following year? Adjust if ‘year’ if necessary. We will come back to these
companies shortly
• It is worth get a list of the unique permnos that appear in this data. It will allow
you to filter your main data for only firms you will eventually use.
"""

#%%
import pandas as pd
import numpy as np
from scipy.optimize import minimize

# Load the pickle file
pricedata = pd.read_pickle('pricedata.pkl')

# Add a year column to the dataframe for easier processing
pricedata['year'] = pricedata['date'].dt.year

# Group by year and permno, then take the last observation to get the market cap at the end of the year
end_of_year = pricedata.groupby(['permno', 'year']).last().reset_index()

# Next, for each year group, we will take the largest 100 firms by market cap
top_firms_by_year = end_of_year.groupby('year').apply(lambda x: x.nlargest(100, 'mktcap')).reset_index(drop=True)

# Indicate if each firm is potentially in the portfolio
top_firms_by_year['in_portfolio'] = True

# Adjust the year to indicate when it is part of the portfolio,
# which is the following year after observation
top_firms_by_year['portfolio_year'] = top_firms_by_year['year'] + 1

# Collect the unique permnos that appear in this data
unique_permnos = top_firms_by_year['permno'].unique()

# Check the output
top_firms_by_year[top_firms_by_year['year'] == top_firms_by_year['year'].max()].head()
#%%

"""
3. Go back to your original data and filter on two things: date and permno.
• Drop all observa>ons prior to 1975
• Drop all firms not in the list of firms that may be part of the MVP at some point
• Aier filtering, unstack your data by permno.
"""

#%%
# Filter out observations before 1975
pricedata_filtered = pricedata[pricedata['year'] >= 1975]

# Keep only the firms that are in our list of firms potentially in the MVP (using index for permno)
# Filter using the index and ensure 'unique_permnos' is a list if it's not already
unique_permno_list = unique_permnos.tolist()
pricedata_filtered = pricedata_filtered.loc[pricedata_filtered.index.isin(unique_permno_list)]

# Unstack the DataFrame to get permnos as columns (This creates a MultiIndex in columns)
# Ensure the date is set as an index before unstacking
pricedata_filtered = pricedata_filtered.set_index(['date'], append=True)
unstacked_data = pricedata_filtered.unstack(level='permno')
#%%

"""
4. This is where things get harder! We need to find the ini+al porOolio weights for each
year. This will require: filtering by date and permno, considering missing data, finding
the variance-covariance matrix, and performing the op>miza>on from last week. You will
want to loop through years for this.
• First, drop data by date, keeping only the last 15 years for each cycle of the for
loop (you will start with 1989, then 1990, then 1991, ... , finish with 2022). You
will need to drop future data in each cycle as well.
• We want enough observa>ons that the correla>ons are meaningful. So drop any
firms from the sample for which there is less than 10 years of data. Ie if returns
are missing for more than 5 years, then drop the firm from the sample.
• Calculate the variance-covariance matrix and perform the op>miza>on. You will
want to store your weights in a DataFrame that contains the weights, permno,
and year for which these weights will start the porOolio.
• If your weights are sufficiently small (less than 10!") set the weight equal to zero
• Merge your weights back into your original data set by year.
"""

#%%
# Define the function to calculate portfolio variance
def portfolio_variance(weights, cov_matrix):
    return weights.T @ cov_matrix @ weights
    
def find_mvp_weights(cov_matrix):
    # Check if the covariance matrix has NaN values and handle them
    if cov_matrix.isna().any().any():
        cov_matrix = cov_matrix.fillna(0)

    # Regularization: Add a small constant to the diagonal elements
    cov_matrix += np.eye(cov_matrix.shape[0]) * 1e-4
    num_assets = len(cov_matrix)
    initial_guess = np.repeat(1 / num_assets, num_assets)
    bounds = tuple((0.0, 1.0) for asset in range(num_assets))
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    
    result = minimize(portfolio_variance, initial_guess, args=(cov_matrix,), method='SLSQP', bounds=bounds, constraints=constraints)
    
    if result.success:
        return result.x
    else:
        raise ValueError("Optimization failed")

# Load the pricedata DataFrame
# pricedata = pd.read_pickle('pricedata.pkl')  # Uncomment this line if you haven't already loaded the data

# Add the 'year' column to the dataframe
pricedata['year'] = pricedata['date'].dt.year

# Assuming 'unique_permnos' is already defined as per the previous steps (list of permno's)

# Calculate the portfolio weights for each year
portfolio_weights = pd.DataFrame()

# Add this before the for-loop starts
if 'permno' in pricedata.index.names:
    pricedata.reset_index(inplace=True)

for year in range(1989, 2023):
    start_year = year - 14  # Start of the 15-year window
    end_year = year
    # Select data for the 15-year window
    mask = (pricedata['year'] >= start_year) & (pricedata['year'] <= end_year) & pricedata['permno'].isin(unique_permnos)
    data_window = pricedata.loc[mask]
    
    # Drop firms with more than 5 years of missing data within the window
    counts = data_window.groupby('permno')['ret'].apply(lambda x: x.isna().sum())
    firms_with_enough_data = counts[counts <= 5].index
    data_window = data_window[data_window['permno'].isin(firms_with_enough_data)]
    
    # Calculate the covariance matrix
    returns = data_window.pivot_table(index='date', columns='permno', values='ret')
    cov_matrix = returns.cov()
    
    # Find the MVP weights
    mvp_weights = find_mvp_weights(cov_matrix)
    
    # Set very small weights to zero
    mvp_weights[np.abs(mvp_weights) < 1e-6] = 0

    # Add the weights to the portfolio_weights DataFrame
    weights_df = pd.DataFrame({
        'permno': cov_matrix.columns,
        'weight': mvp_weights,
        'year': year + 1  # This portfolio will be invested in the next year
    })
    portfolio_weights = pd.concat([portfolio_weights, weights_df], ignore_index=True)

# Merge the portfolio weights back into the original data set
pricedata = pricedata.merge(portfolio_weights, on=['permno', 'year'], how='left')

# Print the head of the updated pricedata to verify the merge was successful
print(pricedata.head())
#%%


"""
5. Now we need to actually track the porOolio returns over >me. No>ce that while we have
already calculated the ini+al porOolio weights, those weights will change from month to
month within each year, and we need to keep this in mind.
• To start, create a groupby object by year with your main data.
• Use a for loop to loop through each year. Within each loop, use the
get_group() method to access the data for that year
• Using weights and individual asset returns, calculate the porOolio return for each
month
i. remember that the weights will change from month to month!
ii. You will want to loop through months to do this

iii. You might have a firm drop from the sample between months. Think
about what this means? How should you handle it?
"""



"""
6. Lastly, plot your result! Time should be on the x-axis, with your porOolio’s cumula+ve
return for each period on the y-axis. DataFrame.plot() should make this predy
straighOorward. Also, pickle your porOolio data! Use the to_pickle() method of
Pandas so we can reuse it next week.
"""
