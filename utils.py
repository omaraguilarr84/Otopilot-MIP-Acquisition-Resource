import time
import random
import pandas as pd
import re
import math
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

def start_driver(auth_url):
    options = Options()
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'
    ]
    user_agent = random.choice(user_agents)
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--headless")
    options.page_load_strategy = 'eager'

    driver = uc.Chrome(options=options)
    driver.get(auth_url)
    time.sleep(3)

    return driver

def pt_search_scrape(patient_id, side, driver, edData):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'patientIdInput'))).send_keys(patient_id)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'patientSearchSubmit'))).click()

        time.sleep(1)
        edData.append({'Patient ID': patient_id, 'Side': side, 'Electrode Number': 1, 'Distance': 5, 'Angle': 30, 'Place Frequency': 1000, 'Channel Frequency': 1500, 'Scalar Location': 'Basal'})
    except Exception as e:
        print(f"Error scraping patient {patient_id}: {e}")

def process_and_match_data(dfED, template_path, output_path):
    df_template = pd.read_csv(template_path)

    for col in df_template.columns:
        df_template[col] = df_template[col].astype(str)

    df_template.set_index('Patient ID', inplace=True)
    dfED.set_index('Patient ID', inplace=True)
    
    for idx in dfED.index:
        if idx in df_template.index:
            for col in dfED.columns:
                df_template.at[idx, col] = dfED.at[idx, col]
    
    df_template.reset_index(inplace=True)
    df_template.to_csv(output_path, index=False)
    print("Data saved to", output_path)
