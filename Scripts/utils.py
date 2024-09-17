import time
import random
import pandas as pd
import re
import math
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import messagebox

def start_driver(auth_url):
    options = Options()
    
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'
    ]
    user_agent = random.choice(user_agents)
    options.add_argument(f'user-agent={user_agent}')

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--headless=new")

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(auth_url)
        time.sleep(10)
        return driver
    except Exception as e:
        messagebox.showerror('Error', f'Failed to start driver: {e}')
        return None

def pt_search_scrape(id, side, driver, edData):
    try:
        id_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tableFoot"]/th[1]/input')))
        id_input.clear()
        id_input.send_keys(id)
        side_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="tableFoot"]/th[2]/input')))
        side_input.clear()
        side_input.send_keys(side)
        
        driver.find_element(By.XPATH, '//*[@id="displayList"]/tbody/tr[1]/td[3]/a[2]').click()

        ed_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="electrode-data-tab"]')))
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="axialSlider"]/span')))
        ed_tab.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="ed_chart1"]/div/div/table')))
        
        ed_table = driver.find_element(By.XPATH, '//*[@id="ed_chart1"]/div/div/table/tbody')
        electrodes = ed_table.find_elements(By.XPATH, './tr')

        for electrode in electrodes:
            info = electrode.find_elements(By.XPATH, './td')

            data = {
                'Patient ID': id,
                'Electrode Number': info[0].text,
                'Distance': info[1].text,
                'Angle': info[2].text,
                'Place Frequency': info[3].text,
                'Channel Frequency': info[4].text,
                'Scalar Location': info[5].text
            }
            edData.append(data)

        print(f'Successfully Retrieved Patient ID: {id}')
        driver.back()
    except Exception as e:
        print(f'Failed Attempt for Patient ID: {id}: {e}')
        driver.quit()

def process_and_match_data(dfED, template_path, output_path, mrn_path):
    # Load Data
    electrodeData = dfED
    mrnData = pd.read_excel(mrn_path)
    template = pd.read_csv(template_path)

    # Clean Data
    cleanedData = electrodeData[electrodeData['Patient ID'].str.startswith('MUSC')]
    cleanedData.loc[:, 'Patient ID'] = cleanedData['Patient ID'].str.replace(r'^MUSC1', 'MUSC', regex=True)

    # Match MRN
    matched = []
    for index, row in cleanedData.iterrows():
        pt_id = row['Patient ID']
        mrn_row = mrnData[mrnData['CT SCAN ID'] == pt_id]
        
        if not mrn_row.empty:
            mrn = mrn_row.iloc[0]['MRN']
            row_data = row.to_dict()
            row_data['MRN'] = mrn
            matched.append(row_data)
        else:
            messagebox.showerror('Error', f'MRN not found for {pt_id}')

    dfMatched = pd.DataFrame(matched)

    # Output to Template
    template['mrn'] = dfMatched['MRN']
    template['vanderbilt_id'] = dfMatched['Patient ID']

    for column_name, series in dfMatched.items():
        num = re.findall(r'\d+', column_name)
        if num:
            num_value = int(num[0])
            if num_value == 1:
                template['distance_mm'] = dfMatched['Distance 1']
                template['angle_degree'] = dfMatched['Angle 1']
                template['place_frequency_hz'] = dfMatched['Place Frequency 1']
                template['channel_frequency_hz'] = dfMatched['Channel Frequency 1']
                template['scalar_location'] = dfMatched['Scalar Location 1']
            elif num_value > 1:
                template[f'distance_mm_{num_value}'] = dfMatched[f'Distance {num_value}']
                template[f'angle_degree_{num_value}'] = dfMatched[f'Angle {num_value}']
                template[f'place_frequency_hz_{num_value}'] = dfMatched[f'Place Frequency {num_value}']
                template[f'channel_frequency_hz_{num_value}'] = dfMatched[f'Channel Frequency {num_value}']
                template[f'scalar_location_{num_value}'] = dfMatched[f'Scalar Location {num_value}']

    template['redcap_event_name'] = 'pre_surgery_data_a_arm_1'
    template['electrode_obtained'] = '1'
    template['electrode_data_w_mismatch_complete'] = '2'

    sl_mapping = {
        'Scala Tympani': '1',
        'Scala Vestibuli': '2',
        'Out of Cochlea': '3',
        'Basilar Membrane': '4'
    }

    template['scalar_location'] = template['scalar_location'].map(sl_mapping)

    for i in range(2, 23):
        template[f'scalar_location_{i}'] = template[f'scalar_location_{i}'].map(sl_mapping)

    template.to_csv(output_path, index=False, mode='w')
