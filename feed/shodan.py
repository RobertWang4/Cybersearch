import json
import logging
import requests
from urllib.parse import quote

class Shodan:

    def __init__(self,api_key,verbose=False):
        self.api_key = api_key
        self.verbose = verbose
        self.headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0"
        }

    def auth(self):
        try:
            url =f"https://api.shodan.io/api-info?key={self.api_key}"
            response = requests.get(url,headers=self.headers)
            data = response.json()
            
            if "error" in data:
                logging.error(f"Shodan API error: {data['error']}")
                return False
            
            logging.info("Shodan authentication successful")
            credits = data.get("query_credits",0)
            logging.info(f"Shodan query credits:{credits}")
            return credits > 0
        
        except Exception as e:
            logging.error(f"Shodan authentication failed : {e}")
            return False
        

        
    def search(self,query,limit=10):
        results=[]
        try:
            encode_query = quote(query)
            url = f"https://api.shodan.io/shodan/host/search?key={self.api_key}&query={encode_query}size={limit}"
            response = requests.get(url, headers=self.headers)
            data = response.json()

            if self.verbose:
                logging.debug(f"Shodan response: {response.json()}")
 

            for item in data.get("matches",[]):
                result={
                    "ip": item.get("ip_str"),  # 使用ip_str而不是ip
                    "port": item.get("port"),  # port直接在item中
                    "title": item.get("http", {}).get("title"),  # title在http对象中
                    "domain": item.get("hostnames", [None])[0] if item.get("hostnames") else None,  # 从hostnames数组获取第一个
                    "country": item.get("location", {}).get("country_code"),  # country_code在location中
                    "feed": "shodan"
                }
                results.append(result)
            return results

        except Exception as e:
            logging.error(f"Shodan search failed: {e}")
            return []
