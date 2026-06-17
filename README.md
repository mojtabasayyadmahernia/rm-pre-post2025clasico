Real Madrid's Xabi Alonso: A Data-Driven Post-Mortem



This project analyzes the rise and fall of Xabi Alonso's tenure at Real Madrid during the 2025/26 season. By correlating  metrics with news sentiment, I explore the narrative that a loss of tactical control and locker room influence followed the first El Clásico of the season.



\### Project Structure \& Narrative



The analysis is divided into two distinct periods:



1\.

Period 1 (The Ascent): Aug 1, 2025 – Oct 26, 2025. Characterized by high-intensity pressing, tactical discipline, and positive media coverage.



2\.

Period 2 (The Decline): Oct 26, 2025 – Jan 12, 2026. Following the first Clásico, metrics show a significant drop in pressing intensity (PPDA) and attacking penetration (Deep Entries), ending in Xabi's dismissal after the Supercopa defeat.



\### Technical Pipeline



1\. Data Collection (collect\_news.py)



Source: Google News RSS.



Method: Weekly date-chunking to retrieve 1,000 headlines across both periods.



Logic: Bypasses the 100-result limit by iterating through 7-day windows.



2. Football Performance Analysis (analyze\_football.py)



Source: Understat (Match-level tactical data).



Metrics:



xG \& xGA: Expected goals created and conceded.



PPDA: Passes Per Defensive Action (Pressing intensity).



Deep: Passes completed within 20 yards of the opponent's goal.



xPTS: Expected points based on match performance.



Visuals: Scatter plots with regression trends and period comparisons.



3\. Sentiment \& Correlation Analysis (sentiment\_analysis.py)



NLP Engine: VADER Sentiment Analysis.



Correlation: Merges tactical metrics with daily sentiment scores to identify which performance factors most influence media narrative.



Visuals: Sentiment trend lines and correlation heatmaps.





\###How to Run



1. Install Dependencies:



Bash



pip install requests beautifulsoup4 pandas matplotlib seaborn nltk lxml





2.News Collection: 



Bash 



python collect\_news.py



3\. Conduct Football Metrics Analysis: 



Bash



python analyze\_football.py



4\. Run Sentiment Analysis: 



Bash



python sentiment\_analysis.py





\###Key Findings



* PPDA increased by over 50% in Period 2, indicating a collapse in Alonso's signature high-press system.



* Media Correlation: Sentiment was most strongly correlated with xG and Deep Entries, suggesting the media reacted more to the loss of attacking "identity" than just the final results.



* Turning Point: Visual trends show the decline began almost immediately after the October 26th Clásico, supporting the "loss of locker room" narrative.





