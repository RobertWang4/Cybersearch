import json
import requests
import logging

class Quake:
    def __init__(self, quake_key, verbose=False):
        self.quake_key = quake_key
        self.verbose = verbose
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
            "Accept": "application/json",
            "X-QuakeToken": self.quake_key
        }
        self.points = {}
        self.info = { 
            "feed": "quake",
        }

    def auth(self):
        try:
            url = "https://quake.360.net/api/v3/user/info"
            response = requests.get(url, headers=self.headers)
            data = response.json()

            if self.verbose:
                logging.info(f"Quake response body: {json.dumps(data, indent=2)}")

            if 'code' in data and data['code'] != 0:
                logging.error(f"Incorrect key! Error: {data.get('message')}")
                return False

            logging.info("Quake authentication successful")
            credits = data.get('data', {}).get('credit')
            persistent_credit = data.get('data', {}).get('persistent_credit')
            self.points = {
                "feed": "quake",
                "credit": credits,
                "persistent_credit": persistent_credit,
            }
            self.info = {
                "feed": "quake",
                "status": "success",
                "username": data.get('data', {}).get('user', {}).get('username'),
                "fullname": data.get('data', {}).get('user', {}).get('fullname'),
                "id": data.get('data', {}).get('user', {}).get('id'),
                "email": data.get('data', {}).get('user',{}).get("email"),
                "mobile": data.get('data', {}).get('mobile_phone'),
                "role": data.get('data', {}).get('role'),
                "credits": credits,
                "persistent_credit": persistent_credit,
            }
            return True
        except Exception as e:
            logging.error(f"Quake authentication failed: {e}")
            return False
    
    def search(self, query, limit=10):
        try:
            url = "https://quake.360.net/api/v3/search/quake_service"
            
            params = {
                "query": query,
                "size": limit,
                "page": 1
            }
            response = requests.post(url, headers=self.headers, json=params)
            data = response.json()
    
            if self.verbose:
                logging.info(f"Quake search query: {query}")
                logging.info(f"Quake response body: {json.dumps(data, indent=2)}")
            
            if 'code' in data and data['code'] != 0:
                logging.error(f"Quake API error: {data.get('message')}")
                return []
                
            results = []
            for item in data.get("data", []):
                result = {
                    "ip": item.get("ip"),
                    "port": item.get("services", [{}])[0].get("port"),
                    "title": None,
                    "domain": item.get("domain"),
                    "country": item.get("location", {}).get("country_code"),
                    "org": item.get("location", {}).get("asname"),
                    "location": {
                        "country": item.get("location", {}).get("country_en"),
                        "country_cn": item.get("location", {}).get("country_cn"),
                        "province": item.get("location", {}).get("province_en"),
                        "province_cn": item.get("location", {}).get("province_cn"),
                        "city": item.get("location", {}).get("city_en"),
                        "city_cn": item.get("location", {}).get("city_cn"),
                        "district": item.get("location", {}).get("district_en"),
                        "district_cn": item.get("location", {}).get("district_cn"),
                        "isp": item.get("location", {}).get("isp"),
                        "scene": item.get("location", {}).get("scene_en"),
                        "scene_cn": item.get("location", {}).get("scene_cn"),
                        "gps": item.get("location", {}).get("gps"),
                        "radius": item.get("location", {}).get("radius")
                    },
                    "feed": "quake"
                }
                results.append(result)
            
            logging.info(f"Quake returned {len(results)} results")
            return results
    
        except Exception as e:
            logging.error(f"Quake search failed: {e}")
            return []