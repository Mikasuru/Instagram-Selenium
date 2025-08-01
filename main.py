import argparse
import logging

from scraper import InstagramScraper
from session_manager import create_session
from discord_notifier import SendNoti
from exceptions import SessionNotFoundException, ScrapingException
from config import TargetUsr, Limit, WebhookUrl

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')

def main():
    Parser = argparse.ArgumentParser(description="Scrape and send to discord")
    Parser.add_argument(
        "--create-session",
        action="store_true",
        help="Run interactive session creation to log in and save cookies."
    )
    Parser.add_argument(
        "-u", "--username",
        type=str,
        default=TargetUsr,
        help=f"The Instagram username to scrape. Default: {TargetUsr}"
    )
    Parser.add_argument(
        "-l", "--limit",
        type=int,
        default=Limit,
        help=f"The maximum number of followers to scrape. Default: {Limit}"
    )
    args = Parser.parse_args()

    if args.create_session:
        create_session()
        return

    TargetName = args.username
    limit = args.limit
    FollowersList = None
    ErrorMsg = None
    
    logging.info(f"> Starting for: {TargetName} (Limit: {limit}) ---")
    
    try:
        with InstagramScraper() as scraper:
            scraper.login()
            FollowersList = scraper.GetFollowers(username=TargetName, limit=limit)
        
        logging.info(f"\n[+] Fetched {len(FollowersList)} followers.")

    except (SessionNotFoundException, ScrapingException, Exception) as e:
        ErrorMsg = f"{e.__class__.__name__}: {e}"
        logging.error(f"\n[-] {ErrorMsg}")

    finally:
        SendNoti(
            webhook_url=WebhookUrl,
            TargetName=TargetName,
            FollowersList=FollowersList,
            ErrorMsg=ErrorMsg
        )

if __name__ == "__main__":
    main()