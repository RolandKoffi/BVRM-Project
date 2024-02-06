import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import StaleElementReferenceException
import pymongo as py
import json
import time

#########################################################################

driver_path = "./geckodriver"
s = Service(driver_path)
driver = Firefox(service=s)
url = "https://bfin.brvm.org/Activites_marche.aspx"
driver.get(url)
page = requests.get(url)


#########################################################################


client = py.MongoClient("mongodb://localhost:27017")
db = client.brvm 


#########################################################################

soup = BeautifulSoup(page.text, 'lxml')


#########################################################################

select_date = Select(driver.find_element(By.XPATH, '//select[@id="ctl00_Main_DropDownList1"]'))

options = select_date.options



""" dt = []
for i in range(len(options)):
    dt.append(options[i].text)

print(dt.index('26/12/2023')) #21
#print(len(options)) #5889
#print(dt[0])
driver.quit() """


 
for index in range(23, 3001):

    time.sleep(5)

    table = soup.find('table', id='ctl00_Main_GridView1')

    headers = []
    for i in table.find_all('th'):
        title = i.text
        headers.append(title)

    headers = headers[1:]

    actions = pd.DataFrame(columns=headers)
    actions['Date'] = ""
    

    try:
        date = options[index].text
        select_date.select_by_index(index)

        if (len(table.find_all('tr')) != 1) :

            for j in table.find_all('tr')[1:]:
                row_data = j.find_all('td')[1:]
                row = [i.text for i in row_data]
                length = len(actions)
                actions.loc[length, :"Valeur échangée"] = row
                actions['Date'] = date

            records = actions.to_json(orient='records')
            records = json.loads(records)
            db.actions.insert_many(records)
            


    except StaleElementReferenceException as e:
        
        time.sleep(5)

        select_date = Select(driver.find_element(By.XPATH, '//select[@id="ctl00_Main_DropDownList1"]'))
        options = select_date.options

        table = soup.find('table', id='ctl00_Main_GridView1')

        headers = []
        for i in table.find_all('th'):
            title = i.text
            headers.append(title)

        headers = headers[1:]

        actions = pd.DataFrame(columns=headers)
        actions['Date'] = ""

        date = options[index].text
        select_date.select_by_index(index)

        if (len(table.find_all('tr')) != 1) :
            
            for j in table.find_all('tr')[1:]:
                row_data = j.find_all('td')[1:]
                row = [i.text for i in row_data]
                length = len(actions)
                actions.loc[length, :"Valeur échangée"] = row
                actions['Date'] = date

            records = actions.to_json(orient='records')
            records = json.loads(records)
            db.actions.insert_many(records)

driver.quit() 