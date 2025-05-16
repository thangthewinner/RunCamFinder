import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse
from tqdm import tqdm

def download_bibpix_images(race_id="tpm2025", start_page=0, end_page=5, save_dir="downloaded_images", lang='vi'):
    os.makedirs(save_dir, exist_ok=True)
    
    for page in range(start_page, end_page + 1):
        base_url = f"https://bibpix.net/photo?race_id={race_id}&bib_type=all&bib=*&lang={lang}&iframe=&page={page}"
        print(f"\n Crawling Page {page}: {base_url}")

        try:
            response = requests.get(base_url, timeout=15)
            if response.status_code != 200:
                print(f"\033[91m Failed to fetch page {page}. Status code: {response.status_code}\033[0m")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            result_image_div = soup.find("div", id="result-image")
            if not result_image_div:
                print(f"\033[93m No result-image div found on page {page}\033[0m")
                continue

            a_tags = result_image_div.find_all("a")
            image_urls = [a['data-src'] for a in a_tags if a.has_attr('data-src')]
            print(f" Found {len(image_urls)} images on page {page}")

            for idx, url in enumerate(tqdm(image_urls, desc=f" Downloading page {page}")):
                try:
                    img_name = url.split("/")[-1].split("?")[0]
                    save_path = os.path.join(save_dir, img_name)

                    if os.path.exists(save_path):
                        print(f"\033[93m Already exists: {img_name}\033[0m")
                        continue

                    image_response = requests.get(url, timeout=10)
                    if image_response.status_code == 200:
                        with open(save_path, "wb") as f:
                            f.write(image_response.content)
                        print(f"\033[92m Downloaded: {img_name}\033[0m")
                    else:
                        print(f"\033[91m Cannot download {url} - Error: {image_response.status_code}\033[0m")
                except requests.exceptions.Timeout:
                    print(f"\033[91m Timeout when downloading {url}\033[0m")
                except Exception as e:
                    print(f"\033[91m Error with {url}: {e}\033[0m")

        except Exception as e:
            print(f"\033[91m Error loading page {page}: {e}\033[0m")

if __name__ == "__main__":
    download_bibpix_images(race_id="tpm2025", start_page=0, end_page=5)
