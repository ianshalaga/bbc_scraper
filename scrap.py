import sys
from termcolor import colored
import scraper_bbc as bbc

if __name__ == "__main__":
    if len(sys.argv) > 4 and len(sys.argv) < 3:
        print(colored("Uso incorrecto", "red", attrs=["bold"]))
        print("Modo de uso:", colored(f"{sys.argv[0]} [-scraper -type -option]", "green"))
        exit()

    if "-bbc" in sys.argv: # Scraper BBC
        if "-links" in sys.argv: # Links
            if "-bruteforce" in sys.argv or "-bf" in sys.argv:
                bbc.scraper_links_brute_force()
            else:
                bbc.scraper_links_daily()
        elif "-titles" in sys.argv: # Titles and authors
            bbc.get_titles_and_authors()
        elif "-content" in sys.argv: # Content
            bbc.get_data_original()
        elif "-codes" in sys.argv: # Codes
            bbc.news_codes_extractor()
        elif "-dates" in sys.argv: # Dates
            bbc.news_dates_extractor()
        elif "-cleaner" in sys.argv:
            bbc.db_cleaner()
        elif "-crepeated" in sys.argv:
            bbc.db_clean_repeated()
        elif "-renew" in sys.argv:
            bbc.db_renew_links()
        else:
            print(colored("Unknown type", "red"))
            exit()
    else:
        print(colored("Unknown scraper", "red"))
        exit()
