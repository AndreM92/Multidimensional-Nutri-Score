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