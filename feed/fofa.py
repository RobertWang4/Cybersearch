import json
import logging
import base64
import requests

class Fofa:

    def __init__(self,fofa_email,fofa_key,verbose=False):
        self.fofa_email = fofa_email
        self.fofa_key = fofa_key
        self.verbose = verbose
        self.headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0"
        }

    def auth(self):
        try:
            url = f"https://fofa.info/api/v1/info/my?email={self.fofa_email}&key={self.fofa_key}"
            response = requests.get(url,headers=self.headers)
            data = response.json()
            logging.debug(f"FOFA response body: {data}")

            if 'error' in data:
                logging.error("Incorrect key!")
                return False
            logging.info("FOFA authentication successful")
            logging.info(f"FOFA coin:{data.get('fcoin')}")
            return True
        
        except Exception as e:
            logging.error(f"FOFA authentication failed: {e}")
            return False
        
    def search(self,query,limit=10):
        results = []
        try:
            encoded_query = base64.b64encode(query.encode()).decode()
            url = f"https://fofa.info/api/v1/search/all?email={self.fofa_email}&key={self.fofa_key}&qbase64={encoded_query}&size={limit}"
            response = requests.get(url, headers=self.headers)
            data = response.json()

            if self.verbose:
                logging.debug(f"FOFA response: {response.json()}")


            for item in data.get("result",[]):
                result={
                    "ip": item.get("ip"),
                    "port": item.get("portinfo", {}).get("port"),
                    "title": item.get("title", [None])[0] if item.get("title") else None,
                    "domain": item.get("hostname"),
                    "country": item.get("geoinfo", {}).get("country", {}).get("code"),
                    "feed":"fofa"
                }
                results.append(result)
                return results
            
        except Exception as e:
            logging.error(f"FOFA search failed: {e}")
            return []
       