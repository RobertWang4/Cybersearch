import requests
import json
import logging
from urllib.parse import quote

class Zoomeye:
    def __init__(self, zoomeye_api_key, verbose=False):
        self.zoomeye_api_key = zoomeye_api_key
        self.verbose = verbose
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "API-KEY": self.zoomeye_api_key
        }

    def auth(self):
        try:
            url = "https://api.zoomeye.org/resources-info"


            response = requests.get(url, headers=self.headers)
            logging.debug(f"Zoomeye response body: {response.json()}")
            response_json = json.loads(response.content.decode("utf-8"))

            if "login_required" in response_json.values():
                return False
            
            logging.info("Zoomeye authentication successful")
            credits = response_json['quota_info']['remain_total_quota']
            logging.info(f"Zoomeye credits: {credits}")
            return True
        
        except Exception as e:
            logging.error(f"Zoomeye authentication failed: {e}")
            return False

    def search(self, query, limit=10):
        results = []
        encoded_query = quote(query)
        url = f"https://api.zoomeye.org/host/search?query={encoded_query}&page=1"


        try:
            response = requests.get(url, headers=self.headers)
            data = response.json()

            if self.verbose:
                logging.debug("Raw response from ZoomEye:\n" + json.dumps(data, indent=2, ensure_ascii=False))

            matches = data.get("matches", [])[:limit]
            for item in matches:
                result = {
                    "ip": item.get("ip"),
                    "port": item.get("portinfo", {}).get("port"),
                    "title": item.get("title", [None])[0] if item.get("title") else None,
                    "domain": item.get("hostname"),
                    "country": item.get("geoinfo", {}).get("country", {}).get("code"),
                    "feed": "zoomeye"
                }
                results.append(result)

            return results

        except Exception as e:
            logging.error(f"Zoomeye search failed: {e}")
            return []