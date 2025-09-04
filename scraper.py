import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import hashlib
from PIL import Image
import io

class ImageScraper:
    def __init__(self, download_path="downloads"):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Setup Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless=new")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")

    def get_driver(self):
        """Initialize and return Chrome driver using system chromedriver"""
        service = Service("/usr/bin/chromedriver")  # Use system-installed chromedriver
        return webdriver.Chrome(service=service, options=self.chrome_options)

    def search_google_images(self, query="", max_images=20):
        print(f"Searching Google Images for: {query}")
        driver = self.get_driver()
        images = []

        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&tbm=isch"
            driver.get(search_url)
            time.sleep(2)

            img_elements = driver.find_elements(By.CSS_SELECTOR, "img")
            for img in img_elements[:max_images]:
                src = img.get_attribute("src")
                if src and src.startswith("http"):
                    images.append(src)
        except Exception as e:
            print(f"Google scraping error: {e}")
        finally:
            driver.quit()

        return images

    def search_bing_images(self, query="", max_images=20):
        print(f"Searching Bing Images for: {query}")
        driver = self.get_driver()
        images = []

        try:
            search_url = f"https://www.bing.com/images/search?q={query.replace(' ', '+')}"
            driver.get(search_url)
            time.sleep(2)

            img_elements = driver.find_elements(By.CSS_SELECTOR, "img.mimg")
            for img in img_elements[:max_images]:
                src = img.get_attribute("src")
                if src and src.startswith("http"):
                    images.append(src)
        except Exception as e:
            print(f"Bing scraping error: {e}")
        finally:
            driver.quit()

        return images

    def search_yahoo_images(self, query="", max_images=20):
        print(f"Searching Yahoo Images for: {query}")
        driver = self.get_driver()
        images = []

        try:
            search_url = f"https://images.search.yahoo.com/search/images?p={query.replace(' ', '+')}"
            driver.get(search_url)
            time.sleep(2)

            img_elements = driver.find_elements(By.CSS_SELECTOR, "img")
            for img in img_elements[:max_images]:
                src = img.get_attribute("src")
                if src and src.startswith("http"):
                    images.append(src)
        except Exception as e:
            print(f"Yahoo scraping error: {e}")
        finally:
            driver.quit()

        return images

    def download_image(self, url, search_name="image", filename=None):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=15, stream=True)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return False

            content = response.content
            if not filename:
                url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
                extension = self.get_image_extension(content)
                safe_name = search_name.strip().replace(" ", "_").lower() or "image"
                filename = f"{safe_name}_{url_hash}.{extension}"

            filepath = os.path.join(self.download_path, filename)

            if self.is_valid_image(content):
                with open(filepath, 'wb') as f:
                    f.write(content)
                return True
            return False
        except Exception as e:
            print(f"Download error: {e}")
            return False

    def get_image_extension(self, content):
        try:
            img = Image.open(io.BytesIO(content))
            return img.format.lower()
        except:
            return "jpg"

    def is_valid_image(self, content):
        try:
            img = Image.open(io.BytesIO(content))
            if img.width < 150 or img.height < 150:
                return False
            if len(content) < 5000:
                return False
            return True
        except:
            return False

    def scrape_and_download(self, source="google", query="", max_images=20):
        images = []

        if source == "google":
            images = self.search_google_images(query, max_images)
        elif source == "bing":
            images = self.search_bing_images(query, max_images)
        elif source == "yahoo":
            images = self.search_yahoo_images(query, max_images)
        elif source == "all":
            g = self.search_google_images(query, max_images // 3)
            b = self.search_bing_images(query, max_images // 3)
            y = self.search_yahoo_images(query, max_images // 3)
            images = g + b + y

        images = list(dict.fromkeys(images))  # remove duplicates
        downloaded = 0
        for img_url in images:
            if self.download_image(img_url, search_name=query):
                downloaded += 1
            time.sleep(1)

        return downloaded

