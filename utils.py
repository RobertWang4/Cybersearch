import re

def convert(query,platform):
    field_map = {
        "title=": {
            "shodan" : "title: ",
            "hunter" : "web_title=",
        },
        "ip=": {
            "shodan" : "ip: "
        },
        "site=": {
            "fofa" : "domain= ",
            "hunter" : "domain=",
            "quake" : "host=",
            "daydaymap" : "domain=",
            "shodan" : "hostname: "
        },
        "body=": {
            "shodan" : "html: ",
            "hunter" : "content=",
        },
        "cert=": {
            "shodan" : "ssl.cert.subject.cn: ",
            "hunter":"cert_info"
        },
        "os=": {
            "shodan" : "os: ",
        },
        "country=" : {
            "shodan" : "country: ",
            "quake" : "location.country_code="
        },
        "port=": {
            "shodan" : "port: ",
            "quake" : "port="
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
        query = query.replace(" AND ", " ").replace(" NOT ", " -")
    elif platform == "quake":
        query = query.replace(" AND ", " ")
        query = re.sub(r'-\w+="[^"]+"', '', query).strip()

    return query
