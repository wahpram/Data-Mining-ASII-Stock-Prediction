import requests
import csv
import os
from time import sleep
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def load_page(self, element):
    global myElem
    delay = 5
    try:
        myElem = WebDriverWait(self, delay).until(EC.presence_of_element_located((By.XPATH, element)))
    except TimeoutException:
        print('Loading too much time')

    return myElem


def format_date(date):
    return date.strftime("%Y-%m-%d")


def write_to_csv(data, filename):
    with open(filename, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(data)


def main():
    driver = webdriver.Chrome()
    driver.get('https://idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham/')
    
    all_items = []
    
    filter = driver.find_element(By.CSS_SELECTOR, '.btn-filter-input.mb-8.btn-col-filter.full-responsive')
    filter.click()
    
    sleep(3)
    
    driver.find_element(By.XPATH, '//*[@id="fltr4"]').click()
    
    apply_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/main/div/div[1]/div[2]/div[2]/button[2]')
    apply_button.click()
    
    sleep(3)
    
    start_date = datetime(2024, 3, 1)
    end_date = datetime(2024, 3, 31)
    
    current_date = start_date
    
    csv_filename = 'ASII_stock.csv'
    
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        if not file_exists:
            csv_writer.writerow(['timestamp', 'open', 'low', 'high', 'close', 'volume'])
            
    
    while current_date <= end_date:
        formated_date = format_date(current_date)
        
        try:
            find_date = driver.find_element(By.CLASS_NAME, 'mx-input')
            ActionChains(driver).move_to_element(find_date).perform()
            
            sleep(2)
            find_date.click()
            find_date.clear()
            
            sleep(2)
            find_date.send_keys(formated_date)
            find_date.send_keys(Keys.RETURN)
        except:
            pass
        
        sleep(3)
        try:
            row_page = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.footer__row-count__select'))
            )
            row_page.click()
            
            all_page = load_page(driver, '/html/body/div[2]/div/div/div[2]/main/div/div[2]/div/div[3]/div[1]/form/select/option[6]')
            all_page.click()
        except:
            pass
        
        sleep(3)
        
        try:
            ActionChains(driver).move_to_element(driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[2]/main/div/div[2]/div/div[2]/table/tbody/tr[59]')).perform()
        except:
            pass
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        rows = soup.find_all('tr')
        
        item_found = False
        for row in rows:
            if "ASII" in row.get_text():
                td_elements = row.find_all('td')
                td_texts = [td.get_text(strip=True) for td in td_elements]
                
                print(f"ASII available in {formated_date}")
                
                item = [text.replace('.', '') for text in td_texts]
                open_item = item[1]
                highest = item[2]
                lowest = item[3]
                close = item[4]
                volume = item[6]
                item_found = True
                break
        
        if item_found:
            all_items.append([formated_date, open_item, lowest, highest, close, volume])
            write_to_csv([formated_date, open_item, lowest, highest, close, volume], csv_filename)
            
        sleep(3)
        current_date += timedelta(days=1)
    
    print(all_items)
    
    driver.quit()
    

if __name__ == '__main__':
    main()