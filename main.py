import logging
import scraper
import job_details
import ai_filter
import analyse
import log_setup
import file_handling as fh

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
    logging.info("  7. Exit")
    logging.info("=" * 100)
    chosen_opt = input("Input Choice: ")
    logging.info("=" * 100)
    return chosen_opt


def handle_opts(opt):
    while opt not in ("1", "2", "3", "4", "5", "6", "7", "12", "123", "126", "26","1236"):
        logging.info("PLEASE SELECT A VALID OPTION")
        opt = menu()

    logging.info("SELECTED OPTION: " + opt)
    if opt == "1":
        logging.info("Chose to run Scraper.")
        scraper.init()
    elif opt == "2":
        logging.info("Chose to get Job Details.")
        job_details.init()
    elif opt == "3":
        logging.info("Chose Filter.")
        ai_filter.init()
    elif opt == "4":
        logging.info("Chose to perform Analysis.")
        analyse.init()
    elif opt == "5":
        logging.info("Chose to perform All.")
        scraper.init()
        job_details.init()
        ai_filter.init()
        analyse.init()
        fh.archive_old_files()
    elif opt == "6":
        logging.info("Chose to Archive old files.")
        fh.archive_old_files()
    elif opt == "7":
        logging.info("BYE!")
        exit()
    elif opt == "12":
        logging.info("Chose to perform Scrape and get Job Details.")
        scraper.init()
        job_details.init()
    elif opt == "123":
        logging.info("Chose to perform Scrape, get Job Details and FIlter.")
        scraper.init()
        job_details.init()
        ai_filter.init()
    elif opt == "126":
        logging.info("Chose to perform Scrape, get Job Details and Archive old files.")
        scraper.init()
        job_details.init()
        fh.archive_old_files()
    elif opt == "26":
        logging.info("Chose to perform get Job Details and Archive old files.")
        job_details.init()
        fh.archive_old_files()
    elif opt == "1236":
        logging.info("Chose to perform Scrape, get Job Details, Filter and Archive old files.")
        scraper.init()
        job_details.init()
        ai_filter.init()
        fh.archive_old_files()
        


def main():
    log_setup.setup_logger()
    option = menu()
    handle_opts(option)


if __name__ == "__main__":
    main()
