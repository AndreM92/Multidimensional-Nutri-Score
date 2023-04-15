from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import *
import time

import requests
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd


# Defining the startpage of Nährwertrechner.de
startpage = r'https://www.naehrwertrechner.de/'

# Driver and website setup
driver = webdriver.Chrome(r"C:\Users\andre\Documents\Python\chromedriver.exe")
driver.maximize_window()
driver.get(startpage)
time.sleep(3)

# Cookie banner
if driver.find_element('xpath', '/html/body/iframe[1]'):
    driver.find_element(By.CLASS_NAME, 'fc-button-label').click()

########################################################################################################################
# List of foods
foods = ['Banane','Broccoli','Ei']

# Imported list of foods (os Module and the full path are optional)
import os
path = os.getcwd() + '/Multidimensional-Nutri-Score/'
# print(os.listdir(path))
with open (path + 'foodlistexample.txt', 'r') as file:
    foods = file.read().split()


# Searching process
def searchFood(food):
    driver.get(startpage)
    se_xp = '//*[@id="one"]/div/div/div[1]/form/div/div[1]/input'
    WebDriverWait(driver,5).until(EC.presence_of_element_located(('xpath',se_xp)))
    searchbox = driver.find_element('xpath',se_xp)
    searchbox.click()
    searchbox.send_keys(Keys.BACKSPACE)
    searchbox.send_keys(food)
    searchbox.send_keys(Keys.ENTER)
    WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'box')))
    soup = BeautifulSoup(driver.page_source,'html.parser')
    links = [l['href'] for l in soup.find_all('a',href=True) if food.lower() in l['href'].lower()]

    # I standardize the information to 100g per food item
    quantity = '?menge=100'
    if len(links) >= 1:
        # inspect the first entry
        link = startpage + links[0] + quantity
        driver.get(link)

# food = foods[0]
# searchFood(food)

# Make sure that the page is completely open
def openPage():
    name = ''
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(('xpath','//*[@id="main"]/div/header/h2')))
    # additional sleeptime
    time.sleep(1)
    name = driver.find_element('xpath','//*[@id="main"]/div/header/h2').text
    openpage = driver.find_element('xpath', '//a[contains(text(), "Weiterlesen")]')
    scrheight = driver.execute_script('return document.body.scrollHeight')
    if openpage:
        try:
            openpage.click()
        except:
            driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            try:
                openpage.click()
            except:
                pass
    if scrheight == driver.execute_script('return document.body.scrollHeight'):
        time.sleep(1)
        try:
            openpage.click()
        except:
            try:
                driver.find_elements(By.CLASS_NAME, 'tbl-read-more-btn').click()
            except:
                pass
        # scroll down
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')

    return name

# name = openPage()


# Scrape the data
def getData(food):
    data = [['food', food]]
    header,columns = ['' for i in range(2)]
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    tables = soup.find_all('table',class_='alt nwdetails')
    if len(tables) >= 1:
        for t in tables:
            rows = t.find_all('tr')
            f_rows = [r for r in rows if not 'Tagesbedarf' in r.text and not 'Richtwert' in r.text]
            columns = [[c.text.strip() for c in r.find_all('td')[:2]] for r in f_rows]
            f_columns = [e for e in columns if len(e) > 1]
            data.extend(f_columns)

    return data

# ftable = getData(food)
# for t in ftable:
#     print(t)


# A loop to scrape the nutrients for every food in the list
foodDict = {}
header = ''

for food in foods:
    foodID = foods.index(food)
    searchFood(food)
    name = openPage()
    nutrients = getData(food)
    if header == '':
        header = [d[0] for d in nutrients[1:]]
    if len(foodDict) == 0:
        foodDict = {'ID':[], 'food':[], 'entry':[]}
        for h in header:
            foodDict[h] = []
    foodDict['ID'].append(foodID)
    foodDict['food'].append(nutrients[0][1])
    foodDict['entry'].append(name)
    for f in foodDict:
        if f in header:
            col = header.index(f)
            foodDict[f].append(nutrients[col][1])

# print(foodDict)
# for f in foodDict:
#     print(foodDict[f])


# Transform the Dictionary to a DataFrame
df = pd.DataFrame(foodDict)
print(df)

########################################################################################################################
# Notes

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