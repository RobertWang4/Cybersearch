from dotenv import load_dotenv
import os
import yaml
import logging

load_dotenv()


def load_api_key():
    config = {}
    config["zoomeye_api_key"] = os.getenv("ZOOMEYE_API_KEY")
    config["fofa_api_key"] = os.getenv("FOFA_API_KEY")
    config["shodan_api_key"] = os.getenv("SHODAN_API_KEY")
    config["hunter_api_key"] = os.getenv("HUNTER_API_KEY")
    config["quake_api_key"] = os.getenv("QUAKE_API_KEY")
    config["daydaymap_api_key"] = os.getenv("DAYDAYMAP_API_KEY")
    
    if not all(config.values()):
        logging.warning("Missing some API keys, trying to load from config file.")
        
    config_path = os.path.expanduser("~/.Cybersearch/api_key.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    if config == None:
        raise Exception("No API key found")

    else:
        return config
        
        
CONFIG = load_api_key()