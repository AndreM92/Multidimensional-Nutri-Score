import numpy as np
import pandas as pd
from sqlalchemy import create_engine

import os
if 'path' in globals():
    del path
path = os.getcwd()
# + '/Multidimensional-Nutri-Score'


# Table of uncleaned nutritional information
dfNutrientsTable = pd.read_excel(path + '/NutrientsData.xlsx', sheet_name='Nutrients')
dfNutrientsTable = dfNutrientsTable.drop(['Unnamed: 0'], axis=1)

# Empty DataFrame with just the ID's and names of the foods
dfEmpty = dfNutrientsTable.loc[:,['ID','food']]
dfEmpty.set_index('ID', inplace=True)

# New DataFrame for Vitamins
colnames = dfNutrientsTable.columns[15:31]
dfVitamins = dfEmpty
# Insert every entry of the category
for c in colnames:
    # Delete the first occurence of "Vitamin" in the name
    header = c.replace('Vitamin ','',1).strip() + ' (µg)'
    dfVitamins[header] = dfNutrientsTable[c]

# Check if the values are in the right units and convert them to float data types
dfVitStr = dfVitamins.astype(str)
new_colnames = dfVitamins.columns[1:]
for n in new_colnames:
    dfVitStr[n] = [float(e.split(' ')[0].replace('.','').replace(',', '.')) * 1000 if 'mg' in e \
                         else float(e.split(' ')[0].replace('.','').replace(',','.')) for e in dfVitStr[n]]
    dfVitamins[n] = dfVitStr[n].astype(float)

# Fill in the missing nutritional contents and convert different types of vitamins
dfVitamins['A Retinol (µg)'] = dfVitamins['A Retinol (µg)'].where(dfVitamins['A Retinol (µg)'] > 1,dfVitamins['A Retinoläquivalent (µg)'])
dfVitamins['A Retinol (µg)'] = dfVitamins['A Retinol (µg)'] + dfVitamins['A Beta-Carotin (µg)']/12
dfVitamins['A Retinol (µg)'] = dfVitamins['A Retinol (µg)'].round(1)
dfVitamins = dfVitamins.drop(['A Retinoläquivalent (µg)', 'A Beta-Carotin (µg)'],axis=1)

dfVitamins['B3 Niacin, Nicotinsäure (µg)'] = dfVitamins['B3 Niacin, Nicotinsäure (µg)'].where \
    (dfVitamins['B3 Niacin, Nicotinsäure (µg)'] > (dfVitamins['B3 Niacinäquivalent (µg)']/17*15),(dfVitamins['B3 Niacinäquivalent (µg)']/17*15))
dfVitamins['B3 Niacin, Nicotinsäure (µg)'] = dfVitamins['B3 Niacin, Nicotinsäure (µg)'].round(1)
dfVitamins = dfVitamins.drop(['B3 Niacinäquivalent (µg)'],axis=1)
print(dfVitamins)


# Vitamin recommendations
dfVitRec_full = pd.read_excel(path + '/DGE_recommendations.xlsx', sheet_name='avg_vitamins')
dfVitRec = dfVitRec_full.iloc[:1].copy()
dfVitRec.columns = ['Population', *dfVitRec_full.columns[1:]]
dfVitRec['Population'] = 'average'
print(dfVitRec)

# Calculate the percentage coverage of the requirements for each nutrient (Vitamin)
dfVitP = dfVitamins.copy()
vitcol = dfVitamins.columns[1:]
for c in vitcol:
    dfVitP[c] = (dfVitamins[c] / dfVitRec[c].loc[0] * 100).round(2)
dfVitP.columns = ['food'] + [n.split()[0] for n in dfVitamins.columns[1:]]
print(dfVitP)

# Second version, same result
dfVit2 = dfVitamins.loc[:,['food']]
for c in vitcol:
    colname = c.split()[0]
    dfVit2 = dfVit2.assign(**{colname: lambda x : round((dfVitamins[c] / dfVitRec[c].loc[0]) * 100,2)})
print(dfVit2)


# Inspect a single food
VitP_liver = dfVitP[dfVitP['food'] == 'Rinderleber'].reset_index()
print(VitP_liver.loc[0])


# To see the entire results in Excel
with pd.ExcelWriter(path + '/CleanedData.xlsx') as writer:
    dfVitamins.to_excel(writer, sheet_name='Vitamins')
    dfVitP.to_excel(writer, sheet_name='VitaminCoverage')

########################################################################################################################
# Export to PostgreSQL
database = 'Multidimensional-Nutri-Score'
path2 = r'C:\Users\andre\OneDrive\Desktop\IT-Projekte\Multidimensional_Nutri-Score\\'
with open (path2 + 'SQL_login.txt','r') as file:
    password, username = file.read().split()

# Connect to the database
address = f'postgresql://{username}:{password}@localhost:5432/{database}'
engine = create_engine(address)

# Export the nutritional information for the vitamins
table_name = 'nut_vitamins'
dfVitamins.to_sql(table_name, con=engine, if_exists='replace', index=False)

# Export the nutritional recommendations for the vitamins
table_name = 'recom_vitamins'
dfVitRec.to_sql(table_name, con=engine, if_exists='replace', index=False)


#dfNutrientsTable = pd.read_pickle('Table.pkl')
#import sqlalchemy
#print(sqlalchemy.__version__)
# SQL Table directory
# C:/Users/andre/Documents/SQL