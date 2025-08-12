import json
import requests
import logging
import base64
import urllib3
import warnings

class DayDayMap:
    def __init__(self, daydaymap_key, verbose=False, verify_ssl=False):
        self.daydaymap_key = daydaymap_key
        self.verbose = verbose
        self.verify_ssl = verify_ssl
        self.info = { 
            "feed": "daydaymap",
        }
 
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')
            requests.packages.urllib3.disable_warnings()
            
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
            response = requests.post(url, headers=self.headers, json=params, verify=self.verify_ssl)
            data = response.json()

            if self.verbose:
                logging.info(f"DayDayMap response body: {json.dumps(data, indent=2)}")
                
            if 'error' in data or data.get('code') != 200:
                logging.error(f"DayDayMap API error {response.status_code}: {data.get('msg', 'Unknown error')}")
                return False

            logging.info("DayDayMap authentication successful")
            self.info = {
                "feed": "daydaymap",
                "status": "success"
            }
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
                logging.error(f"DayDayMap API error {response.status_code}: {data.get('msg', 'Unknown error')}")
                return []
                
            results = []
            for item in data.get("data", {}).get("list", []):
                result = {
                    "asn": item.get("asn"),
                    "asn_org": item.get("asn_org"),
                    "banner": item.get("banner", ""),
                    "cert": item.get("cert"),
                    "cert_selfsigned": item.get("cert_selfsigned"),
                    "city": item.get("city"),
                    "country": item.get("country"),
                    "device": item.get("device"),
                    "domain": item.get("domain"),
                    "header": item.get("header"),
                    "icp_reg_name": item.get("icp_reg_name"),
                    "industry": item.get("industry", []),
                    "ip": item.get("ip"),
                    "is_ipv6": item.get("is_ipv6"),
                    "is_website": item.get("is_website"),
                    "isp": item.get("isp"),
                    "lang": item.get("lang"),
                    "os": item.get("os"),
                    "port": item.get("port"),
                    "product": item.get("product", []),
                    "protocol": item.get("protocol"),
                    "province": item.get("province"),
                    "server": item.get("server"),
                    "service": item.get("service"),
                    "tags": item.get("tags", []),
                    "time_stamp": item.get("time_stamp"),
                    "title": item.get("title"),
                    "feed": "daydaymap"
                }
                results.append(result)
            logging.info(f"DayDayMap returned {len(results)} results")
            return results

        except Exception as e:
            logging.error(f"DayDayMap search failed: {e}")
            return []