import numpy as np
import pandas as pd
from sqlalchemy import create_engine

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

# To see the entire results in Excel
with pd.ExcelWriter(path + '/CleanedData.xlsx') as writer:
    dfVitamins.to_excel(writer, sheet_name='Vitamins')


# Vitamin recommendations
dfVitRec_full = pd.read_excel(path + '/DGE_recommendations.xlsx', sheet_name='avg_vitamins')
dfVitRec = dfVitRec_full.iloc[:1].copy()
dfVitRec.columns = ['Population', *dfVitRec_full.columns[1:]]
dfVitRec['Population'] = 'average'
print(dfVitRec)

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