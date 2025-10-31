import os, time, requests, logging
from bs4 import BeautifulSoup
from pymongo import MongoClient
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

logging.basicConfig(filename="logs/scraper.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s') 
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "FASHIONDB")
DB_COLLECTION = os.getenv("DB_COLLECTION", "PRODUCTS")

print("Mongo URI:", os.getenv("MONGO_URI"))
print("DB Name:", os.getenv("DB_NAME"))
print("Collection:", os.getenv("DB_COLLECTION"))

class MongoDb:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[DB_COLLECTION]
        logging.info("Connected to MongoDB")
    def insertproduct(self, product):
        product['scraped_at'] = datetime.utcnow()
        self.collection.update_one(
            {"product_id": product.get("product_id")},
            {"$set": product},
            upsert=True
        )
        logging.info(f"Upserted product: {product['product_id']}")

class ImageDownloard:
    def __init__(self, out_dir="data/images"):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)
        self.out_dir = out_dir
    def download(self, url, filename_hint="image"):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                ext = url.split(".")[-1].split("?")[0]
                filename = f"{filename_hint}.{ext}"
                path = os.path.join(self.out_dir, filename)
                with open(path, "wb") as f:
                    f.write(response.content)
                return path
        except Exception as e:
            logging.error(f"Failed to load image: {e}")
        return None
class SeleniumScraper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
            )
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
    def get_soup(self, url):
        try:
            self.driver.get(url)
            time.sleep(3)  # Wait for JavaScript to load content
            html = self.driver.page_source
            logging.info(f"Fetched and parsed page: {url}")
            return BeautifulSoup(html, "html.parser")
        except Exception as e:
            logging.error(f"Failed to fetch page {url}: {e}")
            return None
    def close(self):
        self.driver.quit()
        logging.info("Closed Selenium WebDriver")