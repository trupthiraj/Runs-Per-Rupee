import pandas as pd

# ── LOAD ───────────────────────────────────────────────────────────────────────
bat = pd.read_csv('outputs/batting_rpr.csv')
bowl = pd.read_csv('outputs/bowling_rpr.csv')

# ── NORMALISE FRANCHISE NAMES ──────────────────────────────────────────────────
franchise_map = {
    'Kings XI Punjab':                'Punjab Kings',
    'Delhi Daredevils':               'Delhi Capitals',
    'Royal Challengers Bangalore':    'Royal Challengers Bengaluru',
    'Deccan Chargers':                'Sunrisers Hyderabad',
}

def normalise_team(name):
    name = str(name).strip()
    return franchise_map.get(name, name)

bat['TeamName']  = bat['TeamName'].apply(normalise_team)
bowl['TeamName'] = bowl['TeamName'].apply(normalise_team)


# ── APPLY SAME FILTERS AS BEFORE ──────────────────────────────────────────────
bat_f  = bat[(bat['price_crore'] >= 1) & (bat['matches_batted'] >= 5)].copy()
bowl_f = bowl[(bowl['price_crore'] >= 1) & (bowl['wickets'] >= 5)].copy()

# ── FRANCHISE BATTING SUMMARY ──────────────────────────────────────────────────
franchise_bat = (
    bat_f.groupby('TeamName')
    .agg(
        total_spend_crore=('price_crore', 'sum'),
        avg_rpr_batting=('rpr_batting', 'mean'),
        num_purchases=('Name', 'count'),
        best_pick=('rpr_batting', 'max')
    )
    .round(2)
    .reset_index()
    .sort_values('avg_rpr_batting', ascending=False)
)

print("=== FRANCHISE BATTING VALUE (avg runs per rupee) ===")
print(franchise_bat.to_string(index=False))
print()

# ── FRANCHISE BOWLING SUMMARY ──────────────────────────────────────────────────
franchise_bowl = (
    bowl_f.groupby('TeamName')
    .agg(
        total_spend_crore=('price_crore', 'sum'),
        avg_rpr_bowling=('rpr_bowling', 'mean'),
        num_purchases=('Name', 'count'),
        best_pick=('rpr_bowling', 'max')
    )
    .round(3)
    .reset_index()
    .sort_values('avg_rpr_bowling', ascending=False)
)

print("=== FRANCHISE BOWLING VALUE (avg wickets per rupee) ===")
print(franchise_bowl.to_string(index=False))
print()

# ── COMBINED FRANCHISE SCORE ───────────────────────────────────────────────────
combined = franchise_bat[['TeamName', 'avg_rpr_batting']].merge(
    franchise_bowl[['TeamName', 'avg_rpr_bowling']],
    on='TeamName',
    how='outer'
).fillna(0)

# Normalise both metrics to 0-100 scale then average
combined['bat_score'] = (
    (combined['avg_rpr_batting'] - combined['avg_rpr_batting'].min()) /
    (combined['avg_rpr_batting'].max() - combined['avg_rpr_batting'].min()) * 100
).round(1)

combined['bowl_score'] = (
    (combined['avg_rpr_bowling'] - combined['avg_rpr_bowling'].min()) /
    (combined['avg_rpr_bowling'].max() - combined['avg_rpr_bowling'].min()) * 100
).round(1)

combined['franchise_value_score'] = (
    (combined['bat_score'] + combined['bowl_score']) / 2
).round(1)

combined = combined.sort_values('franchise_value_score', ascending=False)

print("=== OVERALL FRANCHISE VALUE SCORE (0-100) ===")
print(combined[['TeamName', 'bat_score', 'bowl_score',
                'franchise_value_score']].to_string(index=False))

# ── SAVE ───────────────────────────────────────────────────────────────────────
franchise_bat.to_csv('outputs/franchise_batting.csv', index=False)
franchise_bowl.to_csv('outputs/franchise_bowling.csv', index=False)
combined.to_csv('outputs/franchise_scores.csv', index=False)

print()
print("Saved: outputs/franchise_batting.csv")
print("Saved: outputs/franchise_bowling.csv")
print("Saved: outputs/franchise_scores.csv")