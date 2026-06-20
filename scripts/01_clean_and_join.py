import pandas as pd
import os
import glob

# ── HELPER: build match key from any name format ───────────────────────────────
# Works on both "Virat Kohli" and "V Kohli" → "v_kohli"
def make_key(name):
    parts = str(name).strip().split()
    if len(parts) < 2:
        return parts[0][0].lower() + '_unknown'
    return parts[0][0].lower() + '_' + parts[-1].lower()

# ── 1. LOAD & STACK ALL AUCTION FILES ─────────────────────────────────────────
auction_files = glob.glob('data/IPL_Auction/IPL_Auction_*.csv')
dfs = []
for f in auction_files:
    year = int(os.path.basename(f).split('_')[2])
    df = pd.read_csv(f)
    df['auction_year'] = year
    dfs.append(df)

auction = pd.concat(dfs, ignore_index=True)
auction.drop(columns=['Unnamed: 0'], errors='ignore', inplace=True)

# Clean price
auction['price_rs'] = (
    auction['Price in rs']
    .str.strip()
    .str.replace(',', '', regex=False)
    .astype(float)
)
auction = auction.dropna(subset=['price_rs'])
auction['price_rs'] = auction['price_rs'].astype(int)
auction['price_crore'] = (auction['price_rs'] / 1e7).round(2)
auction['match_key'] = auction['Name'].apply(make_key)

print(f"Total auction records: {len(auction)}")
print(f"Years covered: {sorted(auction['auction_year'].unique())}")
print(auction[['Name', 'match_key', 'price_crore', 'auction_year']].head(5))
print()

# ── 2. LOAD PERFORMANCE DATA ───────────────────────────────────────────────────
matches = pd.read_csv('data/matches.csv')
deliveries = pd.read_csv('data/deliveries.csv')

matches['season_year'] = matches['season'].str[:4].astype(int)
deliveries = deliveries.merge(
    matches[['id', 'season_year']],
    left_on='match_id',
    right_on='id',
    how='left'
)

print(f"Deliveries loaded: {len(deliveries)}")
print(f"Season years: {sorted(deliveries['season_year'].unique())}")
print()

# ── 3. BATTING STATS ───────────────────────────────────────────────────────────
batting = (
    deliveries.groupby('batter')
    .agg(
        runs=('batsman_runs', 'sum'),
        balls=('batsman_runs', 'count'),
        matches_batted=('match_id', 'nunique')
    )
    .reset_index()
)
batting['strike_rate'] = (batting['runs'] / batting['balls'] * 100).round(1)
batting['runs_per_match'] = (batting['runs'] / batting['matches_batted']).round(2)
batting['match_key'] = batting['batter'].apply(make_key)

print(f"Batting records: {len(batting)}")
print(batting.sort_values('runs', ascending=False).head(5)[
    ['batter', 'match_key', 'runs', 'matches_batted', 'strike_rate']
])
print()

# ── 4. BOWLING STATS ───────────────────────────────────────────────────────────
bowling = (
    deliveries.groupby('bowler')
    .agg(
        balls_bowled=('total_runs', 'count'),
        runs_conceded=('total_runs', 'sum'),
        wickets=('is_wicket', 'sum')
    )
    .reset_index()
)
bowling['economy'] = (bowling['runs_conceded'] / bowling['balls_bowled'] * 6).round(2)
bowling['wickets_per_match'] = (
    bowling['wickets'] / (bowling['balls_bowled'] / 6 / 20)
).round(2)
bowling['match_key'] = bowling['bowler'].apply(make_key)

print(f"Bowling records: {len(bowling)}")
print(bowling.sort_values('wickets', ascending=False).head(5)[
    ['bowler', 'match_key', 'wickets', 'economy']
])
print()

# ── 5. SAVE ────────────────────────────────────────────────────────────────────
auction.to_csv('outputs/auction_clean.csv', index=False)
batting.to_csv('outputs/batting_stats.csv', index=False)
bowling.to_csv('outputs/bowling_stats.csv', index=False)

print("Saved: outputs/auction_clean.csv")
print("Saved: outputs/batting_stats.csv")
print("Saved: outputs/bowling_stats.csv")