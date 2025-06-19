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

parser.add_argument("--query", required=True, help="Search keyword (e.g. title='Apache')")
parser.add_argument("--limit", type=int, default=10, help="Number of results to return (default 10)")
parser.add_argument("--fields", help="Output fields, comma separated, e.g. ip,port,title")
parser.add_argument("--country", help="Filter by country (e.g. CN)")
parser.add_argument("--domain", help="Filter by domain (e.g. example.com)")
parser.add_argument("--verbose", action="store_true", help="Enable debug output")
parser.add_argument(
    "--engine",
    type=str,
    default="all",
    help="Specify search engine (fofa, zoomeye, hunter, quake, shodan, daydaymap, or all)"
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

def run_search(platforms=platforms):
    results = []

    for engine in platforms:
        logging.info(f"Attempting to use platform: {engine}")
        if not engine.auth():
            logging.warning(f"{engine} authentication failed, skipping")
            continue

        # 最简洁的查询转换逻辑
        engine_name = next((name for name, obj in engines.items() if obj == engine), None)
        query = utils.convert(args.query, engine_name) if engine_name in convertible_engines else args.query

        try:
            search_results = engine.search(
                query=query,
                limit=args.limit,
            )
            if search_results:
                results.extend(search_results)
        except Exception as e:
            logging.error(f"搜索引擎 {engine} 查询失败: {str(e)}")

        if search_results:
            logging.info(f"{engine} returned {len(search_results)} results") 

    if not results:
        logging.warning("No results returned from any platform")
        return

    if args.country:
        results = [r for r in results if r.get("country") == args.country]
        logging.info(f"After country filtering: {len(results)} results remaining")
        
    if args.domain:
        results = [r for r in results if r.get("domain") and args.domain in r.get("domain")]
        logging.info(f"After domain filtering: {len(results)} results remaining")

    if args.fields:
        fields = [f.strip() for f in args.fields.split(",")]
        results = apply_field_filter(results, fields)

    for r in results:
        print(r)

if __name__ == "__main__":
    run_search()
