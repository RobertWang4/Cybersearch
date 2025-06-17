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
                logging.debug(f"FOFA response: {json.dumps(data, indent=2)}")

            if 'error' in data:
                logging.error(f"FOFA API error: {data.get('error')}")
                return []

            for item in data.get("results",[]):
                if not isinstance(item, list) or len(item) < 6:
                    continue
                    
                result = {
                    "ip": item[0],
                    "port": item[1],
                    "title": item[2],
                    "domain": item[3],
                    "country": item[4],
                    "feed": "fofa"
                }
                results.append(result)
                
            # 记录结果数量
            logging.info(f"FOFA返回了 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"FOFA search failed: {e}")
            return []
