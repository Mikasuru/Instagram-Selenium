### Instagram follower scraping

This project is a simple script to scrape Instagram followers using `undetected-chromedriver` and `selenium`, then send the results to a Discord webhook.
> This project was made for fun and learning. The code quality may not be good, but atleast it working.

### Prerequisites

You can install all necessary libraries using pip:

```bash
pip install -r requirements.txt
```

### Usage

#### 1. Create Session
First, you need to create a session by logging in. The script will open a browser window for you to log into your Instagram account.

```bash
python main.py --create-session
```

The script will save your login cookies to `selenium_session.json` once you are logged in.

#### 2. Scrape Followers
After creating the session, you can scrape followers using the following command:

```bash
python main.py
```

You can specify a different username and follower limit with the `-u` and `-l` flags:

```bash
python main.py -u kukuri_xyz
```

The script will send a Discord notification with the results when it's finished.
