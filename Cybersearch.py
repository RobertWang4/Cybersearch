import argparse
import logging
from config import CONFIG
from feed.zoomeye import Zoomeye
from filters import apply_field_filter


parser = argparse.ArgumentParser(description="Cybersearch - 聚合搜索工具（初版）")

parser.add_argument("--query", required=True, help="搜索关键词，(如 title='Apache')")
parser.add_argument("--limit", type=int, default=10, help="返回结果数量（默认10）")
parser.add_argument("--fields", help="输出字段，逗号分隔，如 ip,port,title")
parser.add_argument("--country", help="国家过滤（如 CN）")
parser.add_argument("--domain", help="域名过滤（如 example.com）")
parser.add_argument("--verbose", action="store_true", help="开启调试输出")


args = parser.parse_args()

if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

def run_search():
 
    platforms = ["zoomeye"]
    results = []

    for engine in platforms:
        api_key = CONFIG.get(engine)
        if not api_key:
            logging.warning(f"跳过平台 {engine}：未配置 API key")
            continue

        if engine == "zoomeye":
            engine_instance = Zoomeye(api_key, args.verbose)

        logging.info(f"尝试使用平台：{engine}")
        if not engine_instance.auth():
            logging.warning(f"{engine} 认证失败，跳过")
            continue

        results = engine_instance.search(
            query=args.query,
            limit=args.limit,
        )

        if results:
            logging.info(f"{engine} 返回了 {len(results)} 条结果")
            break  

    if not results:
        logging.warning("所有平台均未返回结果")
        return

    if args.fields:
        fields = [f.strip() for f in args.fields.split(",")]
        results = apply_field_filter(results, fields)

    for r in results:
        print(r)

if __name__ == "__main__":
    run_search()
