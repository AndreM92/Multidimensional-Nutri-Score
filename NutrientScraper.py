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

import os
import time
import openpyxl


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
foods = ['Banane','Broccoli','Vollei']

# Imported list of foods (os Module and the full path are optional)
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
    links = [l['href'] for l in soup.find_all('a', href=True) if food.lower() in l['href'].lower()]

    return links

def select(links):
    # I standardize the information to 100g per food item
    quantity = '?menge=100'
    if len(links) >= 1:
        # inspect the first entry
        link = startpage + links[0] + quantity
        driver.get(link)

# Test:
# food = foods[2]
# links = searchFood(food)
# select (links)


# Make sure that the page is completely open
def openPage():
    name = ''
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(('xpath','//*[@id="main"]/div/header/h2')))
    # additional sleeptime
    time.sleep(1)
    name = driver.find_element('xpath','//*[@id="main"]/div/header/h2').text
    openpage = driver.find_element('xpath', '//a[contains(text(), "Weiterlesen")]')
    scrheight = driver.execute_script('return document.body.scrollHeight')
    if scrheight > 10000:
        pass
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

# Test:
# name = openPage()


# Scrape the data
def getData(food):
    data = [['food', food]]
    header,columns = ['' for i in range(2)]
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    tables = soup.find_all('table', class_='alt nwdetails')
    if len(tables) >= 1:
        for t in tables:
            rows = t.find_all('tr')
            f_rows = [r for r in rows if not 'Tagesbedarf' in r.text and not 'Richtwert' in r.text]
            columns = [[c.text.strip() for c in r.find_all('td')[:2]] for r in f_rows]
            f_columns = [e for e in columns if len(e) > 1]
            data.extend(f_columns)

    return data

# Test:
# ftable = getData(foods[2])
# for t in ftable:
#     print(t)

########################################################################################################################
# A loop function to scrape the nutrients for every food in the list
def scrapeFoodList(foods):
    foodDict = {}
    header = ''
    for food in foods:
        foodID = foods.index(food)
        links = searchFood(food)
        select(links)
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

    return foodDict

# To run this function
foodDict = scrapeFoodList(foods)

########################################################################################################################
# But I rather recommend to scrape every page manually to get the specific food you are looking for and to avoid errors
def scrapeSingleFood(foodDict, header, food):
    name = openPage()
    nutrients = getData(food)
    if header == '':
        header = [d[0] for d in nutrients[1:]]
        for h in header:
            foodDict[h] = []
    foodID = len(foodDict['ID'])
    foodDict['ID'].append(foodID)
    foodDict['food'].append(nutrients[0][1])
    foodDict['label'].append(name)
    for f in foodDict:
        if f in header:
            col = header.index(f) +1
            foodDict[f].append(nutrients[col][1])

    return foodDict,header


# Data setup
foodDict = {'ID': [], 'food': [], 'label': []}
header = ''

# Follow these steps for every food
# 1. Search for a specific food:
food = 'Vollei'
links = searchFood(food)
# 2. Click on the result you prefer
# 3. Open the page and scrape the data
foodDict,header = scrapeSingleFood(foodDict, header, food)

for index, value in enumerate(foodDict):
    if index < 10:
        print(f'{index} {value} {foodDict[value]}')
# print(foodDict)

########################################################################################################################
# When you are done with scraping
# A quick check if the length of the rows are consistent
def checkDictFormat():
    lenDict = len(foodDict['ID'])
    for index, value in enumerate(foodDict):
        if lenDict != len(foodDict[value]):
            print(f'{index} {value} {foodDict[value]}')
        else:
            return True

# checkDictFormat()

# Transform the Dictionary to a DataFrame
if checkDictFormat():
    dfNutrientsTable = pd.DataFrame(foodDict)
# print(dfNutrientsTable)


# Quicksave without additional Modules
dfNutrientsTable.to_pickle('Table.pkl')
# Reopen
dfNutrientsTable = pd.read_pickle('Table.pkl')


# Export the DataFrame to Excel
path = os.getcwd() + '/Multidimensional-Nutri-Score'
with pd.ExcelWriter(path + '/NutrientsData.xlsx') as writer:
    dfNutrientsTable.to_excel(writer, sheet_name='Nutrients')