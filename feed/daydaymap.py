import json
import requests
import logging
from urllib.parse import quote

class DayDayMap:
    def __init__(self, daydaymap_key, verbose=False):
        self.daydaymap_key = daydaymap_key
        self.verbose = verbose
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.daydaymap_key}"
        }

    def auth(self):
        try:
            url = "https://www.daydaymap.com/api/v1/user/info"  # 假设的API端点
            response = requests.get(url, headers=self.headers)
            data = response.json()
            logging.debug(f"DayDayMap response body: {data}")
                
            if 'error' in data or response.status_code != 200:
                logging.error(f"Incorrect key! Error: {data.get('message', 'Unknown error')}")
                return False

            logging.info("DayDayMap authentication successful")
            logging.info(f"Username: {data.get('data', {}).get('username')}")
            credits = data.get('data', {}).get('credits', 0)
            logging.info(f"DayDayMap credits: {credits}")
            return True

        except Exception as e:
            logging.error(f"DayDayMap authentication failed: {e}")
            return False
    
    
    def search(self, query, limit=10):
        try:
            url = "https://www.daydaymap.com/api/v1/search"  # 假设的API端点
            encoded_query = quote(query)
            params = {
                "query": encoded_query,
                "size": limit,
                "page": 1
            }
            response = requests.post(url, headers=self.headers, json=params)
            data = response.json()

            if self.verbose:
                logging.info(f"DayDayMap response body: {json.dumps(data, indent=2)}")
            
            if 'error' in data or response.status_code != 200:
                logging.error(f"DayDayMap API error: {data.get('message', 'Unknown error')}")
                return []
                
            results = []
            for item in data.get("data", {}).get("items", []):
                result = {
                    "ip": item.get("ip"),
                    "port": item.get("port"),
                    "title": item.get("title"),
                    "domain": item.get("domain"),
                    "country": item.get("country"),
                    "feed": "daydaymap"
                }
                results.append(result)
            
            logging.info(f"DayDayMap returned {len(results)} results")
            return results

        except Exception as e:
            logging.error(f"DayDayMap search failed: {e}")
            return []