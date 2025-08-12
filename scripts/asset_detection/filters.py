def apply_field_filter(results, fields=None):
    if not fields:
        return results
    
    filtered = []

    for item in results:
        new_item =  {key:item.get(key) for key in fields if key in item}
        if "feed" in item:
            new_item["feed"] = item["feed"]
        filtered.append(new_item)

    return filtered


def match_filters(record,filters):

    if "country" in filters:
        if record.get("country") != filters["country"]:
            return False
    
    if "title_contains" in filters:
        title = record.get("title")
        if not title or filters["title_contains"] not in title:
            return False
    
    if "domain_contains" in filters:
        domain = record.get("domain")
        if not domain or filters["domain_contains"] not in domain:
            return False

    if "port_in" in filters:
        try:
            port = record.get("port")
            if port is not None:
                port_int = int(port)  
                if port_int not in filters["port_in"]:
                    return False
            else:
                return False  
        except (ValueError, TypeError):
            return False 
    
    return True


def filter_results(results,filters):
    return [r for r in results if match_filters(r,filters)]