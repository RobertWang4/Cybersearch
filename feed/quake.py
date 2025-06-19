import json
import requests
import logging
from urllib.parse import quote

class Quake:
    def __init__(self, quake_key, verbose=False):
        self.quake_key = quake_key
        self.verbose = verbose
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "application/json",
            "X-QuakeToken": self.quake_key
        }

    def auth(self):
        try:
            url = "https://quake.360.cn/api/v3/user/info"
            response = requests.get(url, headers=self.headers)
            data = response.json()
                
            if 'code' in data and data['code'] != 0:
                logging.error(f"Incorrect key! Error: {data.get('message')}")
                return False

            logging.info("Quake authentication successful")
            logging.info(f"Username: {data.get('data', {}).get('user_name')}")
            logging.info(f"Remaining credits: {data.get('data', {}).get('month_remaining_credit')}")
            return True
        except Exception as e:
            logging.error(f"Quake authentication failed: {e}")
            return False
    
    def search(self, query, limit=10):
        try:
            url = "https://quake.360.cn/api/v3/search/quake_service"
            encoded_query = quote(query)
            params = {
                "query": encoded_query,
                "size": limit,
                "page": 1
            }
            response = requests.post(url, headers=self.headers, json=params)
            data = response.json()

            if self.verbose:
                logging.info(f"Quake response body: {json.dumps(data, indent=2)}")
            
            if 'code' in data and data['code'] != 0:
                logging.error(f"Quake API error: {data.get('message')}")
                return []
                
            results = []
            for item in data.get("data", []):
                result = {
                    "ip": item.get("ip"),
                    "port": item.get("port"),
                    "title": item.get("service", {}).get("http", {}).get("title"),
                    "domain": item.get("service", {}).get("http", {}).get("host"),
                    "country": item.get("location", {}).get("country_code"),
                    "feed": "quake"
                }
                results.append(result)
            
            logging.info(f"Quake returned {len(results)} results")
            return results

        except Exception as e:
            logging.error(f"Quake search failed: {e}")
            return []