import numpy as np
import pandas as pd
from sqlalchemy import create_engine

import os
if 'my_path' in globals():
    del my_path
my_path = os.getcwd() + '/Multidimensional-Nutri-Score'
# + '/Multidimensional-Nutri-Score'


# Table of uncleaned nutritional information
dfNutrientsTable = pd.read_excel(my_path + '/NutrientsData.xlsx', sheet_name='Nutrients')
dfNutrientsTable = dfNutrientsTable.drop(['Unnamed: 0'], axis=1)

# Empty DataFrame with just the ID's and names and the calories of the foods
dfEmpty = dfNutrientsTable.loc[:,['ID','food']]
dfEmpty.set_index('ID', inplace=True)
dfEmpty['kcal'] = dfNutrientsTable['Energie (kcal)'].str.replace(' kcal', '').str.replace(',','.').astype(float)

########################################################################################################################
# DataFrame with vitamin information
dfVitamins = dfEmpty.copy()
dfVitamins = dfNutrientsTable.loc[:, 'Vitamin A Retinoläquivalent':'Vitamin K']

# Check if the values of the vitamins are in the right units and convert them to float data types
# Extract the digits from each value with a regular expression and just return a series of extracted values.
for c in dfVitamins.columns:
    dfVitamins['unit'] = [1000 if 'mg' in u else 1 for u in dfVitamins[c]]
    dfVitamins[c] = dfVitamins[c].str.extract(r'(\d*\.?\d*\,?\d*)', expand=False)
    dfVitamins[c] = dfVitamins[c].str.replace('.', '', regex=True).str.replace(',', '.', regex=True).astype(float)
    dfVitamins[c] = dfVitamins[c] * dfVitamins['unit']
dfVitamins.drop(['unit'], axis=1, inplace=True)

# Shorten the column names
dfVitamins.rename(columns=lambda c: c.replace('Vitamin ', '', 1).strip() + ' (µg)', inplace=True)

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
#print(dfVitVolume)

# DataFrame for food with information on vitamin content per 100 kcal
dfVitEnergy = dfVitamins.copy()
dfVitEnergy['grams'] = 100
dfVitEnergy = dfVitEnergy.div(dfEmpty['kcal'], axis=0) * 100
dfVitEnergy = pd.concat([dfEmpty[['food']],dfVitEnergy], axis=1)
#print(dfVitEnergy)

# Vitamin recommendations (filter the columns based on the selection of dfVitamins)
dfVitRec_full = pd.read_excel(my_path + '/DGE_recommendations.xlsx', sheet_name='avg_vitamins')
dfVitRec = dfVitRec_full.iloc[1:2].copy()
selected_columns = dfVitamins.columns.tolist()
dfVitRec = dfVitRec.filter(items=selected_columns)
#print(dfVitRec)


# Calculate the percentage coverage of the requirements for each nutrient (Vitamin) based on food volume (100 grams)
dfVitPV = dfVitVolume.copy()
dfVitPV.iloc[:, 2:] = (dfVitPV.iloc[:, 2:] / (dfVitRec.iloc[0] + 0.001) * 100).applymap(lambda x: round(x, 2))
#print(dfVitPV)

# Calculate the percentage coverage of the requirements for each nutrient (Vitamin) based on energy density (100 kcal)
dfVitPE = dfVitEnergy.copy()
dfVitPE.drop('grams',axis=1,inplace=True)
dfVitPE.iloc[:, 1:] = (dfVitPE.iloc[:, 1:] / (dfVitRec.iloc[0] + 0.001) * 100).applymap(lambda x: round(x, 2))
#print(dfVitPE)

# Another shortening of the column names
dfVitPV.columns = dfVitPV.columns.str.split().str[0]
dfVitPE.columns = dfVitPE.columns.str.split().str[0]

# Calculate the Score to which the need for vitamins is covered in percentage
#dfVitPV = pd.read_excel(my_path + '\CleanedData.xlsx', sheet_name='VitaminCovVol').drop('Unnamed: 0', axis=1)
#dfVitPE = pd.read_excel(my_path + '\CleanedData.xlsx', sheet_name='VitaminCovEnerg').drop('Unnamed: 0', axis=1)
# For each 100 grams of the food
dfVitPV['average'] = dfVitPV.loc[:, 'A':'K'].mean(axis=1)
dfVitPVOrder = dfVitPV[['food', 'average']].sort_values('average', ascending=False)
print(dfVitPVOrder)
# For each 100 kcal of the food
dfVitPE['average'] = dfVitPE.loc[:, 'A':'K'].mean(axis=1)
dfVitPEOrder = dfVitPE[['food', 'average']].sort_values('average', ascending=False)
print(dfVitPEOrder)


# Example:
# Inspect a single food
VitPV_liver = dfVitPV[dfVitPE['food'] == 'Rinderleber'].reset_index()
VitPE_liver = dfVitPE[dfVitPE['food'] == 'Rinderleber'].reset_index()
print(VitPV_liver.loc[0])
print(VitPE_liver.loc[0])

########################################################################################################################
# DataFrame with mineral information (including trace minerals in µg)
dfMinerals = dfEmpty.copy()
dfMinerals = dfNutrientsTable.loc[:, 'Natrium':'Schwefel']
dfTrMinerals = dfNutrientsTable.loc[:, 'Eisen':'Iodid']

# Mineral recommendations (filter the columns based on the selection of dfMinerals and dfTrMinerals)
# Note: The bioavailability of minerals is still neglected
dfMrRec_full = pd.read_excel(my_path + '/DGE_recommendations.xlsx', sheet_name='avg_minerals')
dfMrRec = dfMrRec_full.iloc[1:2].copy()
dfTrMrRec_full = pd.read_excel(my_path + '/DGE_recommendations.xlsx', sheet_name='avg_trminerals')
dfTrMrRec = dfTrMrRec_full.iloc[1:2].copy()

mr_columns = dfMinerals.columns.tolist()
dfMrRec = dfMrRec.filter(items=mr_columns).astype(float)
trmr_columns = dfTrMinerals.columns.tolist()
dfTrMrRec = dfTrMrRec.filter(items=trmr_columns)
print(dfMrRec)
print(dfTrMrRec)

# Check if the values of the minerals and trace minerals are in the right units and convert them to float data types
# Extract the digits from each value with a regular expression and just return a series of extracted values.
for c in mr_columns:
    dfMinerals['unitmg'] = [1 if 'mg' in u else 0.001 for u in dfMinerals[c]]
    dfMinerals[c] = dfMinerals[c].str.extract(r'(\d*\.?\d*\,?\d*)', expand=False)
    dfMinerals[c] = dfMinerals[c].str.replace('.', '', regex=True).str.replace(',', '.', regex=True).astype(float)
    dfMinerals[c] = dfMinerals[c] * dfMinerals['unitmg']
dfMinerals.drop(['unitmg'], axis=1, inplace=True)

for c in trmr_columns:
    dfTrMinerals['unitug'] = [1000 if 'mg' in u else 1 for u in dfTrMinerals[c]]
    dfTrMinerals[c] = dfTrMinerals[c].str.extract(r'(\d*\.?\d*\,?\d*)', expand=False)
    dfTrMinerals[c] = dfTrMinerals[c].str.replace('.', '', regex=True).str.replace(',', '.', regex=True).astype(float)
    dfTrMinerals[c] = dfTrMinerals[c] * dfTrMinerals['unitug']
dfTrMinerals.drop(['unitug'], axis=1, inplace=True)

# DataFrame for food with information on mineral content per 100 grams
dfMrVol = pd.concat([dfEmpty,dfMinerals], axis=1)
dfTrMrVol = pd.concat([dfEmpty,dfTrMinerals], axis=1)

# DataFrame for food with information on mineral content per 100 kcal
dfMrEnergy = dfMinerals.copy()
dfMrEnergy['grams'] = 100
dfMrEnergy = dfMrEnergy.div(dfEmpty['kcal'], axis=0) * 100
dfMrEnergy = pd.concat([dfEmpty[['food']],dfMrEnergy], axis=1)
dfTrMrEnergy = dfTrMinerals.copy()
dfTrMrEnergy['grams'] = 100
dfTrMrEnergy = dfTrMrEnergy.div(dfEmpty['kcal'], axis=0) * 100
dfTrMrEnergy = pd.concat([dfEmpty[['food']],dfTrMrEnergy], axis=1)

# Calculate the percentage coverage of the requirements for each nutrient (mineral) based on food volume (100 grams)
dfMrPV = dfMrVol.copy()
dfMrPV.iloc[:, 2:] = (dfMrPV.iloc[:, 2:] / (dfMrRec.iloc[0] + 0.001) * 100).applymap(lambda x: round(x, 2))
# No requirements for sulfur available
dfMrPV.drop('Schwefel',axis=1,inplace=True)
print(dfMrPV)

# Calculate the percentage coverage of the requirements for each nutrient (mineral) based on energy density (100 kcal)
dfMrPE = dfMrEnergy.copy()
dfMrPE.drop('grams',axis=1,inplace=True)
dfMrPE.iloc[:, 1:] = (dfMrPE.iloc[:, 1:] / (dfMrRec.iloc[0] + 0.001) * 100).applymap(lambda x: round(x, 2))
# No requirements for sulfur available
dfMrPE.drop('Schwefel',axis=1,inplace=True)
print(dfMrPE)

# Calculate the percentage coverage of the requirements for each nutrient (tracemineral) based on food volume (100 grams)
dfTrMrPV = dfTrMrVol.copy()
dfTrMrPV.iloc[:, 2:] = (dfTrMrPV.iloc[:, 2:] / (dfTrMrRec.iloc[0] + 0.001) * 100).applymap(lambda x: round(x, 2))
print(dfTrMrPV)

# Calculate the percentage coverage of the requirements for each nutrient (tracemineral) based on energy density (100 kcal)
dfTrMrPE = dfTrMrEnergy.copy()
dfTrMrPE.drop('grams',axis=1,inplace=True)
dfTrMrPE.iloc[:, 1:] = (dfTrMrPE.iloc[:, 1:] / (dfTrMrRec.iloc[0] + 0.001) * 100).applymap(lambda x: round(x, 2))
print(dfTrMrPE)


# Calculate the Score to which the need for minerals is covered in percentage
# For each 100 grams of the food
dfMrPV['average'] = dfMrPV.loc[:, 'Natrium':'Chlorid'].mean(axis=1)
dfMrPVOrder = dfMrPV[['food', 'average']].sort_values('average', ascending=False)
print(dfMrPVOrder)
# For each 100 kcal of the food
dfMrPE['average'] = dfMrPE.loc[:, 'Natrium':'Chlorid'].mean(axis=1)
dfMrPEOrder = dfMrPE[['food', 'average']].sort_values('average', ascending=False)
print(dfMrPEOrder)

# Calculate the Score to which the need for traceminerals is covered in percentage
# For each 100 grams of the food
dfTrMrPV['average'] = dfTrMrPV.loc[:,'Eisen':'Iodid'].mean(axis=1)
dfTrMrPVOrder = dfTrMrPV[['food', 'average']].sort_values('average',ascending=False)
print(dfTrMrPVOrder)
# For each 100 kcal of the food
dfTrMrPE['average'] = dfTrMrPE.loc[:,'Eisen':'Iodid'].mean(axis=1)
dfTrMrPEOrder = dfTrMrPE[['food', 'average']].sort_values('average',ascending=False)
print(dfTrMrPEOrder)


# Calculate the full Score of nutrient coverage by energy(vitamins,minerals,trace minerals)
dfNrCovPE = pd.concat([dfVitPE.loc[:, :'K'], dfMrPE.loc[:, 'Natrium':'Chlorid'], dfTrMrPE.loc[:, 'Eisen':'Iodid']], axis=1)
dfNrCovPE['average'] = dfNrCovPE.loc[:,'A':].mean(axis=1)
print(dfNrCovPE)

########################################################################################################################
# To see the entire results in Excel
with pd.ExcelWriter(my_path + '/Nutrient_coverage_by_volume.xlsx') as writer:
    dfVitPV.to_excel(writer,sheet_name='Vitamins')
    dfMrPV.to_excel(writer,sheet_name='Minerals')
    dfTrMrPV.to_excel(writer,sheet_name='Traceminerals')

with pd.ExcelWriter(my_path + '/Nutrient_coverage_by_energy.xlsx') as writer:
    dfVitPE.to_excel(writer,sheet_name='Vitamins')
    dfMrPE.to_excel(writer,sheet_name='Minerals')
    dfTrMrPE.to_excel(writer,sheet_name='Traceminerals')
    dfNrCovPE.to_excel(writer,sheet_name='Full_Score')

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





#dfNutrientsTable = pd.read_pickle('Table.pkl')
#import sqlalchemy
#print(sqlalchemy.__version__)
# SQL Table directory
# C:/Users/andre/Documents/SQL

# Throws a warning message:
# dfVitP['average'] = dfVitP.mean(axis=1)
# dfVitP.drop('average', axis=1, inplace=True)