import requests
import json
import logging
import base64

class Zoomeye:
    def __init__(self, zoomeye_api_key, verbose=False, fields=["ip","port","domain","title","country.name"]):
        self.zoomeye_api_key = zoomeye_api_key
        self.verbose = verbose
        self.zoomeye_api_key = zoomeye_api_key
        self.fieldss =fields
        self.points = 0
        self.zoomeye_points = 0

    def auth(self):
        try:
            url = "https://api.zoomeye.org/v2/userinfo"
            headers = {
            "User-Agent": "Mozilla/5.0",
            "API-KEY": self.zoomeye_api_key
        }
            response = requests.post(url, headers=headers)

            if response.status_code != 200:
                logging.error(f"ZoomEye auth API returned status code: {response.status_code}")
                logging.error(f"Response: {response.text}")
                return False

            response_json = response.json()
            if self.verbose:
                logging.debug(f"Zoomeye response body: {json.dumps(response_json, indent=2)}")

            if response_json.get("code") != 60000:
                logging.error("ZoomEye auth failed or key invalid")
                return False

            logging.info("ZoomEye authentication successful")
            data = response_json.get("data", {})
            subscription = data.get("subscription", {})
            self.points = subscription.get("points")
            self.zoomeye_points = subscription.get("zoomeye_points")
            logging.info(f"Username: {data.get('username')}")
            logging.info(f"Remaining points: {self.points}")
            logging.info(f"Zoomeye points: {self.zoomeye_points}")
            return True

        except Exception as e:
            logging.error(f"Exception during ZoomEye authentication: {e}")
            return False

    
    def search(self, query, limit=10):
        results = []
        encoded_query = base64.b64encode(query.encode()).decode()
        
        page_size = min(limit, 20)
        total_pages = (limit + page_size - 1) // page_size
        
        headers = {
            "Content-Type": "application/json",
            "API-KEY": self.zoomeye_api_key,
        }
        url = "https://api.zoomeye.org/v2/search"
    
        try:
            for page in range(1, total_pages + 1):
                remaining = limit - len(results)
                current_size = min(page_size, remaining)
                
                data = {
                    "qbase64": encoded_query,
                    "page": page,
                    "size": current_size,
                    "fields": ",".join(self.fieldss)
                }
                
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code != 200:
                    logging.error(f"ZoomEye search API returned status code: {response.status_code}")
                    logging.error(f"Response: {response.text}")
                    break
                    
                response_data = response.json()
            
                if self.verbose:
                    logging.debug(f"Page {page} response from ZoomEye:\n" + json.dumps(response_data, indent=2, ensure_ascii=False))
            
                matches = response_data.get("data", [])
                
                if not matches:
                    break
                    
                for item in matches:
                    if len(results) >= limit:
                        break
                    record = {
                        "url": item.get("url"),
                        "ssl.jarm": item.get("ssl", {}).get("jarm"),
                        "ssl.ja3s": item.get("ssl", {}).get("ja3s"), 
                        "iconhash_md5": item.get("iconhash_md5"),
                        "robots_md5": item.get("robots_md5"),
                        "security_md5": item.get("security_md5"),
                        "ip": item.get("ip"),
                        "domain": item.get("domain"),
                        "hostname": item.get("hostname"),
                        "os": item.get("os"),
                        "port": item.get("port"),
                        "service": item.get("service"),
                        "title": (
                            ", ".join(item.get("title", [])) 
                            if isinstance(item.get("title"), list) 
                            else str(item.get("title", ""))
                        ),
                        "version": item.get("version"),
                        "device": item.get("device"),
                        "rdns": item.get("rdns"),
                        "product": item.get("product"),
                        "header": item.get("header"),
                        "header_hash": item.get("header_hash"),
                        "body": item.get("body"),
                        "body_hash": item.get("body_hash"),
                        "banner": item.get("banner"),
                        "update_time": item.get("update_time"),
                        "header.server.name": item.get("header.server.name"),
                        "header.server.version": item.get("header.server.version"), 
                        "continent.name": item.get("continent.name"),
                        "country": item.get("country.name"),
                        "province.name": item.get("province.name"),
                        "city.name": item.get("city.name"),
                        "lon": item.get("lon"),
                        "lat": item.get("lat"),
                        "isp.name": item.get("isp.name"),
                        "organization.name": item.get("organization.name"),
                        "zipcode": item.get("zipcode"),
                        "idc": item.get("idc"),
                        "honeypot": item.get("honeypot"),
                        "asn": item.get("asn"),
                        "protocol": item.get("protocol"),
                        "ssl": item.get("ssl"),
                        "primary_industry": item.get("primary_industry"),
                        "sub_industry": item.get("sub_industry"),
                        "rank": item.get("rank"),
                        "feed": "zoomeye"
                    }
                    results.append(record)
                    
                if len(results) >= limit:
                        break
            
            return results
        
        except Exception as e:
            logging.error(f"Zoomeye search failed: {e}")
            return []