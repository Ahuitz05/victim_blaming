from unicodedata import name
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import time

# Constants

URL = "https://pnmi.segob.gob.mx/reporte/"
TAB_NAMES = ['Información sobre el medio impreso', 'Información adicional sobre el medio impreso', 'Circulación y distribución geográfica', 'Perfil del lector'] # website is poorly labeled so names are needed


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
        driver.find_element_by_xpath(f"//a[text()='{i}']").click()
        datos = driver.find_elements_by_tag_name("p")

        for val in range(len(datos)):
            if datos[val].text != '':
                if len(datos[val].text.split(': ')) == 2:
                    k_v = dict([datos[val].text.split(': ')])
                    data.update(k_v)
    return data




def get_data_sys(driver):
    # Go to website
    driver.get(URL)
    select = Select(driver.find_element(by="name", value="tipo"))
    # select by value
    select.select_by_value("PERIODICO")
    driver.find_element(by="name", value="publicacion").submit()

    # get list of all divs with papers
    elements = driver.find_elements_by_class_name("resultado")

    for i in range(len(elements)):  # stale element error.
        periodicos = driver.find_elements_by_class_name("resultado")
        periodicos[i].click()

        # get info
        data = data_collector()

        print(data)
        # go back
        driver.find_element_by_class_name("regresar").click()


# Chrome driver setup
chromeOptions = webdriver.ChromeOptions()
# prefs = {"download.default_directory": WORK_FILES}
# chromeOptions.add_experimental_option("prefs", prefs)
chromeOptions.headless = False


s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=chromeOptions)

get_data_sys(driver)
