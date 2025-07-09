import re
import json
import csv
import logging
import dicttoxml
import mmh3
import base64
import yaml
from xml.dom.minidom import parseString
import hashlib


def convert(query, platform):
    field_map = {
        "title=": {
            "shodan": "title:",
            "quake": "title:",
            "hunter": "web.title=",
            "daydaymap": "web.title="
        },
        "ip=": {
            "shodan": "ip:",
            "quake": "ip:",
            "hunter": "ip=",
            "daydaymap": "ip="
        },
        "domain=": {
            "quake": "domain:",
            "daydaymap": "domain=",
            "shodan": "hostname: ",
            "hunter": "domain=",
            "quake": "domain:"
        },
        "body=": {
            "shodan": "html:",
            "hunter": "web.body=",
            "daydaymap": "web.body=",
            "quake":"body:"
        },
        'ssl.cert.subject.cn=': {
            'hunter': 'cert.subject=',
            'daydaymap': 'cert.subject.cn=',
            'fofa': 'cert.subject='
        },
        'ssl.cert.issuer.cn=': {
            'hunter': 'cert.issuer_org=',
            'daydaymap': 'cert.issuer.cn=',
            'fofa': 'cert.issuer='
        },
        'ssl.cert.serial=': {
            'hunter': 'cert.serial_number=',
            'daydaymap': 'cert.sn=',
            'fofa': 'cert.serial='
        },
        'ssl.cert.alg=': {
            'hunter': 'cert.sha-256=',
            'daydaymap': 'cert.md5=',
            'fofa': 'cert.alg='  
        },
        'ssl=': {
            'hunter': 'cert=',
            'daydaymap': 'cert.subject=',
            "quake": "cert:",
            "shodan": "ssl.cert.subject.cn:",
            "fofa": "cert="
        },
        "os=": {
            "shodan": "os:",
            "quake": "os:",
            "hunter": "ip.os=",
            "daydaymap": "ip.os="
        },
        "country=": {
            "shodan": "country:",
            "quake": "country:",
            "hunter": "ip.country=",
            "daydaymap": "ip.country="
        },
        "port=": {
            "shodan": "port:",
            "quake": "port:",
            "hunter": "ip.port=",
            "daydaymap": "ip.port="
        },
        "iconhash=": {
            "fofa": "icon_hash=",
            "daydaymap": "web.icon=",
            "hunter": "web.icon=",
            "shodan": "http.favicon.hash:",
            "quake": "favicon:"
        },
        "server=": {
            "hunter": "header.server=",
            "daydaymap": "web.server=",
            "quake": "server:"
        },
        "app=": {
            "hunter": "app=",
            "daydaymap": "app="
        },
        "province=": {
            "hunter": "ip.province=",
            "daydaymap": "ip.province=",
            "quake": "province:"
        },
        "city=": {
            "hunter": "ip.city=",
            "daydaymap": "ip.city=",
            "quake": "city:"
        },
        "isp=": {
            "hunter": "ip.isp=",
            "daydaymap": "ip.isp=",
            "quake": "isp:"
        },
        "http.header.status_code=": {
            "hunter": "header.status_code=",
            "daydaymap": "web.status_code=",
            "quake": "status_code:"
        },

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


def fix_query(query):
    if "=" in query and '"' not in query:
        parts = query.split("=",1)
        if len(parts) == 2:
            field, value = parts
            fix_query = f'{field}="{value}"'
            return fix_query
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



def hash_icon(filepath, hash_type='mmh3'):
    with open(filepath,'rb') as f:
        data = f.read()
        
    if hash_type == 'md5':
        return hashlib.md5(data).hexdigest()
    else:
        b64 = base64.encodebytes(data).decode()
        return mmh3.hash(b64)

def load_config(path):
    with open(path,'r') as f:
        return yaml.safe_load(f)

def convert_fields(fields, engine):
    if engine == "zoomeye":
        converted_fields = []
        for field in fields:
            if field == "country":
                converted_fields.append("country.name")
            else:
                converted_fields.append(field)
        return converted_fields
    return fields

