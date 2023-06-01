# Test
nutrients = [['A',1],['B',5],['E',3]]

# A loop to scrape the nutrients for every food in the list
name = ['n']
header = ''
foodDict = {}

for food in foods:
    foodID = foods.index(food)
#    searchFood(food)
#    name = openpage()
#    nutrients = getData(food,name)
    if header == '':
        header = [d[0] for d in nutrients]
    if len(foodDict) == 0:
        foodDict = {'ID':[], 'food':[], 'entry':[]}
        for h in header:
            foodDict[h] = []
    foodDict['ID'].append(foodID)
    foodDict['food'].append(food)
    foodDict['entry'].append(name)
    for h in header:
        col = header.index(h)
        if nutrients[col][0] in h:
            foodDict[h].append(nutrients[col][1])
        else:
            foodDict[h].append('NaN')
    nutrients = [['A', 1], ['D', 5], ['E', 3]]
print(foodDict)

# create a DataFrame
header = ['food'] + [d[0] for d in data]
amount = [name] + [d[1] for d in data]
# Empty DataFrame
df = pd.DataFrame(columns=header)
# As long as I only have one or a few lines of data, I'm using this command:
df.loc[len(df)] = amount
print(df)

#df = pd.DataFrame(data,columns=header)

# Vitamins
# Columns
for n in dfNutrientsTable.columns[15:31]:
    e = n.split(' ')[1:]
    print(e[0]+" ("+' '.join(e[1:])+")")


###############
food = 'A'
data = [['food', food]]
soup = BeautifulSoup(driver.page_source,'html.parser')
tables = soup.find_all('table', class_='alt nwdetails')
t = tables[8]
rows = t.find_all('tr')
f_rows = [r for r in rows if not 'Tagesbedarf' in r.text and not 'Richtwert' in r.text]
columns = [[c.text.strip() for c in r.find_all('td')[:2]] for r in f_rows]
f_columns = [e for e in columns if len(e) > 1]
print(f_columns)

# The data should get extended by nested tables (separated by nutritional category)
data.extend([f_columns])

# tables = getData(food)
tables = data
macros,vitamins,minerals,traceminerals,carbs,aminos,fibre,omegafats,fats = tables
comptable = [macros,vitamins,minerals+traceminerals,carbs,aminos,fibre,omegafats+fats]
tablenames = ['macros','vitamins','minerals','carbs','aminos','fibre','fats']

########################################################################################################################
# Data cleaning
# Notes
dfVitamins['calc']= dfVitamins['E Tocopherole (µg)'] + dfVitamins['K (µg)']
print(dfVitamins['calc'])


dft = pd.DataFrame({
    'a':[0,0,2],
    'b':[0,1,3],
    'c':[5,2,0]})

dft.loc[dft['a'] < 0.1, 'a'] = np.nan
dft.loc[dft['b'] < 0.1, 'b'] = np.nan
dft['c'] = dft['c'] * 5

dft['f'] = dft['a'].combine_first(dft['b']).combine_first(dft['c'])
print(dft)

dft['f'] = dft['b'].where(dft['b'] < 1, dft['c'])
dft['a'] = dft['a'].where(dft['a'] >= 1, dft['b'])


# Earlier calculations of vitamin percentages
vitcol = dfVitamins.columns
for c in vitcol:
    dfVitP[c] = (dfVitamins[c] / dfVitRec[c].loc[0] * 100).round(2)
dfVitP.columns = ['food'] + [n.split()[0] for n in dfVitamins.columns[1:]]

# Second version, same result
dfVit2 = dfVitamins.loc[:,['food']]
for c in vitcol:
    colname = c.split()[0]
    dfVit2 = dfVit2.assign(**{colname: lambda x : round((dfVitamins[c] / dfVitRec[c].loc[0]) * 100,2)})
print(dfVit2)


# df['mean'] = df.iloc[:, 0:4].mean(axis=1)
# df['mean'] = df.iloc[:, [0,1,2,3,4].mean(axis=1)
# df["mean_odd_year"] = df.loc[:, ["Y1961","Y1963","Y1965"]].mean(axis = 1)


dfVitamins = pd.concat([dfEmpty[['food']],dfVitamins], axis=1)
with pd.ExcelWriter(my_path + '/CleanedData.xlsx') as writer:
    dfVitamins.to_excel(writer, sheet_name='Vitamins')
    dfVitPV.to_excel(writer, sheet_name='VitaminCovVol')
    dfVitPE.to_excel(writer, sheet_name='VitaminCovEnerg')