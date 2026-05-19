import logging
import scraper
import job_details
import ai_filter
import log_setup


def menu():
    logging.info("=" * 100)
    logging.info("  SELECT AN OPTION:   ")
    logging.info("=" * 100)
    logging.info("  1. Run Scraper")
    logging.info("  2. Get Job Descriptions")
    logging.info("  3. Filter")
    logging.info("  4. All")
    logging.info("  5. Exit")
    logging.info("=" * 100)
    chosen_opt = input("Input Choice: ")
    logging.info("=" * 100)
    return chosen_opt


def handle_opts(opt):
    while opt not in ("1", "2", "3", "4", "5"):
        logging.info("PLEASE SELECT A VALID OPTION")
        opt = menu()

    logging.info("SELECTED OPTION: " + opt)
    if opt == "1":
        logging.info("Chose Run Scraper")
        scraper.init()
    elif opt == "2":
        logging.info("Chose Get Job Descriptions")
        job_details.init()
    elif opt == "3":
        logging.info("Chose Filter")
        ai_filter.init()
    elif opt == "4":
        logging.info("Chose All")
        scraper.init()
        job_details.init()
        ai_filter.init()
    elif opt == "5":
        logging.info("BYE!")
        exit()


def main():
    log_setup.setup_logger()
    option = menu()
    handle_opts(option)


if __name__ == "__main__":
    main()
