from dotenv import load_dotenv
import os
import yaml
import logging

load_dotenv()


def load_api_key():
    config = {}
    
    # 1. Load from environment variables first
    config["zoomeye_api_key"] = os.getenv("ZOOMEYE_API_KEY")
    config["fofa_api_key"] = os.getenv("FOFA_API_KEY")
    config["shodan_api_key"] = os.getenv("SHODAN_API_KEY")
    config["hunter_api_key"] = os.getenv("HUNTER_API_KEY")
    config["quake_api_key"] = os.getenv("QUAKE_API_KEY")
    config["daydaymap_api_key"] = os.getenv("DAYDAYMAP_API_KEY")
    
    # 2. If environment variables are incomplete, try loading from YAML config
    if not all(config.values()):
        logging.info("Some API keys not found in environment variables, attempting to load from config file...")
        
        # Support multiple possible config file paths
        possible_paths = [
            os.path.expanduser("~/.Cybersearch/api_keys.yaml"),
            "config.yaml"
        ]
        
        for config_path in possible_paths:
            if os.path.exists(config_path):
                logging.info(f"Found config file: {config_path}")
                with open(config_path, "r", encoding="utf-8") as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        # Merge configurations, YAML config supplements missing parts from environment variables
                        for key, value in yaml_config.items():
                            if not config.get(key):
                                config[key] = value
                        break
    
    # 3. Verify that at least one API key is available
    available_keys = [k for k, v in config.items() if v]
    if not available_keys:
        raise Exception("No API keys found. Please check environment variables, .env file, or YAML config file")
    
    logging.info(f"Successfully loaded API keys: {', '.join([k.replace('_api_key', '') for k in available_keys])}")
    return config
        
        
CONFIG = load_api_key()