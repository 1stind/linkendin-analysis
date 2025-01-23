from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

class LinkedInScraper:
    def __init__(self, browser_path, driver_path, url, output_path, num_jobs):
        self.browser_path = browser_path
        self.driver_path = driver_path
        self.url = url
        self.output_path = output_path
        self.num_jobs = num_jobs
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        options = Options()
        options.binary_location = self.browser_path
        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def scrape_jobs(self):
        self.driver.maximize_window()
        self.driver.get(self.url)

        n_scroll = (self.num_jobs // 25) + 1

        for _ in range(n_scroll):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            try:
                button = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/main/section[2]/button")
                button.click()
                time.sleep(2)
            except Exception:
                pass

        jobs = self.driver.find_element(By.CLASS_NAME, "jobs-search__results-list").find_elements(By.TAG_NAME, 'li')
        print(f"Total jobs scraped: {len(jobs)}")
        
        return jobs

    def extract_job_details(self, jobs):
        job_data = {
            'Date': [], 'Company': [], 'Title': [], 'Location': [],
            'Description': [], 'Type': []
        }

        for job in jobs:
            try:
                job_data['Title'].append(job.find_element(By.CSS_SELECTOR, 'h3').get_attribute('innerText'))
                job_data['Company'].append(job.find_element(By.CSS_SELECTOR, 'h4').get_attribute('innerText'))
                job_data['Location'].append(job.find_element(By.CLASS_NAME, 'job-search-card__location').get_attribute('innerText'))
                job_data['Date'].append(job.find_element(By.CSS_SELECTOR, 'div>div>time').get_attribute('datetime'))
                job_data['Description'].append(self._extract_description(job))
                job_data['Type'].append(self._extract_detail(job, 2))
            except Exception as e:
                print(f"Error extracting job: {e}")

        return pd.DataFrame(job_data)

    def _extract_description(self, job):
        try:
            jd_path = '/html/body/div[1]/div/section/div[2]/div/section[1]/div/div/section'
            return job.find_element(By.XPATH, jd_path).get_attribute('innerText')
        except Exception:
            return ""

    def _extract_detail(self, job, index):
        try:
            detail_path = f'/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[{index}]/span'
            return job.find_element(By.XPATH, detail_path).get_attribute('innerText')
        except Exception:
            return ""

    def save_to_excel(self, job_data):
        job_data.to_excel(self.output_path, index=False)
        print(f"Data saved to {self.output_path}")

    def close_driver(self):
        self.driver.quit()

if __name__ == "__main__":
    browser_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    driver_path = "D:\\Aplikasi\\chromedriver-win64\\chromedriver.exe"

    # Input dari user
    keywords = input("Masukkan Kata Kunci (cth, Desainer): ")
    location = input("Masukkan Lokasi (cth, Indonesia): ")
    num_jobs = int(input("Masukkan estimasi lowongan yang di scrape: "))

    # Membentuk URL berdasarkan input user
    url = f"https://www.linkedin.com/jobs/search/?keywords={keywords.replace(' ', '%20')}&location={location.replace(' ', '%20')}"

    # Membuat nama file berdasarkan keyword
    output_filename = f"{keywords.replace(' ', '_')}.xlsx"
    output_path = f"D:/##KAMI CINTA AMIKOM/SEMESTER 5/PYTHON LANJUT/UAS/HASIL SCRAPPING/{output_filename}"

    scraper = LinkedInScraper(browser_path, driver_path, url, output_path, num_jobs)

    try:
        jobs = scraper.scrape_jobs()
        job_data = scraper.extract_job_details(jobs)
        scraper.save_to_excel(job_data)
    finally:
        scraper.close_driver()
