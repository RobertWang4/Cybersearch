import argparse
import logging
import utils
import sys
import json
import select
from config import CONFIG       
from feed.fofa import Fofa 
from feed.shodan import Shodan
from feed.zoomeye import Zoomeye
from feed.hunter import Hunter
from feed.quake import Quake
from feed.daydaymap import DayDayMap
from filters import apply_field_filter,filter_results


parser = argparse.ArgumentParser(description="Cybersearch - Aggregated Search Tool (Beta)")

parser.add_argument("--query", required=False, help="Search keyword (e.g. title='Apache')")
parser.add_argument("--limit", type=int, default=10, help="Number of results to return (default 10)")
parser.add_argument("--fields",default="ip,port,title,domain,country", help="Output fields, comma separated, e.g. ip,port,title")
parser.add_argument("--verbose", default=False, action="store_true", help="Enable debug output")
parser.add_argument("--icon", help="Icon hash to search(.icon)")
parser.add_argument("--config", type=str, help="Path to config file")
parser.add_argument(
    "--engine",
    type=str,
    default="all",
    help="Specify search engine (fofa, zoomeye, hunter, quake, shodan, daydaymap, or all)"
)
parser.add_argument(
    "--input",
    type=str,
    help="Path to txt file with list of queries"
)
parser.add_argument(
    "--output",
    type=str,
    help="Output file name and format (json, csv, or xml)"
)
parser.add_argument("--show-fields", action="store_true", help="显示各个搜索引擎支持的字段")

args = parser.parse_args()


if args.show_fields:
    print("\n=== 各平台支持的字段 ===")
    print("\n=== 各搜索引擎支持的字段 ===")
    
    engine_fields = {
        "zoomeye": ["ip", "domain", "title", "port", "country.name", "city", "ssl", "http.body", "http.favicon.hash", "org", "url", "ssl.jarm", "ssl.ja3s", "iconhash_md5", "robots_md5", "security_md5", "hostname", "os", "service", "version", "device", "rdns", "product", "header", "header_hash", "body", "body_hash", "banner", "update_time", "header.server.name", "header.server.version", "continent.name", "province.name", "city.name", "lon", "lat", "isp.name", "organization.name", "zipcode", "idc", "honeypot", "asn", "protocol", "primary_industry", "sub_industry", "rank"],
        "fofa": ["ip", "port", "protocol", "country", "country_name", "region", "city", "longitude", "latitude", "asn", "org", "host", "domain", "os", "server", "icp", "title", "jarm", "header", "banner", "cert", "base_protocol", "link", "cert.issuer.org", "cert.issuer.cn", "cert.subject.org", "cert.subject.cn", "tls.ja3s", "tls.version", "cert.sn", "cert.not_before", "cert.not_after", "cert.domain", "header_hash", "banner_hash", "banner_fid", "cname", "lastupdatetime", "product", "product_category", "product.version", "icon_hash", "cert.is_valid", "cname_domain", "body", "cert.is_match", "cert.is_equal", "icon", "fid", "structinfo"],
        "shodan": ["ip", "port", "title", "domain", "country", "city", "org", "os", "html", "ssl.cert.subject.cn", "http.favicon.hash"],
        "hunter": ["ip", "port", "title", "domain", "country", "city", "os", "banner", "province", "base_protocol", "protocol", "component", "url", "updated_at", "status_code", "number", "company", "is_web", "is_risk", "is_risk_protocol", "as_org", "isp", "header"],
        "quake": ["ip", "port", "title", "domain", "country", "city", "org", "os", "cert", "favicon", "service", "transport", "response", "components", "asn"],
        "daydaymap": ["ip", "port", "title", "domain", "country", "city", "province", "isp", "os", "cert", "header", "server", "product", "service", "protocol", "is_website", "is_ipv6", "time_stamp", "tags", "lang"]
    }
    
    for engine, fields in engine_fields.items():
        print(f"\n{engine.upper()}:")
        print(f"  默认字段: {', '.join(fields[:5])}")
        print(f"  所有字段: {', '.join(fields)}")
        print(f"  使用示例: --fields {','.join(fields[:3])} --engine {engine}")
    
    print("\n=== 通用字段说明 ===")
    field_descriptions = {
        "ip": "IP地址",
        "port": "端口号", 
        "title": "网页标题",
        "domain": "域名",
        "country": "国家",
        "city": "城市",
        "os": "操作系统",
        "body": "网页内容",
    }
    
    for field, desc in field_descriptions.items():
        print(f"  {field}: {desc}")
    
    print("\n=== 使用示例 ===")
    print("  显示基本信息: --fields ip,port,domain,title")
    print("  显示详细信息: --fields ip,port,title,domain,country,city,os")
    print("  显示所有字段: --fields ip,port,title,domain,country,city,os")
    sys.exit(0)


log_level = logging.DEBUG if args.verbose else logging.INFO

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=log_level,
    format='%(levelname)s:%(name)s:%(message)s',
    stream=sys.stdout
)


if not args.query and not args.input and not args.icon:
    if not sys.stdin.isatty() or select.select([sys.stdin], [], [], 0.1)[0]:
        args.query = sys.stdin.read().strip()

filters = {}
if args.config:
    config = utils.load_config(args.config)
    if config is None:
        raise ValueError(f"Failed to load config file, please check if the path is correct: {args.config}")
    if "filter" in config:
        filters = config.get("filter",{})
    if "engine" in config:
        args.engine = config["engine"]
    if "limit" in config:
        args.limit = config["limit"]
    if "fields" in config:
        args.fields = config["fields"]
    if "verbose" in config:
        args.verbose = config["verbose"]
    if not args.icon and "icon" in config:
        args.icon = config["icon"]
    if not args.input and "input" in config:
        args.input = config["input"]
    if not args.output and "output" in config:
        args.output = config["output"]
    if not args.query and "query" in config:
        args.query = config["query"]
        
if not args.query and not args.input and not args.icon:
    print("Error: Please provide either --query or --input parameter")
    sys.exit(1)

if args.fields:
    fields = args.fields.split(",")
    fofa = Fofa(CONFIG.get("fofa_api_key"), args.verbose, fields=fields)
    zoomeye = Zoomeye(CONFIG.get("zoomeye_api_key"), args.verbose, fields=utils.convert_fields(fields,"zoomeye"))
else:
    fofa = Fofa(CONFIG.get("fofa_api_key"), args.verbose)
    zoomeye = Zoomeye(CONFIG.get("zoomeye_api_key"), args.verbose)
    

engines = {
    "zoomeye": zoomeye,
    "hunter": Hunter(CONFIG.get("hunter_api_key"), args.verbose),
    "fofa": fofa,
    "shodan": Shodan(CONFIG.get("shodan_api_key"), args.verbose),
    "quake": Quake(CONFIG.get("quake_api_key"), args.verbose),
    "daydaymap":DayDayMap(CONFIG.get("daydaymap_api_key"), args.verbose),
}


convertible_engines = {"fofa", "shodan", "hunter", "quake", "daydaymap","zoomeye"}

selected_engine = args.engine.split(",")

if "all" in selected_engine:
    platforms = list(engines.values())
else:
    invalid = [name for name in selected_engine if name not in engines]
    if invalid:
        logging.warning(f"Unknown engines specified: {', '.join(invalid)}")
    
    platforms = [engines[name] for name in selected_engine if name in engines]


def run_search(platforms=platforms, query=args.query):
    results = []

    for engine in platforms:
        logging.info(f"Attempting to use platform: {engine}")
        if not engine.auth():
            logging.warning(f"{engine} authentication failed, skipping")
            continue

        # 最简洁的查询转换逻辑
        engine_name = next((name for name, obj in engines.items() if obj == engine), None)
        engine_query = utils.convert(query, engine_name) if engine_name in convertible_engines else query
        logging.info(f"Converted query for {engine}: {engine_query}")

        try:
            search_results = engine.search(
                query=engine_query,
                limit=args.limit,
            )
            if search_results:
                results.extend(search_results)
                logging.info(f"{engine} returned {len(search_results)} results")
        except Exception as e:
            logging.error(f"Search engine {engine} query failed: {str(e)}")
            continue

    if not results:
        logging.warning("No results returned from any platform")
        return []

    if args.fields:
        fields = [f.strip() for f in args.fields.split(",")]
        results = apply_field_filter(results, fields)
        logging.info(f"After field filtering: {len(results)} results remaining")
    
    if filters:
        results = filter_results(results,filters)
        logging.info(f"After config filter, {len(results)} results remaining")


    return results

if __name__ == "__main__":
    results = []  
    if args.input:
        with open(args.input, "r") as f:
            queries = [q.strip() for q in f.readlines() if q.strip()] 
            queries = list(dict.fromkeys(queries))
            total = len(queries)
            
            for idx, query in enumerate(queries, start=1):
                query = utils.fix_query(query)
                print(f"[{idx}/{total}] Searching: {query}")
                try:
                    batch_results = run_search(platforms, query)
                    results.extend(batch_results)
                except Exception as e:
                    logging.error(f"Error processing query '{query}': {e}")
                    continue
                
    elif args.query:
        print(f"Searching: {args.query}")
        args.query = utils.fix_query(args.query)
        try:
            results = run_search(platforms, args.query)
        except Exception as e:
            logging.error(f"Error processing query '{args.query}': {e}")
            sys.exit(1)
    
    elif args.icon:

        results = []
        
        for engine in platforms:
            engine_name = next((name for name, obj in engines.items() if obj == engine), None)
            
            if engine_name == 'quake':
                icon_hash = utils.hash_icon(args.icon, 'md5')
                print(f"Icon hash (MD5 for Quake): {icon_hash}")
            else:
                icon_hash = utils.hash_icon(args.icon, 'mmh3')
                print(f"Icon hash (MMH3 for {engine_name}): {icon_hash}")
                
            query = f'iconhash="{icon_hash}"'
            
            try:
                engine_results = run_search([engine], query)
                results.extend(engine_results)
            except Exception as e:
                logging.error(f"Error processing query '{query}' for {engine_name}: {e}")
                continue

    if args.output:
        if '.' not in args.output:
            logging.error("You have to input a valid output file name (例如: results.json)")
            sys.exit(1)

        try:
            output_format = args.output.split(".")[-1].lower()
            output_file = args.output

            if output_format not in ['json', 'csv', 'xml', "xlsx", "txt"]:
                logging.error("Unsupport format, only json/csv/xml/xlsx/txt")
                sys.exit(1)

            utils.save_results(results, output_format, output_file)
            logging.info(f"Results already saved at {args.output}")
            
        except Exception as e:
            logging.error(f"Error when save results to {args.output}: {str(e)}")
            sys.exit(1)
            
    else:
        if results:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print("No results found matching the criteria.")

if not args.query and not args.input and not args.icon and not args.show_fields:
    print("Error: Please provide either --query, --input, --icon parameter, or use --show-fields")
    sys.exit(1)
              
