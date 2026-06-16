import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# --- CONFIGURATION ---
QUERY = "Real Madrid"
# Period 1: Ascent (Start of season to first Clasico)
PERIOD_1 = ("2025-08-01", "2025-10-26")
# Period 2: Decline (First Clasico to Supercopa Final/Firing)
PERIOD_2 = ("2025-10-26", "2026-01-12")

def get_date_chunks(start_date_str, end_date_str, days=7):
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    chunks = []
    current = start
    while current < end:
        chunk_end = min(current + timedelta(days=days), end)
        chunks.append((current.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        current = chunk_end
    return chunks

def fetch_news(query, start_date, end_date):
    url = f"https://news.google.com/rss/search?q={query}+after:{start_date}+before:{end_date}&hl=en-US&gl=US&ceid=US:en"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        data = []
        for item in items:
            data.append({
                'title': item.title.text,
                'date': item.pubDate.text,
                'link': item.link.text
            })
        return data
    except Exception as e:
        print(f"Error fetching {start_date} to {end_date}: {e}")
        return []

def run_collection():
    os.makedirs('data/raw', exist_ok=True)
    
    windows = [
        {'name': 'Period_1_Ascent', 'start': PERIOD_1[0], 'end': PERIOD_1[1]},
        {'name': 'Period_2_Decline', 'start': PERIOD_2[0], 'end': PERIOD_2[1]}
    ]
    
    for w in windows:
        print(f"Collecting: {w['name']}...")
        chunks = get_date_chunks(w['start'], w['end'])
        all_results = []
        for start, end in chunks:
            print(f"  Chunk: {start} to {end}")
            all_results.extend(fetch_news(QUERY, start, end))
            time.sleep(1)
        
        df = pd.DataFrame(all_results).drop_duplicates(subset=['title'])
        filename = f"data/raw/news_{w['name'].lower()}.csv"
        df.to_csv(filename, index=False)
        print(f"  Saved {len(df)} headlines to {filename}")

if __name__ == "__main__":
    run_collection()