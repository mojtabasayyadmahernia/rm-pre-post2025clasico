import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# --- CONFIGURATION ---
PRE_CLASICO_FILE = "data/raw/news_pre_clasico.csv"
POST_CLASICO_FILE = "data/raw/news_post_clasico.csv"
FOOTBALL_STATS_FILE = "data/processed/football_stats.csv"
CLASICO_DATE = "2025-10-26"

def setup_nltk():
    """Download necessary NLTK data for sentiment analysis."""
    print("Initializing NLP components...")
    nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(df, period_name):
    """Calculates sentiment scores for headlines using VADER."""
    print(f"Analyzing sentiment for {period_name}...")
    sia = SentimentIntensityAnalyzer()
    
    # Calculate scores
    df['sentiment_scores'] = df['title'].apply(lambda x: sia.polarity_scores(str(x)))
    df['compound'] = df['sentiment_scores'].apply(lambda x: x['compound'])
    
    # Clean up dates for plotting
    # Google News RSS pubDate format is usually "Fri, 19 Aug 2025 19:00:00 GMT"
    df['date'] = pd.to_datetime(df['pubDate'], errors='coerce').dt.date
    df = df.dropna(subset=['date'])
    df['date'] = pd.to_datetime(df['date'])
    
    return df

def generate_sentiment_visuals(df_pre, df_post):
    """Creates sentiment-specific visualizations."""
    sns.set_theme(style="whitegrid")
    os.makedirs("assets", exist_ok=True)
    
    # Combine for comparison
    df_pre['period'] = 'Pre-Clasico'
    df_post['period'] = 'Post-Clasico'
    combined = pd.concat([df_pre, df_post])
    
    # Chart 1: Sentiment Distribution (Boxplot)
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=combined, x='period', y='compound', palette=['#00529F', '#EF3340'])
    plt.title('Headline Sentiment Distribution: Pre vs Post Clasico', fontsize=14)
    plt.ylabel('Compound Sentiment Score (-1 to 1)')
    plt.savefig('assets/sentiment_distribution.png', dpi=300)
    print("Saved: assets/sentiment_distribution.png")
    
    # Chart 2: Daily Sentiment Trend
    daily_sentiment = combined.groupby(['date', 'period'])['compound'].mean().reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=daily_sentiment, x='date', y='compound', hue='period', palette=['#00529F', '#EF3340'], linewidth=2)
    plt.axvline(pd.to_datetime(CLASICO_DATE), color='black', linestyle='--', alpha=0.7)
    plt.title('Daily Average News Sentiment Trend', fontsize=14)
    plt.ylabel('Avg Compound Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('assets/sentiment_trend.png', dpi=300)
    print("Saved: assets/sentiment_trend.png")
    
    return daily_sentiment

def correlate_performance_sentiment(sentiment_df, football_file):
    """Combines football stats and sentiment data to find correlations."""
    if not os.path.exists(football_file):
        print("Warning: Football stats file not found. Skipping correlation.")
        return
    
    print("Correlating sentiment with football performance...")
    fb_df = pd.read_csv(football_file)
    fb_df['datetime'] = pd.to_datetime(fb_df['datetime']).dt.date
    fb_df['datetime'] = pd.to_datetime(fb_df['datetime'])
    
    # Merge daily sentiment with match-day stats
    # Note: We merge on the match date to see how sentiment was ON that day
    merged = pd.merge(fb_df, sentiment_df, left_on='datetime', right_on='date', how='inner')
    
    if merged.empty:
        print("No overlapping dates found for correlation.")
        return

    # Calculate correlation
    correlation = merged[['rm_xG', 'compound', 'rm_goals']].corr()
    print("\n--- Correlation Matrix ---")
    print(correlation)
    
    # Save correlation data
    os.makedirs("data/processed", exist_ok=True)
    merged.to_csv("data/processed/correlated_data.csv", index=False)
    
    # Chart 3: Correlation Scatter
    plt.figure(figsize=(10, 6))
    sns.regplot(data=merged, x='rm_xG', y='compound', scatter_kws={'alpha':0.5}, line_kws={'color':'#00529F'})
    plt.title('Correlation: Match Performance (xG) vs. News Sentiment', fontsize=14)
    plt.xlabel('Real Madrid xG (Created)')
    plt.ylabel('Avg News Sentiment (Compound)')
    plt.savefig('assets/correlation_plot.png', dpi=300)
    print("Saved: assets/correlation_plot.png")

if __name__ == "__main__":
    setup_nltk()
    
    # Check if files exist
    if not os.path.exists(PRE_CLASICO_FILE) or not os.path.exists(POST_CLASICO_FILE):
        print(f"Error: Raw news files not found in data/raw/. Run Day 1 script first.")
    else:
        df_pre = pd.read_csv(PRE_CLASICO_FILE)
        df_post = pd.read_csv(POST_CLASICO_FILE)
        
        df_pre = analyze_sentiment(df_pre, "Pre-Clasico")
        df_post = analyze_sentiment(df_post, "Post-Clasico")
        
        daily_sentiment = generate_sentiment_visuals(df_pre, df_post)
        correlate_performance_sentiment(daily_sentiment, FOOTBALL_STATS_FILE)
        
        print("\nSUCCESS: Day 3 sentiment analysis and correlation complete.")