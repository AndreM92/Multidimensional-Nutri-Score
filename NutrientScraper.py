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
foods = ['Banane','Broccoli','Ei','Rinderleber','Walnuss']
# I standardize the information to 100g per food item
quantity = '?menge=100'

# searching process
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
    elements = driver.find_elements(By.CLASS_NAME,'box')
    soup = BeautifulSoup(driver.page_source,'html.parser')
    links = [l['href'] for l in soup.find_all('a',href=True) if food.lower() in l['href'].lower()]
    if len(links) >= 1:
        # inspect the first entry
        link = startpage + links[0] + quantity
        driver.get(link)

food = foods[0]
searchFood(food)

# make sure that the page is completely open
def openpage():
    WebDriverWait(driver, 5).until(EC.presence_of_element_located(('xpath','//*[@id="main"]/div/header/h2')))
    name = driver.find_element('xpath','//*[@id="main"]/div/header/h2').text
    openpage = driver.find_elements(By.CLASS_NAME,'tbl-read-more-btn')
    if openpage:
        try:
            openpage[0].click()
        except:
            driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            openpage[0].click()
        # scroll down
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
    return name

name = openpage()

# scrape the data
def getData(food,name):
    data = []
    header,columns = ['' for i in range(2)]

    time.sleep(1)
    soup = BeautifulSoup(driver.page_source,'html.parser')
    tables = soup.find_all('table',class_='alt nwdetails')
    if len(tables) >= 1:
        rows = tables[2].find_all('tr')
        f_rows = [r for r in rows if not 'Tagesbedarf' in r.text]
        columns = [[c.text for c in r.find_all('td')[:2]] for r in f_rows]
        f_columns = [e for e in columns if len(e) > 1]

    for t in tables:
        rows = t.find_all('tr')
        f_rows = [r for r in rows if not 'Tagesbedarf' in r.text and not 'Richtwert' in r.text]
        columns = [[c.text.strip() for c in r.find_all('td')[:2]] for r in f_rows]
        f_columns = [e for e in columns if len(e) > 1]
        data.extend(f_columns)

    return data

data = getData(food,name)

for d in data:
    print(d)
# print(data)

# create a DataFrame
header = ['food'] + [d[0] for d in data]
amount = [name] + [d[1] for d in data]
# Empty DataFrame
df = pd.DataFrame(columns=header)
# As long as I only have one or a few lines of data, I'm using this command:
df.loc[len(df)] = amount
print(df)


# Notes
########################################################################################################################

#df = pd.DataFrame(amount,columns=header)