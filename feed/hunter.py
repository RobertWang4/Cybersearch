import json
import requests
import logging
import base64
import time
logging.basicConfig(level=logging.INFO)
time.sleep(3)

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
            query = base64.urlsafe_b64encode('title="Apache"'.encode("utf-8")).decode()
            url = f"https://hunter.qianxin.com/openApi/search?api-key={self.hunter_key}"
            params = {
                "search": query,
                "page": 1,
                "page_size": 1
            }
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()

            if self.verbose:
                logging.info(f"Hunter response body: {data}")

            if data.get("code") != 200:
                logging.error("Incorrect key!")
                return False
            logging.info("Hunter authentication successful")
            logging.info(f"Username: {data.get('data', {}).get('username')}")
            consume_date = data.get('data', {}).get('consume_quota', 0)
            credits = data.get('data', {}).get('rest_quota', 0)
            logging.info(f"Hunter consume credits: {consume_date}")
            logging.info(f"Hunter credits: {credits}")
            return True
        except Exception as e:
            logging.error(f"Hunter authentication failed: {e}")
            return False
    
    def search(self, query, limit=10):
        try:
            url = f"https://hunter.qianxin.com/openApi/search?api-key={self.hunter_key}"
            encode_query = base64.urlsafe_b64encode(query.encode("utf-8")).decode()
            if limit > 100 or limit % 10 != 0:
                logging.warning("Hunter requires page_size to be a multiple of 10 between 10 and 100, adjusting limit")
                if limit % 10 < 5:
                    limit -= limit % 10
                else:
                    limit += 10 - (limit % 10)
                logging.info(f"Adjusted limit to {limit}")
            params = {
                "search": encode_query,
                "page": 1,
                "page_size": limit
            }
            response = requests.get(url, headers=self.headers, params=params)
            data = response.json()

            if self.verbose:
                logging.info(f"Hunter response body: {data}")

            if data.get("code") != 200:
                logging.error(f"Hunter API error: {data.get('message')}")
                return []
            
            results = []
            for item in data.get("data", []).get("arr",[]):
                result = {
                    "ip": item.get("ip"),
                    "port": item.get("port"),
                    "title": item.get("web_title"),
                    "domain": item.get("domain"),
                    "country": item.get("country"),
                    "os": item.get("os"),
                    "banner": item.get("banner"),
                    "province": item.get("province"),
                    "city": item.get("city"),
                    "base_protocol": item.get("base_protocol"),
                    "protocol": item.get("protocol"),
                    "component": item.get("component"),
                    "url": item.get("url"),
                    "updated_at": item.get("updated_at"),
                    "status_code": item.get("status_code"),
                    "number": item.get("number"),
                    "company": item.get("company"),
                    "is_web": item.get("is_web"),
                    "is_risk": item.get("is_risk"),
                    "is_risk_protocol": item.get("is_risk_protocol"),
                    "as_org": item.get("as_org"),
                    "isp": item.get("isp"),
                    "header": item.get("header"),
                    "feed": "hunter"
                }
                results.append(result)
            return results

        except Exception as e:
            logging.error(f"Hunter search failed: {e}")
            return []
