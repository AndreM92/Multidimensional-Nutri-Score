from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import *

import requests
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd


# Defining the startpage of Nährwertrechner.de
startpage = r'https://www.naehrwertrechner.de/'

# Driver setup
driver = webdriver.Chrome(r"C:\Users\andre\Documents\Python\chromedriver.exe")
driver.maximize_window()
driver.get(startpage)

########################################################################################################################
# List of foods
foods = ['Banane','Bitterschokolade','Rinderleber']
# I standardize the information to 100g per food item
quantity = '?menge=100'

# searchbox
se_xp = '//*[@id="one"]/div/div/div[1]/form/div/div[1]/input'
WebDriverWait(driver,5).until(EC.presence_of_element_located(('xpath',se_xp)))
searchbox = driver.find_element('xpath',se_xp)

# Inspection of a specific food
searchbox.click()
searchbox.send_keys(Keys.BACKSPACE)
searchbox.send_keys(foods[0])
searchbox.send_keys(Keys.ENTER)
# examination of the search results
elements = driver.find_elements(By.CLASS_NAME,'box')
print(elements)

food = foods[0]
soup = BeautifulSoup(driver.page_source,'html.parser')
links = [l['href'] for l in soup.find_all('a',href=True) if food in l['href']]
print(links)


# inspect the selected entry
link = startpage + links[0] + quantity
driver.get(link)
# scroll down and open the full page
driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
driver.find_element(By.CLASS_NAME,'tbl-read-more-btn').click()

# Scrape the page
soup = BeautifulSoup(driver.page_source,'html.parser')
tables = soup.find_all('table',class_='alt nwdetails')
#print(len(tables))

rows = tables[2].find_all('tr')
f_rows = [r for r in rows if not 'Tagesbedarf' in r.text]

columns = [[c.text for c in r.find_all('td')[:2]] for r in f_rows]
f_columns = [e for e in columns if len(e) > 1]

data = []
for t in tables:
    rows = t.find_all('tr')
    f_rows = [r for r in rows if not 'Tagesbedarf' in r.text and not 'Richtwert' in r.text]
    columns = [[c.text.strip() for c in r.find_all('td')[:2]] for r in f_rows]
    f_columns = [e for e in columns if len(e) > 1]
    data.extend(f_columns)

for d in data:
    print(d)
# print(data)


# Notes
########################################################################################################################
for r in f_rows:
    columns = [n.text.strip() if len(n.text.strip()) > 1 for n in r.find_all('td')[:2]]
    for c in columns:
        print(len(c))
    print(columns)
    nutrient, amount = [n.text.strip() for n in c.find_all('td')[:2]]
    print(nutrient)
    print(amount)

data = []
header = []
amount = []
for t in tables[1:3]:
    rows = t.find_all('tr')
    f_rows = [r for r in rows if not 'Tagesbedarf' in r.text]
    for r in rows:
        name, quant = [e.text.strip() for e in r.find_all('td')[:2]]
        header.extend(name)
        amount.extend(quant)
df = pd.DataFrame(columns = header, rows = amount)

