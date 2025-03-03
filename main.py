import time
import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# LinkedIn credentials
EMAIL = "xepoga8879@egvoo.com"
PASSWORD = "Hehe@ggxml"
JOB_SEARCH = "python"
LOCATION = "India"
NUM_JOBS_TO_APPLY = 10  # Number of jobs to apply

# Setup Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Control variables
paused = False
stop_thread = False

def login():
    """Logs into LinkedIn using provided credentials."""
    driver.get("https://www.linkedin.com/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(EMAIL)
    driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)

def search_jobs():
    """Searches for jobs with specified criteria."""
    driver.get("https://www.linkedin.com/jobs/")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']"))).send_keys(JOB_SEARCH)
    location_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
    location_input.clear()
    location_input.send_keys(LOCATION + Keys.RETURN)
    time.sleep(3)
    try:
        easy_apply_filter = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Easy Apply filter')]"))
        )
        easy_apply_filter.click()
    except:
        print("Easy Apply filter not found or already selected.")
    try:
        past_week_filter = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Date Posted filter')]"))
        )
        past_week_filter.click()
        time.sleep(2)
        last_week_option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Past Week')]"))
        )
        last_week_option.click()
    except:
        print("Past Week filter not found or already selected.")

def apply_jobs():
    """Applies to jobs using the Easy Apply feature."""
    global paused, stop_thread
    time.sleep(5)
    jobs = driver.find_elements(By.CLASS_NAME, "job-card-container")
    applied_jobs = []
    for job in jobs[:NUM_JOBS_TO_APPLY]:
        if stop_thread:
            print("Stopping job application process.")
            return
        while paused:
            print("Paused. Waiting to resume...")
            time.sleep(2)
        job.click()
        time.sleep(2)
        try:
            easy_apply_button = driver.find_element(By.CLASS_NAME, "jobs-apply-button")
            easy_apply_button.click()
            time.sleep(2)
            while True:
                if stop_thread:
                    print("Stopping job application process.")
                    return
                while paused:
                    print("Paused. Waiting to resume...")
                    time.sleep(2)
                try:
                    action_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "artdeco-button--primary"))
                    )
                    if "Next" in action_button.text or "Review" in action_button.text:
                        action_button.click()
                        time.sleep(2)
                    elif "Submit" in action_button.text:
                        action_button.click()
                        print("Applied to:", job.text)
                        applied_jobs.append([job.text])
                    else:
                        break
                except:
                    print("Manual input required. Complete the form and proceed.")
                    time.sleep(5)
            try:
                close_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Dismiss']"))
                )
                close_button.click()
            except:
                print("No close button found.")
        except:
            print("Skipping job (No Easy Apply)")
    with open("applied_jobs.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Job Title"])
        writer.writerows(applied_jobs)

def main():
    """Main function that logs in, searches jobs, and applies continuously."""
    global paused, stop_thread
    try:
        login()
        search_jobs()
        while not stop_thread:
            apply_jobs()
            print("Waiting before searching for new jobs...")
            time.sleep(600)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Manual intervention required, keeping browser open.")
        while not stop_thread:
            time.sleep(10)

def pause_script():
    """Pauses or resumes the script based on the current state."""
    global paused
    paused = not paused
    print("Script paused." if paused else "Script resumed.")

def stop_script():
    """Stops the script execution."""
    global stop_thread
    stop_thread = True
    print("Script stopping...")

if __name__ == "__main__":
    thread = threading.Thread(target=main)
    thread.start()
    while True:
        command = input("Enter command (pause/resume/stop): ")
        if command.lower() == "pause":
            pause_script()
        elif command.lower() == "resume":
            pause_script()
        elif command.lower() == "stop":
            stop_script()
            break