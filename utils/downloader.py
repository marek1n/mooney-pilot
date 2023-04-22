import requests
from os import getenv
from pathlib import Path
from tqdm import tqdm
from functools import cache



class AzureImgSearch:

    def __init__(self):
        self._KEY = getenv("SUBSCRIPTION_KEY")
        self._SEARCH_URL = "https://api.bing.microsoft.com/v7.0/images/search"
        self._HEADERS = {
            "Ocp-Apim-Subscription-Key": self._KEY
            }

    @cache
    def get_image_urls(self, search_term: str, offset_max: int = 200) -> list[str]:

        params  = {
            "q": search_term,
            "license": "public", 
            "imageType": "photo",
            "aspect": "all"
            }

        print(f"\nSearching for '{search_term}' images...\n")

        urls = []
        offset = 0

        while offset <= offset_max:
            params["offset"] = offset
            response = requests.get(self._SEARCH_URL, headers=self._HEADERS, params=params)
            response.raise_for_status()
            search_results = response.json()

            for item in search_results["value"]:
                url = item["contentUrl"]
                urls.append(url)

            # check if search not stuck on last page
            if (params["offset"] == search_results["nextOffset"]
                or params["offset"] > search_results["nextOffset"]): 
                break

            offset = search_results["nextOffset"]

        urls = list(set(urls))
        print(len(urls), f"urls found for {search_term}\n")

        return urls


    def save_images(url_list: list[str], search_term: str):
        path = Path.cwd() / "final" / search_term
        path.mkdir(parents=True, exist_ok=True)

        print(f"\nSaving images to {path}")
        print("\ndownloading images...\n")

        for i, url in tqdm(enumerate(url_list), leave=False):
            im_path = path / f"{search_term}_{i}.jpg"
            try:
                with open(im_path, 'wb') as f:
                    img_data = requests.get(url, stream=True)
                    f.write(img_data.content)
            except Exception as e:
                print(e)
                continue

        print("\nDownload finished")
