import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os

# Download VADER lexicon
nltk.download('vader_lexicon')

def analyze_sentiment():
    # 1. Load News Data
    pre_file = "data/raw/news_pre_clasico.csv"
    post_file = "data/raw/news_post_clasico.csv"
    
    if not os.path.exists(pre_file) or not os.path.exists(post_file):
        print("News data files not found. Please run the collector first.")
        return

    pre_df = pd.read_csv(pre_file)
    post_df = pd.read_csv(post_file)
    
    pre_df['period'] = 'Period 1 (Ascent)'
    post_df['period'] = 'Period 2 (Decline)'
    
    news_df = pd.concat([pre_df, post_df])
    
    # Handle date columns
    if 'pubDate' in news_df.columns:
        news_df['date'] = pd.to_datetime(news_df['pubDate'], errors='coerce')
    elif 'date' in news_df.columns:
        news_df['date'] = pd.to_datetime(news_df['date'], errors='coerce')
    else:
        print("Error: Could not find date column in news data.")
        return
        
    news_df = news_df.dropna(subset=['date'])
    
    # 2. Run VADER Sentiment
    sia = SentimentIntensityAnalyzer()
    news_df['sentiment_score'] = news_df['title'].apply(lambda x: sia.polarity_scores(str(x))['compound'])
    
    # 3. Load Football Data for Correlation
    fb_file = "data/processed/football_stats_v2.csv"
    if not os.path.exists(fb_file):
        print("Football stats file not found. Please run football_performance.py first.")
        return
        
    fb_df = pd.read_csv(fb_file)
    fb_df['datetime'] = pd.to_datetime(fb_df['datetime']).dt.date
    
    # Aggregate daily sentiment
    daily_sentiment = news_df.groupby(news_df['date'].dt.date)['sentiment_score'].mean().reset_index()
    daily_sentiment.columns = ['date', 'avg_sentiment']
    
    # Merge for correlation
    merged = pd.merge(fb_df, daily_sentiment, left_on='datetime', right_on='date', how='inner')
    
    if merged.empty:
        print("Warning: No overlapping dates found between football matches and news headlines.")
        return

    # 4. Comparative Correlation Analysis
    # Metrics to correlate against 'avg_sentiment'
    metrics = ['xG', 'xGA', 'goals_for', 'goals_against', 'ppda', 'deep']
    
    # Overall Correlation
    overall_corr = merged[['avg_sentiment'] + metrics].corr()['avg_sentiment'].drop('avg_sentiment')
    
    # Period 1 Correlation
    p1_data = merged[merged['period'] == 'Period 1 (Ascent)']
    p1_corr = p1_data[['avg_sentiment'] + metrics].corr()['avg_sentiment'].drop('avg_sentiment') if not p1_data.empty else pd.Series(dtype=float)
    
    # Period 2 Correlation
    p2_data = merged[merged['period'] == 'Period 2 (Decline)']
    p2_corr = p2_data[['avg_sentiment'] + metrics].corr()['avg_sentiment'].drop('avg_sentiment') if not p2_data.empty else pd.Series(dtype=float)
    
    # Combine for plotting
    corr_df = pd.DataFrame({
        'Overall': overall_corr,
        'Period 1 (Ascent)': p1_corr,
        'Period 2 (Decline)': p2_corr
    }).reset_index().rename(columns={'index': 'Metric'})
    
    # Melt for seaborn
    corr_melted = corr_df.melt(id_vars='Metric', var_name='Timeframe', value_name='Correlation with Sentiment')
    
    # --- VISUALIZATION ---
    os.makedirs('assets', exist_ok=True)
    sns.set_theme(style="whitegrid")
    
    # Chart: Comparative Correlation Bar Plot
    plt.figure(figsize=(12, 7))
    sns.barplot(data=corr_melted, x='Metric', y='Correlation with Sentiment', hue='Timeframe', palette='viridis')
    plt.title("Correlation Analysis: Media Sentiment vs. Football Metrics (Comparative)", fontsize=14)
    plt.axhline(0, color='black', linewidth=0.8)
    plt.ylim(-1, 1)
    plt.legend(title="Timeframe", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('assets/comparative_correlation_v2.png', dpi=300)
    plt.close()
    
    # Chart: Sentiment Distribution
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=news_df, x='sentiment_score', hue='period', fill=True)
    plt.title("Media Sentiment Distribution: The Xabi Alonso Narrative")
    plt.savefig('assets/sentiment_distribution_v2.png')
    plt.close()
    
    print("Comparative sentiment analysis complete. Generated 'assets/comparative_correlation_v2.png'.")
    print(f"Processed {len(news_df)} headlines.")

if __name__ == "__main__":
    analyze_sentiment()