from loguru import logger
import requests

def main():
    url = "https://example.com/"
    r = requests.get(url, timeout=20)
    logger.info(f"Fetched {url} with status {r.status_code}")

if __name__ == "__main__":
    main()
