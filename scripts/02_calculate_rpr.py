import pandas as pd

# ── LOAD ───────────────────────────────────────────────────────────────────────
auction = pd.read_csv('outputs/auction_clean.csv')
batting = pd.read_csv('outputs/batting_stats.csv')
bowling = pd.read_csv('outputs/bowling_stats.csv')

# ── STANDARDISE ROLES ──────────────────────────────────────────────────────────
def classify_role(role):
    if pd.isna(role):
        return 'unknown'
    role = str(role).lower()
    if 'all' in role:
        return 'allrounder'
    elif any(x in role for x in ['bat', 'wicket']):
        return 'batter'
    elif 'bowl' in role:
        return 'bowler'
    return 'unknown'

auction['role_clean'] = auction['Role'].apply(classify_role)

print("Role distribution:")
print(auction['role_clean'].value_counts())
print()

# ── SPLIT AUCTION BY ROLE ──────────────────────────────────────────────────────
auction_bat  = auction[auction['role_clean'].isin(['batter', 'allrounder'])].copy()
auction_bowl = auction[auction['role_clean'].isin(['bowler', 'allrounder'])].copy()

# ── MATCH ON INITIAL + SURNAME ─────────────────────────────────────────────────
matched_bat = auction_bat.merge(
    batting[['match_key', 'runs', 'balls', 'matches_batted',
             'strike_rate', 'runs_per_match']],
    on='match_key',
    how='inner'
)

matched_bowl = auction_bowl.merge(
    bowling[['match_key', 'balls_bowled', 'runs_conceded',
             'wickets', 'economy', 'wickets_per_match']],
    on='match_key',
    how='inner'
)

print(f"Auction batters/allrounders:  {len(auction_bat)}")
print(f"Matched to batting stats:     {len(matched_bat)}")
print()
print(f"Auction bowlers/allrounders:  {len(auction_bowl)}")
print(f"Matched to bowling stats:     {len(matched_bowl)}")
print()

# ── CALCULATE RUNS PER RUPEE ───────────────────────────────────────────────────
matched_bat['rpr_batting'] = (
    matched_bat['runs_per_match'] / matched_bat['price_crore']
).round(4)

matched_bowl['rpr_bowling'] = (
    matched_bowl['wickets_per_match'] / matched_bowl['price_crore']
).round(6)

# ── RESULTS: filter >= 1 crore to focus on meaningful purchases ────────────────
bat_filtered  = matched_bat[
    (matched_bat['price_crore'] >= 1) &
    (matched_bat['matches_batted'] >= 5)
].copy()

bowl_filtered = matched_bowl[
    (matched_bowl['price_crore'] >= 1) &
    (matched_bowl['wickets'] >= 5)
].copy()

bat_cols  = ['Name', 'TeamName', 'auction_year', 'price_crore',
             'runs_per_match', 'strike_rate', 'rpr_batting']
bowl_cols = ['Name', 'TeamName', 'auction_year', 'price_crore',
             'wickets', 'economy', 'rpr_bowling']

print("=== TOP 10 BATTING VALUE (best runs per rupee, min 1 crore) ===")
print(bat_filtered.sort_values('rpr_batting', ascending=False)[bat_cols]
      .head(10).to_string(index=False))

print()
print("=== BOTTOM 10 BATTING VALUE (worst runs per rupee, min 1 crore) ===")
print(bat_filtered.sort_values('rpr_batting')[bat_cols]
      .head(10).to_string(index=False))

print()
print("=== TOP 10 BOWLING VALUE (best wickets per rupee, min 1 crore) ===")
print(bowl_filtered.sort_values('rpr_bowling', ascending=False)[bowl_cols]
      .head(10).to_string(index=False))

print()
print("=== BOTTOM 10 BOWLING VALUE (worst wickets per rupee, min 1 crore) ===")
print(bowl_filtered.sort_values('rpr_bowling')[bowl_cols]
      .head(10).to_string(index=False))

# ── SAVE ───────────────────────────────────────────────────────────────────────
matched_bat.to_csv('outputs/batting_rpr.csv', index=False)
matched_bowl.to_csv('outputs/bowling_rpr.csv', index=False)

print()
print("Saved: outputs/batting_rpr.csv")
print("Saved: outputs/bowling_rpr.csv")