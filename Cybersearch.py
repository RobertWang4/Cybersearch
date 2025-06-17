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

args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

def run_search():
    engine_zoomeye = Zoomeye(CONFIG.get("zoomeye_api_key"), args.verbose)
    engine_fofa = Fofa(CONFIG.get("fofa_email"), CONFIG.get("fofa_api_key"), args.verbose)
    engine_shodan = Shodan(CONFIG.get("shodan_api_key"), args.verbose)
    engine_hunter = Hunter(CONFIG.get("hunter_api_key"), args.verbose)
    engine_quake = Quake(CONFIG.get("quake_api_key"), args.verbose)
    engine_daydaymap = DayDayMap(CONFIG.get("daydaymap_api_key"), args.verbose)

    platforms = [
        engine_zoomeye,
        engine_fofa,
        engine_shodan,
        engine_hunter,
        engine_quake,
        engine_daydaymap
    ]
    results = []

    for engine in platforms:
        if engine == engine_zoomeye:
            api_key = CONFIG.get("zoomeye_api_key")
        elif engine == engine_fofa:
            api_key = CONFIG.get("fofa_email") and CONFIG.get("fofa_api_key")
        elif engine == engine_shodan:
            api_key = CONFIG.get("shodan_api_key")
        elif engine == engine_hunter:
            api_key = CONFIG.get("hunter_api_key")
        elif engine == engine_quake:
            api_key = CONFIG.get("quake_api_key")
        elif engine == engine_daydaymap:
            api_key = CONFIG.get("daydaymap_api_key")
        else:
            api_key = None
            
        if not api_key:
            logging.warning(f"Skipping platform {engine}: API key not configured")
            continue
        
        logging.info(f"Attempting to use platform: {engine}")
        if not engine.auth():
            logging.warning(f"{engine} authentication failed, skipping")
            continue

        if engine == engine_fofa:
            query = utils.convert(args.query, "fofa")
        elif engine == engine_shodan:
            query = utils.convert(args.query, "shodan")
        elif engine == engine_hunter:
            query = utils.convert(args.query, "hunter")
        elif engine == engine_quake:
            query = utils.convert(args.query, "quake")
        elif engine == engine_daydaymap:
            query = utils.convert(args.query, "daydaymap")
        else:
            query = args.query

            
        try:
            search_results = engine.search(
                query=query,
                limit=args.limit,
            )
            if search_results:
                results.extend(search_results)
        except Exception as e:
            logging.error(f"搜索引擎 {engine} 查询失败: {str(e)}")

        if results:
            logging.info(f"{engine} returned {len(results)} results") 

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
