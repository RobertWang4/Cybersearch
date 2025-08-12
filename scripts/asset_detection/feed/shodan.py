import json
import logging
from shodan import Shodan


class ShodanEngine:

    def __init__(self, api_key, verbose=False):
        self.api_key = api_key
        self.verbose = verbose
        self.points = {}
        self.info = { 
            "feed": "shodan",
        }

    def auth(self):
        try:
            response = Shodan(self.api_key).info()

            if self.verbose:
                logging.debug(f"Shodan response: {response}")

            if "error" in response:
                logging.error(f"Shodan API error: {response['error']}")
                return False
            
            logging.info("Shodan authentication successful")
            logging.info(f"Your account plan is {response.get('plan')}")
            credits = response.get("query_credits", 0)
            self.points = {
                "feed": "shodan",
                "query_credits": credits,
            }
            self.info = {
                "feed": "shodan",
                "status": "success",
                "query_credits": credits,
                "unlocked": response.get("unlocked"),
                "plan": response.get("plan"),
                "monitored_ips": response.get("monitored_ips", 0)
            }
            if credits <= 0:
                logging.warning("Shodan points are not enough!")
                return False
            return True
        
        except Exception as e:
            logging.error(f"Shodan authentication failed : {e}")
            return False
        

        
    def search(self,query,limit=10):
        results=[]
        try:
            api = Shodan(self.api_key)
            data = api.search(query, limit=limit)
            
            if self.verbose:
                logging.debug(f"Shodan response: {json.dumps(data, indent=2)}")
            

            if "error" in data:
                logging.error(f"Shodan search API error: {data['error']}")
                return []
        
            for item in data.get("matches",[]):
                result={
                    "ip": item.get("ip_str"),
                    "port": item.get("port"),
                    "title": item.get("http", {}).get("title"),
                    "domain": item.get("hostnames", [None])[0] if item.get("hostnames") else None,
                    "country": item.get("location", {}).get("country_code"),
                    "org": item.get("org"),
                    "os": item.get("os"),
                    "data": item.get("data"),
                    "banner": item.get("banner"),
                    "feed": "shodan"
                }
                results.append(result)
            return results
        
        except Exception as e:
            logging.error(f"Shodan search failed: {e}")
            return []
