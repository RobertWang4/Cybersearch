from curses import keyname
import requests
import base64
import logging
import json
logging.basicConfig(level=logging.INFO)


def search(query, limit=10, fields=["ip", "port", "title"]):
    key = "b41bad5a1b924e6d4145f09fdcec66d6"
    try:
        encoded_query = base64.b64encode(query.encode()).decode()
        url = f"https://fofa.info/api/v1/search/all?&key={key}&qbase64={encoded_query}&size={limit}&fields={','.join(fields)}"
        response = requests.get(url)
        data = response.json()

        
        logging.debug(f"FOFA response: {data}")

        if data.get("error") != False:
            logging.error(f"FOFA API error: {data.get('error')}")
            return []

        results = []
        for item in data.get("results", []):
            record = {}
            for i in range(min(len(fields), len(item))):
                record[fields[i]] = item[i]
            record["feed"] = "fofa"
            results.append(record)

            
        # 记录结果数量
        logging.info(f"FOFA返回了 {len(results)} 条结果")
        return results
        
    except Exception as e:
        logging.error(f"FOFA search failed: {e}")
        return []


print(search('title="Apache"', limit=13))
