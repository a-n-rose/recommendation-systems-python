import sqlite3
import numpy as np
import pandas as pd

def get_years():
    '''Selects all years from database and returns only unique vals
    
    Returns
    -------
    list of ints
    '''
    msg = '''SELECT year FROM popularity '''
    years = c.execute(msg)
    years_df = pd.DataFrame(years, columns=['year'])
    years_unique = years_df['year'].unique()
    return years_unique

def get_all_data():
    msg = '''SELECT year_id, year, popularity, year_name_id FROM popularity'''
    popularity = c.execute(msg)
    pop_df = pd.DataFrame(popularity,
                          columns=['year_id','year','popularity', 'year_name_id'])
    return pop_df

def get_year_numnames_dict(year_list, data_df):
    year_numnames_dict = {}
    for year in year_list:
        x = data_df[data_df['year'] == year]['popularity'].sum()
        year_numnames_dict[year] = x
    return year_numnames_dict

# want to divide popularity with total values from 
# corresponding year

def sum_names_each_year(year_list):
    data = get_all_data()
    year_names_dict = get_year_numnames_dict(year_list, data)
    data['total_num_names'] = 0
    data['total_num_names'] = data['year'].apply(
        lambda x: year_names_dict[x])
    return data
    
#test.loc[test['YearBuilt']==test['YearRemodAdd'], 'RemodAdd'] = 0
    
def get_percentage(data_df):
    data_df['percent_pop'] = round(data_df['popularity'] / data_df['total_num_names'] * 100000,4)
    return data_df

def standardize_percent_pop(data_df):
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaler.fit_transform(data_df['percent_pop'].values.reshape(-1,1))
    return data_df
        
    
conn = sqlite3.connect('babynames_USA.db')
c = conn.cursor()

year_list = get_years()
numnames_df = sum_names_each_year(year_list)
numnames_df = get_percentage(numnames_df)
#print('max')
#print(max(year_percentage['popularity_percent']))
#print('min')
#print(min(year_percentage['popularity_percent']))
#print('mean')
#print(np.mean(year_percentage['popularity_percent']))
#print('median')
#print(np.median(year_percentage['popularity_percent']))

print(numnames_df.describe())
print(numnames_df.head())

#numnames_df = standardize_percent_pop(numnames_df)
#print(numnames_df.describe())
#print(numnames_df.head())
#print()
#for key, value in year_numnames_dict.items():
    #print(key, ' num names: ', value)

sql_df = pd.DataFrame()
sql_df['year_id'] = numnames_df['year_id']
sql_df['year'] = numnames_df['year']
sql_df['popularity'] = numnames_df['percent_pop']
sql_df['year_name_id'] = numnames_df['year_name_id'] 
print(sql_df.head())

sql_df.to_sql(name = 'popularity', 
              con = conn,
              if_exists='replace',
              index=False)

conn.close()


            #year_id          year    popularity  year_name_id  total_num_names   percent_pop
#count  1.957046e+06  1.957046e+06  1.957046e+06  1.957046e+06     1.957046e+06  1.957046e+06
#mean   9.785235e+05  1.975563e+03  1.796856e+02  2.894312e+04     3.258623e+06  7.102541e+00
#std    5.649507e+05  3.419121e+01  1.522804e+03  2.678628e+04     8.989608e+05  5.932904e+01
#min    1.000000e+00  1.880000e+03  5.000000e+00  1.000000e+00     1.926960e+05  1.190000e-01
#25%    4.892622e+05  1.952000e+03  7.000000e+00  5.452000e+03     3.143519e+06  2.028000e-01
#50%    9.785235e+05  1.985000e+03  1.200000e+01  2.253500e+04     3.639329e+06  3.828000e-01
#75%    1.467785e+06  2.004000e+03  3.200000e+01  4.575300e+04     3.778497e+06  1.217400e+00
#max    1.957046e+06  2.018000e+03  9.968900e+04  1.091730e+05     4.200022e+06  4.791944e+03
