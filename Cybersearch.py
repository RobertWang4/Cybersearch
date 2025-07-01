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
parser.add_argument("--fields", default="ip,port,title,country", help="Output fields, comma separated, e.g. ip,port,title")
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

args = parser.parse_args()

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
                print(f"[{idx}/{total}] Searching: {query}")
                try:
                    batch_results = run_search(platforms, query)
                    results.extend(batch_results)
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
              
