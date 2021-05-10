from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


text_vals = {
    'gear-levels': ['85', '88', '90'],
    'gear-type': ['white', 'blue', 'purple', 'red'],
}


parse_vals = {
    'gear-lv': ['lv85', 'lv90', 'lv90'],
    'gear-type': ['gwhite', 'gblue', 'gpink', 'gred'],
    'atk': 'atkper',
    'def': 'defper',
    'hp': 'hpper',
    'atkflat': 'atkflat',
    'defflat': 'defflat',
    'hpflat': 'hpflat',
    'crit': 'critch',
    'cd': 'critdmg',
    'spd': 'spd',
    'eff': 'eff',
    'res': 'res',
    'supported_stats': ['atk', 'def', 'hp', 'atkflat', 'hpflat', 'defflat', 'crit', 'cd', 'spd', 'eff', 'res']
}

GECKODRIVER_PATH = '/app/vendor/geckodriver/geckodriver'
FIREFOX_PATH = '/app/vendor/firefox/firefox'

def run(stat_list, value_list, gear_options=None):
    text = ""
    #url for gear
    url = 'https://meowyih.github.io/epic7-gear/index.html?lang=en'

    #Firefox headless options & start webbdriver
    firefox_options = FirefoxOptions()
    firefox_options.headless = True
    fire_bin = FirefoxBinary(FIREFOX_PATH)
    driver = webdriver.Firefox(options=firefox_options, executable_path=GECKODRIVER_PATH, firefox_binary=fire_bin)

    # vars for the website
    gear_level_id= 'gear-lv'
    gear_type_id = 'gear-type'
    gear_enhance_id = 'gear-enc-lv'
    default_gear_lvl = 'lv85'
    default_gear_type = 'gpink'
    default_enhance_level = 'gear-lv15'

    # calc and response btn
    calc_btn_id = 'btn-calc'
    response_id = 'errmsg'


    id_args = [gear_level_id, gear_type_id, gear_enhance_id]
    val_args = [default_gear_lvl, default_gear_type, default_enhance_level]
    if len(gear_options) == 2:
        val_args = gear_options
        val_args.append(default_enhance_level)
    

    print("Running the selenium script...")

    driver.get(f"{url}")
    args = stat_list
    percents = value_list

    #select default gear lvl, type, enhance lvl
    for idx, id in enumerate(id_args):
        select = Select(driver.find_element_by_id(f"{id}"))
        select.select_by_value(val_args[idx])

    #add values
    for index, arg in enumerate(args):
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, f"{parse_vals[arg]}"))
            )
        finally:
            element = driver.find_element_by_id(f"{parse_vals[arg]}")
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



