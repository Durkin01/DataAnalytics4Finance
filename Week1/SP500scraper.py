# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 12:48:48 2023

@author: swebb
"""

def get_SP500_list():
    import pandas as pd
    import wikipedia as wp
    
    
    wiki = "List of S&P 500 companies"
    html = wp.page(title=wiki).html().encode('UTF-8')
    table = pd.read_html(html)[0]
    table.head()
    return table
