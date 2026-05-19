import logging
import os
from datetime import datetime as dt


def setup_logger():
    os.makedirs(os.path.join("data", "runs"), exist_ok=True)
    # timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    # log_path = f"./data/runs/run-{timestamp}.log"
    filename = dt.now().strftime("run-%Y%m%d-%H%M.log")
    filepath = os.path.join("data", "runs", filename)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(message)s")

    fh = logging.FileHandler(filepath)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logging.info(f"Log started: {filepath}")
