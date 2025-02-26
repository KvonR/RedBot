import os
import praw
import requests
import random
import time
import schedule
import json
import ssl
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 🚀 API Credentials (Loaded from .env file)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = os.getenv("USER_AGENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🌎 Reddit API Setup
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=USER_AGENT,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD
)


# 🔥 Tech Deal Scraper
def fetch_tech_deals():
    url = "https://www.amazon.com/deals?node=172282"  # Tech Deals Section
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    deals = []
    for item in soup.find_all("div", class_="dealContainer"):  # Modify per Amazon structure
        title = item.find("span", class_="dealTitle").text
        link = "https://www.amazon.com" + item.find("a")["href"]
        deals.append({"title": title, "url": link})
    return deals[:5]  # Return top 5 deals


# 📢 Affiliate Deals (Pulled dynamically)
affiliate_deals = fetch_tech_deals()


# 🎯 AI-Powered Response Generation
def generate_ai_reply(comment_text, deal):
    openai.api_key = OPENAI_API_KEY
    prompt = f"A user asked: '{comment_text}'. Reply casually as if you are giving a genuine recommendation. Keep it short, engaging, and include a product suggestion with an affiliate link: {deal['url']}. Add a bit of a personal touch."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a helpful, friendly tech enthusiast who loves recommending great products."},
            {"role": "user", "content": prompt}
        ]
    )

    return response["choices"][0]["message"]["content"]


# 🚀 Post Deals to Reddit
def post_to_reddit():
    deal = random.choice(affiliate_deals)
    subreddit = reddit.subreddit(random.choice(["deals", "buildapcsales", "laptops", "hardware"]))
    post_text = f"🔥 Limited-time tech deal: {deal['title']}. Check it out here: {deal['url']}"
    subreddit.submit(title=deal["title"], selftext=post_text)
    print(f"✅ Posted on Reddit: {deal['title']}")


# 📝 AI-Powered Reddit Replies
def reply_to_reddit():
    for comment in reddit.subreddit("+".join(["laptops", "buildapc", "hardware"])).stream.comments(skip_existing=True):
        comment_text = comment.body.lower()
        deal = random.choice(affiliate_deals)

        if "best mouse" in comment_text or "best keyboard" in comment_text or "best headset" in comment_text:
            reply_text = generate_ai_reply(comment_text, deal)
            comment.reply(reply_text)
            print(f"💬 Replied on Reddit: {reply_text}")
            time.sleep(random.randint(600, 1800))  # 10-30 min delay


# 🕒 Intelligent Randomized Scheduling
schedule.every(random.randint(2, 5)).hours.do(post_to_reddit)
schedule.every(random.randint(1, 3)).hours.do(reply_to_reddit)

# Self-Healing: If API fails, retry
while True:
    try:
        schedule.run_pending()
        sleep_time = random.randint(30, 120)  # Random small sleep intervals
        print(f"⏳ Sleeping for {sleep_time} seconds before checking schedule...")
        time.sleep(sleep_time)
    except Exception as e:
        print(f"🚨 Error: {e}, retrying in 5 minutes...")
        time.sleep(300)
