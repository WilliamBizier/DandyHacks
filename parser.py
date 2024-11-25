from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

existing_csv_path = "spring/econ.csv"
existing_prereqs = {}
with open(existing_csv_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        course_code = row.get("Code")
        prereqs = row.get("Prereqs", "")
        if course_code:
            existing_prereqs[course_code] = prereqs

driver = webdriver.Chrome()

driver.get('https://cdcs.ur.rochester.edu/')

try:
    wait = WebDriverWait(driver, 10)
    term_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "ddlTerm")))
    term_dropdown.click()
    spring_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='Spring 2025']")))
    spring_option.click()
    dept_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "ddlDept")))
    dept_dropdown.click()
    econ_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='CSC - Computer Science']")))
    econ_option.click()
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btnSearchTop")))
    search_button.click()
    time.sleep(5)

    results_code = []
    results_name = []
    results_credits = []
    results_day = []
    results_time_b = []
    results_time_e = []

    index = 0
    while True:
        try:
            result = driver.find_element(By.ID, f"rpResults_lblCNum_{index}")
            results_code.append(result.text)
            result = driver.find_element(By.ID, f"rpResults_cellTitle_{index}")
            results_name.append(result.text)
            result = driver.find_element(By.ID, f"rpResults_lblCredits_{index}")
            results_credits.append(result.text)
            result = driver.find_element(By.ID, f"rpResults_rpSchedule_{index}_lblDay_0")
            results_day.append(result.text)
            result = driver.find_element(By.ID, f"rpResults_rpSchedule_{index}_lblStartTime_0")
            results_time_b.append(result.text)
            result = driver.find_element(By.ID, f"rpResults_rpSchedule_{index}_lblEndTime_0")
            results_time_e.append(result.text)
            index += 1
        except:
            break

    csv_file = 'results.csv'
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Code', 'Title', 'Credits', 'Prereqs', 'Day', 'Begin', 'End'])
        for i, code in enumerate(results_code):
            prereqs = existing_prereqs.get(code, "")
            writer.writerow([code, results_name[i], results_credits[i], prereqs, results_day[i], results_time_b[i], results_time_e[i]])

    print(f"Results saved to {csv_file}")

finally:
    driver.quit()
