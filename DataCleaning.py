import numpy as np
import pandas as pd
import openpyxl

import os
path = os.getcwd() + '/Multidimensional-Nutri-Score'


# Table of uncleaned nutritional information
dfNutrientsTable = pd.read_excel(path + '/NutrientsData.xlsx', sheet_name='Nutrients')
dfNutrientsTable = dfNutrientsTable.drop(['Unnamed: 0'], axis=1)

# New DataFrame for Vitamins
colnames = dfNutrientsTable.columns[15:31]
# Empty DataFrame
dfVitamins = dfNutrientsTable.loc[:,['ID','food','label']]
# Insert every entry of the category
for c in colnames:
    # Delete the first occurence of "Vitamin" in the name
    header = c.replace('Vitamin ','',1).strip() + ' (µg)'
    dfVitamins[header] = dfNutrientsTable[c]

# Check if the values are in the right units and convert them to float data types
dfVitStr = dfVitamins.astype(str)
new_colnames = dfVitamins.columns[3:]
for n in new_colnames:
    dfVitStr[n] = [float(e.split(' ')[0].replace('.','').replace(',', '.')) * 1000 if 'mg' in e \
                         else float(e.split(' ')[0].replace('.','').replace(',','.')) for e in dfVitStr[n]]
    dfVitamins[n] = dfVitStr[n].astype(float)

print(dfVitamins)

# To see the entire results
with pd.ExcelWriter(path + '/CleanedData.xlsx') as writer:
    dfVitamins.to_excel(writer, sheet_name='Vitamins')


# Vitamin recommendations
df_v_rec = pd.read_excel(path + '/DGE_recommendations.xlsx', sheet_name='avg_vitamins')
print(df_v_rec[:2])

dfNutrientsTable = pd.read_pickle('Table.pkl')
print(dfNutrientsTable)