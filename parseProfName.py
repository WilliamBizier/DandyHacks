import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

existing_csv_path = "wrtg_spring.csv"

existing_courses = {}
with open(existing_csv_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    for row in rows:
        code = row.get("Code")
        if code:
            existing_courses[code] = row

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
    econ_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//option[text()='WRTG - Writing Program']")))
    econ_option.click()
    search_button = wait.until(EC.element_to_be_clickable((By.ID, "btnSearchTop")))
    search_button.click()
    time.sleep(5)

    index = 0
    while True:
        try:
            code_element = driver.find_element(By.ID, f"rpResults_lblCNum_{index}")
            code = code_element.text
            try:
                professor_element = driver.find_element(By.ID, f"rpResults_lblInstructors_{index}")
                professor = professor_element.text if professor_element.text.strip() else ""
            except:
                professor = ""
            if code in existing_courses:
                existing_courses[code]["Professor"] = professor
            index += 1
        except:
            break

    updated_csv_path = "spring/cs_updated.csv"
    with open(updated_csv_path, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = list(rows[0].keys()) + ["Professor"] if "Professor" not in rows[0] else list(rows[0].keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in existing_courses.values():
            writer.writerow(row)

    print(f"Updated CSV saved to {updated_csv_path}")

finally:
    driver.quit()
