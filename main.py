import logging
import log_setup
import file_handling as fh
import helper as hp
import config
import scraper, scraper_linkedin, job_details, job_details_linkedin, ai_filter, analyse, app
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="AI Literacy Scraper")
    parser.add_argument("option", nargs="?", default=None, help="Main menu option (1-9, 0, c, or combos)")
    parser.add_argument("scrape_type", nargs="?", default=None, help="Posting type for scraper: 1=Academic, 2=PhD, 3=Both")
    parser.add_argument("analyse_type", nargs="?", default=None, help="Posting type for analysis: 1=Academic, 2=PhD, 3=LinkedIn, 4=All")
    return parser.parse_args()


def menu():
    logging.info("=" * 100)
    logging.info("  SELECT AN OPTION:   ")
    logging.info("=" * 100)
    logging.info("  1. Run Scraper (jobs.ac.uk)")
    logging.info("  2. Get Job Details (jobs.ac.uk)")
    logging.info("  3. Filter (AI term matching)")
    logging.info("  4. Analyse")
    logging.info("  5. All")
    logging.info("  6. Archive old files")
    logging.info("  7. Run App")
    logging.info("  8. Run Scraper (LinkedIn)")
    logging.info("  9. Get Job Details (LinkedIn)")
    logging.info("  0. Exit")
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
        logging.info("Chose to run Scraper (jobs.ac.uk).")
        scraper.init(scrape_type)
    elif opt == "2":
        logging.info("Chose to get Job Details (jobs.ac.uk).")
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
        scraper_linkedin.init()
        job_details_linkedin.init()
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
        logging.info("Chose to run Scraper (LinkedIn).")
        scraper_linkedin.init()
    elif opt == "9":
        logging.info("Chose to get Job Details (LinkedIn).")
        job_details_linkedin.init()
    elif opt == "0":
        logging.info("BYE!")
        exit()
    elif opt == "12":
        logging.info("Chose to perform Scrape and get Job Details.")
        scraper.init(scrape_type)
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
        analyse.init(analyse_type)
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
    elif opt == "89":
        logging.info("Chose to run LinkedIn Scraper and get LinkedIn Job Details.")
        scraper_linkedin.init()
        job_details_linkedin.init()
    elif opt == "893":
        logging.info("Chose to run LinkedIn Scraper, get LinkedIn Job Details and Filter.")
        scraper_linkedin.init()
        job_details_linkedin.init()
        ai_filter.init()
    elif opt == "8934":
        logging.info("Chose to run LinkedIn Scraper, get LinkedIn Job Details, Filter and Analyse.")
        scraper_linkedin.init()
        job_details_linkedin.init()
        ai_filter.init()
        analyse.init(analyse_type)
    elif opt == "86":
        logging.info("Chose to run LinkedIn Scraper and Archive old files.")
        scraper_linkedin.init()
        fh.archive_old_files()
    elif opt == "896":
        logging.info("Chose to run LinkedIn Scraper, get LinkedIn Job Details and Archive old files.")
        scraper_linkedin.init()
        job_details_linkedin.init()
        fh.archive_old_files()
    elif opt == "8936":
        logging.info("Chose to run LinkedIn Scraper, get LinkedIn Job Details, Filter and Archive old files.")
        scraper_linkedin.init()
        job_details_linkedin.init()
        ai_filter.init()
        fh.archive_old_files()
    elif opt == "89346":
        logging.info("Chose to run LinkedIn Scraper, get LinkedIn Job Details, Filter, Analyse and Archive old files.")
        scraper_linkedin.init()
        job_details_linkedin.init()
        ai_filter.init()
        analyse.init(analyse_type)
        fh.archive_old_files()
    elif opt == "96":
        logging.info("Chose to get LinkedIn Job Details and Archive old files.")
        job_details_linkedin.init()
        fh.archive_old_files()
    elif opt == "936":
        logging.info("Chose to get LinkedIn Job Details, Filter and Archive old files.")
        job_details_linkedin.init()
        ai_filter.init()
        fh.archive_old_files()
    elif opt == "9346":
        logging.info("Chose to get LinkedIn Job Details, Filter, Analyse and Archive old files.")
        job_details_linkedin.init()
        ai_filter.init()
        analyse.init(analyse_type)
        fh.archive_old_files()

def main():
    log_setup.setup_logger()
    args = parse_args()
    opt = args.option or menu()
    handle_opts(opt, args.scrape_type, args.analyse_type)

if __name__ == "__main__":
    main()