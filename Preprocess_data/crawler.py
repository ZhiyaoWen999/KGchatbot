import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os

class UCLCourseScraper:
    def __init__(self):
        self.base_url = 'https://www.ucl.ac.uk/prospective-students/graduate/taught-degrees'
        self.urls_file = 'data/urls.txt'
        self.course_info_file = 'data/course_info.json'
        self.course_urls = []

    def fetch_course_urls(self):
        """crawl course from url"""
        try:
            response = requests.get(self.base_url)
            response.raise_for_status() 
            soup = BeautifulSoup(response.text, 'html.parser')
            self.course_urls = set(a['href'] for a in soup.find_all('a', href=True) 
                                   if a['href'].startswith(self.base_url))
            with open(self.urls_file, 'w') as f:
                for link in self.course_urls:
                    f.write(f"{link}\n")
            print(f"URLs have been written to {self.urls_file}")
        except requests.RequestException as e:
            print(f"Failed to fetch course URLs: {e}")

    def fetch_course_info(self, url):
        """fetch the course page information"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            course_title = soup.find('h1').get_text(strip=True)
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            return {'url': url, 'title': course_title, 'paragraphs': paragraphs}
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def crawl_course_pages(self):
        """crawl the course page"""
        with open(self.urls_file, 'r') as f:
            urls = [url.strip() for url in f.readlines()]

        course_infos = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.fetch_course_info, url): url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data:
                        course_infos.append(data)
                        print(f"Finished fetching {url}")
                except Exception as e:
                    print(f"Error processing {url}: {e}")

        with open(self.course_info_file, 'w', encoding='utf-8') as f:
            json.dump(course_infos, f, ensure_ascii=False, indent=4)
        print(f"Finished! Course information has been saved to {self.course_info_file}")

    def run(self):

        print("Starting to fetch course URLs...")
        self.fetch_course_urls()
        print("Starting to fetch course information...")
        self.crawl_course_pages()
        print("All tasks completed successfully!")

if __name__ == "__main__":
    scraper = UCLCourseScraper()
    scraper.run()
