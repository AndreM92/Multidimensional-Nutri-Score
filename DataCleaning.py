import numpy as np
import pandas as pd
from sqlalchemy import create_engine

import os
if 'path' in globals():
    del path
path = os.getcwd() + '/Multidimensional-Nutri-Score'
# + '/Multidimensional-Nutri-Score'


# Table of uncleaned nutritional information
dfNutrientsTable = pd.read_excel(path + '/NutrientsData.xlsx', sheet_name='Nutrients')
dfNutrientsTable = dfNutrientsTable.drop(['Unnamed: 0'], axis=1)

# Empty DataFrame with just the ID's and names ant the calories of the foods
dfEmpty = dfNutrientsTable.loc[:,['ID','food']]
dfEmpty.set_index('ID', inplace=True)
dfEmpty['kcal'] = dfNutrientsTable['Energie (kcal)'].str.replace(' kcal', '').str.replace(',','.').astype(float)

# DataFrame with vitamin informations
dfVitamins = dfEmpty
dfVitamins = dfNutrientsTable.loc[:, 'Vitamin A Retinoläquivalent':'Vitamin K']

# Check if the values of the vitamins are in the right units and convert them to float data types
# Extract the digits from each value with a regular expression and just return a series of extracted values.
vitcols = dfNutrientsTable.loc[:, 'Vitamin A Retinoläquivalent':'Vitamin K'].columns
for c in vitcols:
    dfVitamins['unit'] = [1000 if 'mg' in u else 1 for u in dfVitamins[c]]
    dfVitamins[c] = dfVitamins[c].str.extract(r'(\d+\.?\d*)', expand=False)
    dfVitamins[c] = dfVitamins[c].str.replace('.', '', regex=True).str.replace(',', '.', regex=True).astype(float)
    dfVitamins[c] = dfVitamins[c] * dfVitamins['unit']
dfVitamins.drop(['unit'], axis=1, inplace=True)

# Shorten the column names
dfVitamins = dfVitamins[vitcols].rename(columns=lambda c: c.replace('Vitamin ', '', 1).strip() + ' (µg)')

# Fill in the missing nutritional contents and convert different types of vitamins
dfVitamins['A Retinol (µg)'] = dfVitamins['A Retinol (µg)'].where(dfVitamins['A Retinol (µg)'] > 1,dfVitamins['A Retinoläquivalent (µg)'])
dfVitamins['A Retinol (µg)'] = dfVitamins['A Retinol (µg)'] + dfVitamins['A Beta-Carotin (µg)']/12
dfVitamins['A Retinol (µg)'] = dfVitamins['A Retinol (µg)'].round(1)
dfVitamins = dfVitamins.drop(['A Retinoläquivalent (µg)', 'A Beta-Carotin (µg)'],axis=1)

dfVitamins['B3 Niacin, Nicotinsäure (µg)'] = dfVitamins['B3 Niacin, Nicotinsäure (µg)'].where \
    (dfVitamins['B3 Niacin, Nicotinsäure (µg)'] > (dfVitamins['B3 Niacinäquivalent (µg)']/17*15),(dfVitamins['B3 Niacinäquivalent (µg)']/17*15))
dfVitamins['B3 Niacin, Nicotinsäure (µg)'] = dfVitamins['B3 Niacin, Nicotinsäure (µg)'].round(1)
dfVitamins = dfVitamins.drop(['B3 Niacinäquivalent (µg)'],axis=1)


# DataFrame for food with information on vitamin content per 100 grams
dfVitVolume = pd.concat([dfEmpty,dfVitamins], axis=1)
# print(dfVitVolume)

# DataFrame for food with information on vitamin content per 100 kcal
dfVitEnergy = dfVitamins.copy()
dfVitEnergy['grams'] = 100
dfVitEnergy = dfVitEnergy.div(dfEmpty['kcal'], axis=0) * 100
dfVitEnergy = pd.concat([dfEmpty[['food']],dfVitEnergy], axis=1)
# print(dfVitEnergy)


# Vitamin recommendations (filter the columns based on the selection of dfVitamins)
dfVitRec_full = pd.read_excel(path + '/DGE_recommendations.xlsx', sheet_name='avg_vitamins')
dfVitRec = dfVitRec_full.iloc[:1].copy()
selected_columns = dfVitamins.columns.tolist()
dfVitRec = dfVitRec.filter(items=selected_columns)
# print(dfVitRec)


# Calculate the percentage coverage of the requirements for each nutrient (Vitamin) based on food volume (100 grams)
dfVitPV = dfVitVolume.copy()
dfVitPV.iloc[:, 2:] = (dfVitPV.iloc[:, 2:] / (dfVitRec.iloc[0] + 0.001) * 100).applymap(lambda x: round(x, 2))
# print(dfVitPV)

# Calculate the percentage coverage of the requirements for each nutrient (Vitamin) based on energy density (100 kcal)
dfVitPE = dfVitEnergy.copy()
dfVitPE.drop('grams',axis=1,inplace=True)
dfVitPE.iloc[:, 1:] = (dfVitPE.iloc[:, 1:] / (dfVitRec.iloc[0] + 0.001) * 100).applymap(lambda x: round(x, 2))
# print(dfVitPE)


# Another shortening of the column names
dfVitPV.columns = dfVitPV.columns.str.split().str[0]
dfVitPE.columns = dfVitPE.columns.str.split().str[0]


# Inspect a single food
VitPV_liver = dfVitPV[dfVitPE['food'] == 'Rinderleber'].reset_index()
VitPE_liver = dfVitPE[dfVitPE['food'] == 'Rinderleber'].reset_index()
print(VitPV_liver.loc[0])
print(VitPE_liver.loc[0])


# To see the entire results in Excel
dfVitamins = pd.concat([dfEmpty[['food']],dfVitamins], axis=1)
with pd.ExcelWriter(path + '/CleanedData.xlsx') as writer:
    dfVitamins.to_excel(writer, sheet_name='Vitamins')
    dfVitPV.to_excel(writer, sheet_name='VitaminCovVol')
    dfVitPE.to_excel(writer, sheet_name='VitaminCovEnerg')

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

########################################################################################################################
# Calculate the Score to which the need for vitamins (in 100 grams of food) is covered in percentage
dfVitP = pd.read_excel(path + '\CleanedData.xlsx', sheet_name='VitaminCovVol')
dfVitP['average'] = dfVitP.loc[:, 'A':'K'].mean(axis=1)




#dfNutrientsTable = pd.read_pickle('Table.pkl')
#import sqlalchemy
#print(sqlalchemy.__version__)
# SQL Table directory
# C:/Users/andre/Documents/SQL

# Throws a warning message:
# dfVitP['average'] = dfVitP.mean(axis=1)
# dfVitP.drop('average', axis=1, inplace=True)