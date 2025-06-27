import re
import json
import csv
import logging
import dicttoxml
import mmh3
import base64
from xml.dom.minidom import parseString


def convert(query, platform):
    field_map = {
        "title=": {
            "shodan": "title: ",
        },
        "ip=": {
            "shodan": "ip: "
        },
        "site=": {
            "fofa": "domain= ",
            "hunter": "domain=",
            "quake": "host=",
            "daydaymap": "domain=",
            "shodan": "hostname: "
        },
        "body=": {
            "shodan": "html: ",
            "hunter": "content=",
        },
        "cert=": {
            "shodan": "ssl.cert.subject.cn: ",
            "hunter": "cert_info"
        },
        "os=": {
            "shodan": "os: ",
        },
        "country=": {
            "shodan": "country: ",
            "quake": "location.country_code="
        },
        "port=": {
            "shodan": "port: ",
            "quake": "port="
        },
        "icon_hash=":{
            "shodan":"http.favicon.hash:"
        }
    }
    for old, platform_map in field_map.items():
        if platform in platform_map:
            query = query.replace(old, platform_map[platform])

    if platform == "fofa":
        query = query.replace(" AND ", " && ").replace(" NOT ", " !")
    elif platform == "hunter" or platform == "daydaymap":
        pass
    elif platform == "shodan":
        query = re.sub(r'http\.favicon\.hash:"([^"]+)"', r'http.favicon.hash:\1', query)
        query = query.replace(" AND ", " ").replace(" NOT ", " -")
    elif platform == "quake":
        query = query.replace(" AND ", " ")
        query = re.sub(r'-\w+="[^"]+"', '', query).strip()      
    return query



def save_results(results, output_format, output_file):
    if not results:
        logging.warning("No results to save")
        return

    try:
        if output_format == "json":
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False)
        elif output_format == "csv":
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        elif output_format == "xlsx":
            import pandas as pd
            df = pd.DataFrame(results)
            df.to_excel(output_file, index=False, engine='openpyxl')
        elif output_format == "txt":
            with open(output_file, "w") as f:
                for i, result in enumerate(results):
                    f.write(f"Record {i+1}:\n")
                    for key, value in result.items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
        elif output_format == "xml":
            with open(output_file, "w") as f:
                xml = dicttoxml.dicttoxml(results, custom_root="results", attr_type=False)
                xml = parseString(xml).toprettyxml()
                f.write(xml)
    except Exception as e:
        logging.error(f"Error when saving results to {output_file}: {e}")



def hash_icon(filepath):
    with open(filepath,'rb') as f:
        data = f.read()
        b64 = base64.encodebytes(data).decode()
        return mmh3.hash(b64)
