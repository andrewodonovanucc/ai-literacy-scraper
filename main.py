# =================================================================================
#   IMPORTS
# =================================================================================

import logging
import log_setup
import file_handling as fh
import helper as hp
import config
import scraper, job_details, ai_filter, analyse, app
import argparse
import sys


# =================================================================================
#   GIVE THE OPTION TO SKIP THE MENU AND PROVIDE ARGUMENTS DIRECTLY
# =================================================================================

def parse_args():
    parser = argparse.ArgumentParser(description="AI Literacy Scraper")
    parser.add_argument("option", nargs="?", default=None, help="Main menu option (1-8, or combos like 123)")
    parser.add_argument("scrape_type", nargs="?", default=None, help="Posting type for scraper: 1=Academic, 2=PhD, 3=Both")
    parser.add_argument("analyse_type", nargs="?", default=None, help="Posting type for analysis: 1=Academic, 2=PhD, 3=Both")
    return parser.parse_args()

# =================================================================================
#   MENU OF OPTIONS
# =================================================================================

def menu():
    logging.info("=" * 100)
    logging.info("  SELECT AN OPTION:   ")
    logging.info("=" * 100)
    logging.info("  1. Run Scraper")
    logging.info("  2. Get Job Details")
    logging.info("  3. Filter")
    logging.info("  4. Analyse")
    logging.info("  5. All")
    logging.info("  6. Archive old files")
    logging.info("  7. Run App")
    logging.info("  8. Exit")
    logging.info("=" * 100)
    chosen_opt = input("Input Choice: ")
    logging.info("=" * 100)
    return chosen_opt


def handle_opts(opt, scrape_type, analyse_type):
    while opt not in config.valid_menu_options:
        logging.info("PLEASE SELECT A VALID OPTION")
        opt = menu()

    logging.info("SELECTED OPTION: " + opt)
    if opt == "1":
        logging.info("Chose to run Scraper.")
        scraper.init(scrape_type)
    elif opt == "2":
        logging.info("Chose to get Job Details.")
        job_details.init()
    elif opt == "3":
        logging.info("Chose Filter.")
        ai_filter.init()
    elif opt == "4":
        logging.info("Chose to perform Analysis.")
        analyse.init(analyse_type)
    elif opt == "5":
        logging.info("Chose to perform All.")
        scraper.init(scrape_type)
        job_details.init()
        ai_filter.init()
        analyse.init(analyse_type)
        fh.archive_old_files()
    elif opt == "6":
        logging.info("Chose to Archive old files.")
        fh.archive_old_files()
    elif opt == "7":
        logging.info("Chose to run the Streamlit Web App.")
        app.init()
    elif opt == "8":
        logging.info("BYE!")
        exit()
    elif opt == "12":
        logging.info("Chose to perform Scrape and get Job Details.")
        scraper.init()
        job_details.init()
    elif opt == "123":
        logging.info("Chose to perform Scrape, get Job Details and Filter.")
        scraper.init(scrape_type)
        job_details.init()
        ai_filter.init()
    elif opt == "126":
        logging.info("Chose to perform Scrape, get Job Details and Archive old files.")
        scraper.init(scrape_type)
        job_details.init()
        fh.archive_old_files()
    elif opt == "24":
        logging.info("Chose to perform get Job Details and Analyse.")
        job_details.init()
        analyse.init(analyse_type)
    elif opt == "246":
        logging.info("Chose to perform get Job Details, Analyse and Archive old files.")
        job_details.init()
        analyse.init(analyse_type)
        fh.archive_old_files()
    elif opt == "26":
        logging.info("Chose to perform get Job Details and Archive old files.")
        job_details.init()
        fh.archive_old_files()
    elif opt == "46":
        logging.info("Chose to perform Analyse and Archive old files.")
        analyse.init()
        fh.archive_old_files()
    elif opt == "1236":
        logging.info("Chose to perform Scrape, get Job Details, Filter and Archive old files.")
        scraper.init(scrape_type)
        job_details.init()
        ai_filter.init()
        fh.archive_old_files()
    elif opt == "1246":
        logging.info("Chose to perform Scrape, get Job Details, Analyse and Archive old files.")
        scraper.init(scrape_type)
        job_details.init()
        analyse.init(analyse_type)
        fh.archive_old_files()
        


def main():
    # hp.time_check()
    log_setup.setup_logger()
    args = parse_args()
    opt = args.option or menu()
    handle_opts(opt, args.scrape_type, args.analyse_type)

if __name__ == "__main__":
    main()