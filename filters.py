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
