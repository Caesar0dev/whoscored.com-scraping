from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from undetected_chromedriver import Chrome, ChromeOptions
import time
import datetime
from seleniumbase import Driver

current_date = datetime.date.today()
print(current_date)

driver = Driver(uc=True)
driver.maximize_window()
driver.get("https://1xbet.whoscored.com/LiveScores")

total_box = driver.find_element(By.XPATH, '/html/body/div[4]/div[3]/div[1]/div/div/div/div[4]/div[9]')
numbers = total_box.find_elements(By.CLASS_NAME, 'Match-module_score__5Ghhj')
teams = total_box.find_elements(By.CLASS_NAME, 'Match-module_teamName__GoJbS')
homeTeamNumbers = []
awayTeamNumbers = []
for i in range(len(numbers)):
    resultNumbers = numbers[i].find_elements(By.TAG_NAME, 'span')
    homeTeamNumbers.append(resultNumbers[0].text)
    awayTeamNumbers.append(resultNumbers[1].text)

print("home team number >>> ", homeTeamNumbers)

# header_box = driver.find_element(By.XPATH, '//*[@id="forex"]/div[3]/div/table/thead')
# header_elements= header_box.find_elements(By.TAG_NAME, 'th')
# for i in range(len(header_elements)-1):
#     header = header_elements[i].text
#     header = header.replace("\n", " ")
#     print(">>>", header)

# elements_box = driver.find_element(By.XPATH, '//*[@id="forex-content"]/tr[1]/td[1]').text

# print("------->", elements_box)

time.sleep(6)
driver.quit()