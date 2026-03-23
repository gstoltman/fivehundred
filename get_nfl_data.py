import requests
import os
import pandas as pd
import re
from constants import TEAM_PAGES, TAGS

def extract_teams():
    current_path = os.getcwd()
    file_path = os.path.join(current_path, 'exports/')
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    combined_df = pd.DataFrame()

    for team, url in TEAM_PAGES.items():
        headers = {'User-Agent': 'get_nfl_win_loss_totals'}
        response = requests.get(url, headers=headers, timeout=60)
        tables = pd.read_html(response.text)
        for t in tables:
            # Team wikis have multi-level W/L headers, extracting the bottom of those
            cols = t.columns.get_level_values(-1) if isinstance(t.columns, pd.MultiIndex) else t.columns
            if 'Season' in cols:
                df = t
                break
        # remove junk references from column headers
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(1)
        df.columns = [re.sub(r'\[\d+\]', '', col).strip() for col in df.columns]
        # removes junk rows
        df = df[df['Season'].astype(str).str.match(r'^\d{4}$')]
        keep_cols = [c for c in ['Season', 'League', 'Conference', 'Division', 'W', 'L', 'Head Coach'] if c in df.columns]
        df = df[keep_cols]
        df.insert(2, 'Team Name', team)
        combined_df = pd.concat([combined_df, df], ignore_index=True)

    return combined_df

def clean_text(value):
    pattern = "|".join(re.escape(tag) for tag in TAGS)
    s = str(value)
    s = re.sub(pattern, "", s)  # remove all tags
    return s.strip()

def clean_df(df):
    return df.map(clean_text)

combined_df = extract_teams()

final_df = clean_df(combined_df)

final_df.to_csv("nfl_seasons.csv", index=False)
    
