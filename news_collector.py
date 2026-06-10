import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# --- CONFIGURATION ---
QUERY = "Real Madrid"
PRE_CLASICO = ("2025-08-01", "2025-10-26")
POST_CLASICO = ("2025-10-26", "2026-04-27")

def get_date_chunks(start_date_str, end_date_str, days=7):
    """Splits a long time range into smaller weekly chunks."""
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    chunks = []
    
    current = start
    while current < end:
        chunk_end = min(current + timedelta(days=days), end)
        chunks.append((current.strftime("%Y-%m-%d"), chunk_end.strftime("%Y-%m-%d")))
        current = chunk_end
    return chunks

def fetch_news_chunk(query, start_date, end_date):
    """Fetches up to 100 headlines for a specific date range."""
    # Google News RSS format: q={query} after:{start} before:{end}
    rss_url = f"https://news.google.com/rss/search?q={query}+after:{start_date}+before:{end_date}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        response = requests.get(rss_url )
        soup = BeautifulSoup(response.content, 'xml') # Uses the lxml parser
        items = soup.find_all('item')
        
        data = []
        for item in items:
            data.append({
                'title': item.title.text,
                'link': item.link.text,
                'pubDate': item.pubDate.text,
                'source': item.source.text if item.source else "Unknown",
                'search_window': f"{start_date} to {end_date}"
            })
        return data
    except Exception as e:
        print(f"Error fetching {start_date} to {end_date}: {e}")
        return []

def run_collection(name, date_range):
    """Runs the full collection for a specific window (Pre or Post Clasico)."""
    print(f"\n--- Starting Collection: {name} ---")
    chunks = get_date_chunks(date_range[0], date_range[1])
    all_results = []
    
    for start, end in chunks:
        print(f"  Fetching: {start} to {end}...")
        chunk_data = fetch_news_chunk(QUERY, start, end)
        all_results.extend(chunk_data)
        time.sleep(1) # Be polite to the server
        
    df = pd.DataFrame(all_results)
    print(f"--- Finished! Collected {len(df)} headlines for {name}. ---")
    return df

if __name__ == "__main__":
    # Create data folder if it doesn't exist
    os.makedirs("data/raw", exist_ok=True)
    
    # Run Pre-Clasico
    df_pre = run_collection("Pre-Clasico", PRE_CLASICO)
    df_pre.to_csv("data/raw/news_pre_clasico.csv", index=False)
    
    # Run Post-Clasico
    df_post = run_collection("Post-Clasico", POST_CLASICO)
    df_post.to_csv("data/raw/news_post_clasico.csv", index=False)
    
    print("\nSUCCESS: All data saved to data/raw/")
