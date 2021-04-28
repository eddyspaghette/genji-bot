from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def run():
    text = ""
    #url for gear
    url = 'https://meowyih.github.io/epic7-gear/index.html?lang=en'

    #Firefox headless options & start webbdriver
    firefox_options = FirefoxOptions()
    firefox_options.headless = True
    driver = webdriver.Firefox(options=firefox_options)

    # vars for the website
    gear_level_id= 'gear-lv'
    gear_type_id = 'gear-type'
    gear_enhance_id = 'gear-enc-lv'
    default_gear_lvl = 'lv85'
    default_gear_type = 'gpink'
    default_enhance_level = 'gear-lv15'
    calc_btn_id = 'btn-calc'
    response_id = 'errmsg'


    id_args = [gear_level_id, gear_type_id, gear_enhance_id]
    val_args = [default_gear_lvl, default_gear_type, default_enhance_level]

    print("Running the selenium script...")

    driver.get(f"{url}")
    args = ['atkper', 'defper', 'hpper', 'spd']
    percents = [15, 15, 15, 10]

    #select default gear lvl, type, enhance lvl
    for idx, id in enumerate(id_args):
        select = Select(driver.find_element_by_id(f"{id}"))
        select.select_by_value(val_args[idx])

    #add values
    for index, arg in enumerate(args):
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, f"{arg}"))
            )
        finally:
            element = driver.find_element_by_id(f"{arg}")
            element.send_keys(percents[index])

    #Calculate
    element = driver.find_element_by_id(calc_btn_id)
    element.click()

    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, response_id))
        )
    finally:
        text = element.text


    #Close the webdriver
    print("Closing the selenium script...")
    driver.close()
    return text



