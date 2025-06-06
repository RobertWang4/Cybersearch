from dotenv import load_dotenv
import os
import yaml

load_dotenv()


def load_api_key():
    config = {}
    config["zoomeye"] = os.getenv("ZOOMEYE_API_KEY")
    if config["zoomeye"]:
        return config
    
    config_path= os.path.expanduser("~/.searcher/api_key.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
        
    raise Exception("No API key found")
        
CONFIG = load_api_key()