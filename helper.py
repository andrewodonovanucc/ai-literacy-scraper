import logging
import requests
import time
import file_handling as fh
from datetime import datetime as dt
from datetime import timedelta as td

# =================================================================================
# REQUEST HELPER
# =================================================================================

def request_page(session, url, label=""):
    try:
        r = session.get(url, timeout=60)
        if r.status_code != 200:
            logging.warning(f"Non-200 response ({r.status_code}) for {label or url}")
            r.close()
            return None
        return r
    except requests.exceptions.Timeout:
        logging.warning(f"Timeout fetching {label or url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.warning(f"Request error for {label or url}: {e}")
        return None
    
def time_check():
    mrr = fh.get_most_recent_item("runs")

    if mrr != None:
        run_dt = dt.strptime(mrr, "run-%Y%m%d-%H%M.log")
        if dt.now() - run_dt < td(minutes=5):
            logging.info("TIME DELTA: " + str(dt.now() - run_dt))
            logging.info("SLEEPING FOR 1 MINUTE")
            logging.info("=" * 100)
            time.sleep(60)
            logging.info("SLEEP COMPLETE...")
        else:
            logging.info("SLEEPING FOR 10 SECONDS")
            logging.info("=" * 100)
            time.sleep(10)
            logging.info("SLEEP COMPLETE...")
            logging.info("=" * 100)
    else:
        logging.info("=" * 100)
        logging.info("NO PREVIOUS RUNS...")
        logging.info("=" * 100)
        logging.info("SLEEPING FOR 10 SECONDS")
        logging.info("=" * 100)
        time.sleep(10)
        logging.info("SLEEP COMPLETE...")
        logging.info("=" * 100)
    