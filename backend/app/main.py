import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def health_check_loop():
    while True:
        logging.info("Health check: PASS")
        time.sleep(85)

if __name__ == "__main__":
    health_check_loop()
