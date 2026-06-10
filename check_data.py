import pandas as pd
pre = pd.read_csv("data/raw/news_pre_clasico.csv")
post = pd.read_csv("data/raw/news_post_clasico.csv")
print(f"Pre-Clasico Headlines: {len(pre)}")
print(f"Post-Clasico Headlines: {len(post)}"
print("\nMissing Values:")
print(pre.isnull().sum())
print("\nSample Headlines:")
print(pre['title'].head())
