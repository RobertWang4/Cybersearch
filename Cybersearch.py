import argparse
import logging
import utils
from config import CONFIG       
from feed.fofa import Fofa 
from feed.shodan import Shodan
from feed.zoomeye import Zoomeye
from feed.hunter import Hunter
from feed.quake import Quake
from feed.daydaymap import DayDayMap
from filters import apply_field_filter
    
parser = argparse.ArgumentParser(description="Cybersearch - Aggregated Search Tool (Beta)")

parser.add_argument("--query", required=False, help="Search keyword (e.g. title='Apache')")
parser.add_argument("--limit", type=int, default=10, help="Number of results to return (default 10)")
parser.add_argument("--fields", help="Output fields, comma separated, e.g. ip,port,title")
parser.add_argument("--country", help="Filter by country (e.g. CN)")
parser.add_argument("--domain", help="Filter by domain (e.g. example.com)")
parser.add_argument("--verbose", action="store_true", help="Enable debug output")
parser.add_argument("--icon", help="Icon hash to search(.icon)")
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
    default="results.json",
    help="Output file name and format (json, csv, or xml)"
)

args = parser.parse_args()


if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


engines = {
    "hunter": Hunter(CONFIG.get("hunter_api_key"), args.verbose),
    "zoomeye": Zoomeye(CONFIG.get("zoomeye_api_key"), args.verbose),
    "fofa": Fofa(CONFIG.get("fofa_api_key"), args.verbose, args.fields.split(",")),
    "shodan": Shodan(CONFIG.get("shodan_api_key"), args.verbose),
    "quake": Quake(CONFIG.get("quake_api_key"), args.verbose),
    "daydaymap": DayDayMap(CONFIG.get("daydaymap_api_key"), args.verbose)
}

# 需要查询转换的引擎
convertible_engines = {"fofa", "shodan", "hunter", "quake", "daydaymap"}

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
        query = utils.convert(query, engine_name) if engine_name in convertible_engines else query
        logging.info(f"Converted query for {engine}: {query}")

        try:
            search_results = engine.search(
                query=query,
                limit=args.limit,
            )
            if search_results:
                results.extend(search_results)
                logging.info(f"{engine} returned {len(search_results)} results")
        except Exception as e:
            logging.error(f"搜索引擎 {engine} 查询失败: {str(e)}")
            continue

    if not results:
        logging.warning("No results returned from any platform")
        return []

    # 按国家过滤结果
    if args.country:
        results = [r for r in results if r.get("country") == args.country]
        logging.info(f"After country filtering: {len(results)} results remaining")
        
    # 按域名过滤结果
    if args.domain:
        results = [r for r in results if r.get("domain") and args.domain in r.get("domain")]
        logging.info(f"After domain filtering: {len(results)} results remaining")

    # 按字段过滤结果
    if args.fields:
        fields = [f.strip() for f in args.fields.split(",")]
        results = apply_field_filter(results, fields)
        logging.info(f"After field filtering: {len(results)} results remaining")

    if args.output:
        # 检查文件名格式是否合法
        if '.' not in args.output:
            logging.error("You have to input a valid output file name (例如: results.json)")
            return
            
        try:
            output_format = args.output.split(".")[-1].lower()
            output_file = args.output
            
            # 检查输出格式是否支持
            if output_format not in ['json', 'csv', 'xml',"xlsx","txt"]:
                logging.error("Unsupport format, only json/csv/xml/xlsx/txt")
                return
                
            utils.save_results(results, output_format, output_file)
            logging.info(f"Results already saved at {args.output}")
            return
            
        except Exception as e:
            logging.error(f"Error when save results to {args.output}: {str(e)}")
            return

    return results

if __name__ == "__main__":
    if args.input:
        with open(args.input, "r") as f:
            queries = [q.strip() for q in f.readlines() if q.strip()] 
            queries = list(dict.fromkeys(queries))
            total = len(queries)
            
            for idx, query in enumerate(queries, start=1):
                print(f"[{idx}/{total}] Searching: {query}")
                try:
                    results = run_search(platforms, query)
                except Exception as e:
                    logging.error(f"Error processing query '{query}': {e}")
                    continue
                
    elif args.query:
        print(f"Searching: {args.query}")
        try:
            results = run_search(platforms, args.query)
        except Exception as e:
            logging.error(f"Error processing query '{args.query}': {e}")
            sys.exit(1)
    
    elif args.icon:
        icon_hash = utils.hash_icon(args.icon)
        print(f"Icon hash: {icon_hash}")
        query = f'icon_hash="{icon_hash}"'
        try:
            results = run_search(platforms, query)
        except Exception as e:
            logging.error(f"Error processing query '{query}': {e}")
            sys.exit(1)
    
    else:
        print("Error: Please provide either --query or --input parameter")
        sys.exit(1)
