from doctest import master
from unicodedata import name
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import pandas as pd
import time

# Constants

URL = "https://pnmi.segob.gob.mx/reporte/"
TAB_NAMES = ['Información sobre el medio impreso', 'Información adicional sobre el medio impreso', 'Circulación y distribución geográfica'] # website is poorly labeled so names are needed


def data_collector():
    """
    1 - if dataframe does not exist initializes it with colnames
    2 - collects all data and puts it in a list
    3 - remove colnames
    4 - check that list length = df length
    5 - appends list to df
    """
    data = {}
    for i in TAB_NAMES:
        driver.find_element(by=By.XPATH, value=f"//a[text()='{i}']").click()
        datos = driver.find_elements(By.TAG_NAME, "p")

        for val in range(len(datos)):
            if datos[val].text != '':
                if len(datos[val].text.split(': ')) == 2:
                    k_v = dict([datos[val].text.split(': ')])
                    data.update(k_v)

    df = pd.DataFrame([data], columns=data.keys())
    return df




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
                    master_data = master_data.append(data_collector())
                    print(master_data)
                    break
            except:
                time.sleep(2)
                retry_counter += 1
                if retry_counter > 3:
                    master_data = data_collector()
                    print(master_data)
                    break
                print(f"retrying. Attempt: {retry_counter}")
                continue
        
        # go back
        driver.find_element(by=By.CLASS_NAME, value="regresar").click()
    return master_data


# Chrome driver setup
chromeOptions = webdriver.ChromeOptions()
# prefs = {"download.default_directory": WORK_FILES}
# chromeOptions.add_experimental_option("prefs", prefs)
chromeOptions.headless = False


s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=chromeOptions)

master_data = get_data_sys(driver)
master_data.to_csv('newspaper_data.csv', index=False)

