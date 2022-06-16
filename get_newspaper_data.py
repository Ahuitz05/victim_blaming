from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import pandas as pd
import time
from bs4 import BeautifulSoup

# Constants
URL = "https://pnmi.segob.gob.mx/reporte/"
TAB_NAMES = ['Información sobre el medio impreso', 'Circulación y distribución geográfica', 'Perfil del lector'] # website is poorly labeled so names are needed
TAB_PREFIX = ['info', 'circulacion', 'perfil']

def circulacion_collector():
    title = driver.find_element(By.TAG_NAME, "h3").text
    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")
    table = soup.find_all("table")[1]
    df = pd.read_html(str(table))[0]
    df.insert(0, 'periodico', title)
    return df


def table_collector():
    rows = driver.find_elements(By.TAG_NAME, "td")
    columns = []
    values = []
    rows = [i for i in rows if i.text != '']
    for row in range(len(rows)):
        if row % 2 == 0:
            columns.append(rows[row].text)
        else:
            values.append(rows[row].text)
    
    zip_iterator = zip(columns, values)
    k_v = dict(zip_iterator)

    return k_v



def data_collector():
    """
    Returns a dataframe with all the information found in paragraphs and tables
    """
    data = {}
    for tab, pref in zip(TAB_NAMES, TAB_PREFIX):
        driver.find_element(by=By.XPATH, value=f"//a[text()='{tab}']").click()
        datos = driver.find_elements(By.TAG_NAME, "p")

        for val in range(len(datos)):
            if datos[val].text != '':
                if len(datos[val].text.split(': ')) == 2:
                    values = datos[val].text.split(': ')
                    colname, value = values[0], values[1]
                    colname = pref + '_' + colname
                    k_v = dict([[colname, value]])
                    data.update(k_v)
        
        if pref == 'circulacion':
             circulacion = circulacion_collector()
        if pref == 'perfil':
            data.update(table_collector())


    df = pd.DataFrame([data], columns=data.keys())
    return df, circulacion




def get_data_sys(driver):
    # Go to website
    driver.get(URL)
    select = Select(driver.find_element(by="name", value="tipo"))
    # select by value
    select.select_by_value("PERIODICO")
    driver.find_element(by="name", value="publicacion").submit()

    # get list of all divs with papers
    elements = driver.find_elements(by=By.CLASS_NAME, value='resultado')

    for i in range(len(elements)):  # stale element error.
        periodicos = driver.find_elements(by=By.CLASS_NAME, value='resultado')
        periodicos[i].click()

        # get info
        retry_counter = 0
        while True:
            try:
                if retry_counter <= 3:
                    master_data_new, circulacion_new = data_collector()
                    master_data = pd.concat([master_data, master_data_new])
                    circulacion = pd.concat([circulacion, circulacion_new])
                    
                    print(master_data)
                    print(circulacion)
                    break
            except:
                retry_counter += 1
                if retry_counter > 3:
                    master_data, circulacion = data_collector()
                    print(master_data)
                    print(circulacion)
                    break
                print(f"retrying. Attempt: {retry_counter}")
                continue
        
        # go back
        driver.find_element(by=By.CLASS_NAME, value="regresar").click()
    return master_data, circulacion


# Chrome driver setup
chromeOptions = webdriver.ChromeOptions()
# prefs = {"download.default_directory": WORK_FILES}
# chromeOptions.add_experimental_option("prefs", prefs)
chromeOptions.headless = False


s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=chromeOptions)

master_data, circulacion = get_data_sys(driver)
master_data.to_csv('newspaper_data.csv', index=False)
circulacion.to_csv('circulacion.csv', index=False)

