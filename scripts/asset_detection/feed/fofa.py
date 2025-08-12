import json
import logging
import base64
import requests

class Fofa:

    def __init__(self,fofa_key,verbose=False,fields=["ip", "port", "title"]):
        self.fofa_key = fofa_key
        self.verbose = verbose
        self.fields = fields
        self.points = {}
        self.info = { 
            "feed": "fofa",
        }

    def auth(self):
        try:
            url = f"https://fofa.info/api/v1/info/my?key={self.fofa_key}"
            response = requests.get(url)
            data = response.json()

            if self.verbose:
                logging.info(f"FOFA response: {data}")
                
            if data.get("error") != False:
                logging.error("Incorrect key!")
                return False
            logging.info("FOFA authentication successful")

            is_vip = data.get("isvip", False)
            points = data.get("remain_api_query", 0)
            
            if is_vip:
                logging.info("FOFA VIP user")
            else:
                logging.info("FOFA free user")
            self.points = {
                "feed": "fofa",
                "fcoin": data.get("fcoin", 0),
                "fofa_point": data.get("fofa_point", 0),
                "remain_free_point": data.get("remain_free_point", 0),
                "remain_api_query": points,
                "remain_api_data": data.get("remain_api_data", 0),
            }
            self.info = {
                "feed": "fofa",
                "status": "success",
                "email": data.get("email"),
                "username": data.get("username"),
                "category": data.get("category"),
                "fcoin": data.get("fcoin", 0),
                "fofa_point": data.get("fofa_point", 0),
                "remain_free_point": data.get("remain_free_point", 0),
                "remain_api_query": points,
                "remain_api_data": data.get("remain_api_data", 0),
                "isvip": is_vip,
                "vip_level": data.get("vip_level", 0),
                "is_verified": data.get("is_verified", False),
                "avatar": data.get("avatar"),
                "message": data.get("message", ""),
                "fofacli_ver": data.get("fofacli_ver"),
                "fofa_server": data.get("fofa_server", False)
            }
            return True
        
        except Exception as e:
            logging.error(f"FOFA authentication failed: {e}")
            return False
        
    def search(self, query, limit=10):
        results = []
        try:
            encoded_query = base64.b64encode(query.encode()).decode()
            url = f"https://fofa.info/api/v1/search/all?&key={self.fofa_key}&qbase64={encoded_query}&size={limit}&fields={','.join(self.fields)}"
            response = requests.get(url)
            data = response.json()

            if self.verbose:
                logging.debug(f"FOFA response: {json.dumps(data, indent=2)}")

            if data.get("error") != False:
                logging.error(f"FOFA API error: {data.get('error')}")
                return []

            for item in data.get("results",[]):
                record = {}
                for i in range(min(len(self.fields), len(item))):
                    record[self.fields[i]] = item[i]
                record["feed"] = "fofa"
                results.append(record)
                
            # 记录结果数量
            logging.info(f"FOFA返回了 {len(results)} 条结果")
            return results
            
        except Exception as e:
            logging.error(f"FOFA search failed: {e}")
            return []
