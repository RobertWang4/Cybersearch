import json
import requests
import logging

class Hunter:
    def __init__(self, hunter_key, verbose=False):
        self.hunter_key = hunter_key
        self.verbose = verbose
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "application/json",
            "X-Api-Key": self.hunter_key
        }

    def auth(self):
        try:
            url = "https://hunter.qianxin.com/openApi/api/v2/account/info"
            response = requests.get(url, headers=self.headers)
            data = response.json()
            logging.debug(f"Hunter response body: {data}")
                
            if 'error' in data:
                logging.error("Incorrect key!")
                return False
            logging.info("Hunter authentication successful")
            logging.info(f"Username: {data.get('data', {}).get('username')}")
            credits = data.get('data', {}).get('rest_quota', 0)
            logging.info(f"Hunter credits: {credits}")
            return True
        except Exception as e:
            logging.error(f"Hunter authentication failed: {e}")
            return False
    
    def search(self, query, limit=10):
        try:
            url = "https://hunter.qianxin.com/openApi/api/v2/domain/search"
            params = {
                "query": query,
                "page": 1,
                "page_size": limit
            }
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()

            if self.verbose:
                logging.info(f"Hunter response body: {data}")
            
            results = []
            for item in data.get("data", []):
                result = {
                    "ip": item.get("ip"),
                    "port": item.get("portinfo", {}).get("port"),
                    "title": item.get("web_title"),  
                    "domain": item.get("domain"),    
                    "country": item.get("country"),  
                    "feed": "hunter"                
                }
                results.append(result)
            return results

        except Exception as e:
            logging.error(f"Hunter search failed: {e}")
            return []
