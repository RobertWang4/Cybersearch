import json
import requests
import logging
import base64

class DayDayMap:
    def __init__(self, daydaymap_key, verbose=False):
        self.daydaymap_key = daydaymap_key
        self.verbose = verbose
        self.headers = {
            'api-key': self.daydaymap_key
        }

    def auth(self):
        try:
            url = "https://www.daydaymap.com/api/v1/raymap/search/all"
            encoded_quota = base64.b64encode('title="Apache"'.encode()).decode()
            params = {
                "page": 1,
                "page_size": 1,
                "keyword": encoded_quota,
            }
            response = requests.post(url, headers=self.headers, json=params, verify=False)
            data = response.json()
                
            if 'error' in data or data.get('code') != 200:
                logging.error(f"DayDayMap API error: {data.get('message', 'Unknown error')}")
                return False

            logging.info("DayDayMap authentication successful")
            return True

        except Exception as e:
            logging.error(f"DayDayMap authentication failed: {e}")
            return False
    
    
    def search(self, query, limit=10):
        try:
            encoded_quota = base64.b64encode(query.encode()).decode()
            params = {
                "page": 1,
                "page_size": limit,
                "keyword": encoded_quota             
            }
            url = "https://www.daydaymap.com/api/v1/raymap/search/all"
           
            response = requests.post(url, headers=self.headers, json=params, verify=False)
            data = response.json()

            if self.verbose:
                logging.info(f"DayDayMap response body: {json.dumps(data, indent=2)}")
            
            if 'error' in data or data.get('code') != 200:
                logging.error(f"DayDayMap API error: {data.get('message', 'Unknown error')}")
                return []
                
            results = []
            for item in data.get("data", {}).get("list", []):
                result = {
                    "ip": item.get("ip", ""),
                    "port": item.get("port", ""),
                    "title": item.get("title", "").strip(),
                    "domain": item.get("domain", ""), 
                    "country": item.get("country", "").strip(),
                    "feed": "daydaymap"
                }
                results.append(result)
            
            logging.info(f"DayDayMap returned {len(results)} results")
            return results

        except Exception as e:
            logging.error(f"DayDayMap search failed: {e}")
            return []