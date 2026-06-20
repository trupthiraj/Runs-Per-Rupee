import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── SETTINGS ───────────────────────────────────────────────────────────────────
BG     = '#1a1a2e'
PAPER  = '#1a1a2e'
GRID   = '#2a2a4a'
TEXT   = '#ffffff'
DIM    = '#8888aa'
ACCENT = '#e94560'
GOLD   = '#f5a623'
TEAL   = '#00b4d8'
GREEN  = '#2ecc71'

def base(title):
    return dict(
        title=dict(text=title, font=dict(color=TEXT, size=17)),
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
        font=dict(color=TEXT, family='Arial'),
        xaxis=dict(gridcolor=GRID, zeroline=False),
        yaxis=dict(gridcolor=GRID, zeroline=False),
        margin=dict(l=60, r=40, t=80, b=60)
    )

# ── LOAD ───────────────────────────────────────────────────────────────────────
bat     = pd.read_csv('outputs/batting_rpr.csv')
bowl    = pd.read_csv('outputs/bowling_rpr.csv')
auction = pd.read_csv('outputs/auction_clean.csv')

name_fix = {
    'Kings XI Punjab':             'Punjab Kings',
    'Delhi Daredevils':            'Delhi Capitals',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
    'Deccan Chargers':             'Sunrisers Hyderabad',
}
for df in [bat, bowl, auction]:
    df['TeamName'] = df['TeamName'].str.strip().replace(name_fix)

bat_f  = bat[(bat['price_crore'] >= 1) & (bat['matches_batted'] >= 5)].copy()
bowl_f = bowl[(bowl['price_crore'] >= 1) & (bowl['wickets'] >= 5)].copy()


# ── CHART 1: THE MONEY MAP (quadrant) ─────────────────────────────────────────
price_mid = bat_f['price_crore'].median()
rpm_mid   = bat_f['runs_per_match'].median()
x_max     = bat_f['price_crore'].max() * 1.08
y_max     = bat_f['runs_per_match'].max() * 1.08

def quadrant(row):
    cheap  = row['price_crore'] <= price_mid
    output = row['runs_per_match'] >= rpm_mid
    if cheap and output:       return 'Hidden Gem'
    if not cheap and output:   return 'Worth It'
    if not cheap and not output: return 'Robbery'
    return 'Underperformer'

bat_f['quad'] = bat_f.apply(quadrant, axis=1)

quad_color = {
    'Hidden Gem':     TEAL,
    'Worth It':       GREEN,
    'Robbery':        ACCENT,
    'Underperformer': '#666688'
}

gems     = bat_f[bat_f['quad'] == 'Hidden Gem'].nlargest(3, 'rpr_batting')
robbery  = bat_f[bat_f['quad'] == 'Robbery'].nsmallest(4, 'rpr_batting')
annotate = pd.concat([gems, robbery])

fig1 = go.Figure()

shapes = [
    dict(type='rect', x0=0, y0=rpm_mid, x1=price_mid, y1=y_max,
         fillcolor='rgba(0,180,216,0.06)', line=dict(width=0)),
    dict(type='rect', x0=price_mid, y0=rpm_mid, x1=x_max, y1=y_max,
         fillcolor='rgba(46,204,113,0.06)', line=dict(width=0)),
    dict(type='rect', x0=price_mid, y0=0, x1=x_max, y1=rpm_mid,
         fillcolor='rgba(233,69,96,0.08)', line=dict(width=0)),
    dict(type='rect', x0=0, y0=0, x1=price_mid, y1=rpm_mid,
         fillcolor='rgba(0,0,0,0)', line=dict(width=0)),
    dict(type='line', x0=price_mid, x1=price_mid, y0=0, y1=y_max,
         line=dict(color=GRID, width=1, dash='dot')),
    dict(type='line', x0=0, x1=x_max, y0=rpm_mid, y1=rpm_mid,
         line=dict(color=GRID, width=1, dash='dot')),
]

annotations = [
    dict(x=price_mid*0.45, y=y_max*0.95, text='HIDDEN GEMS',
         font=dict(color=TEAL, size=9), showarrow=False, opacity=0.7),
    dict(x=(price_mid+x_max)/2, y=y_max*0.95, text='WORTH IT',
         font=dict(color=GREEN, size=9), showarrow=False, opacity=0.7),
    dict(x=(price_mid+x_max)/2, y=rpm_mid*0.12, text='ROBBERY',
         font=dict(color=ACCENT, size=9), showarrow=False, opacity=0.7),
    dict(x=price_mid*0.45, y=rpm_mid*0.12, text='UNDERPERFORMERS',
         font=dict(color='#666688', size=9), showarrow=False, opacity=0.7),
]

for _, row in annotate.iterrows():
    annotations.append(dict(
        x=row['price_crore'], y=row['runs_per_match'],
        text=f"  {row['Name'].split()[-1]}",
        font=dict(color=TEXT, size=9),
        showarrow=True, arrowhead=0,
        arrowcolor=GRID, arrowwidth=1,
        ax=18, ay=-18
    ))

for quad, grp in bat_f.groupby('quad'):
    fig1.add_trace(go.Scatter(
        x=grp['price_crore'], y=grp['runs_per_match'],
        mode='markers', name=quad,
        marker=dict(color=quad_color[quad], size=7, opacity=0.75,
                    line=dict(width=0)),
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>'
            'Price: ₹%{x:.1f}Cr<br>Runs/Match: %{y:.1f}<extra></extra>'
        ),
        customdata=grp[['Name', 'TeamName']].values
    ))

fig1.update_layout(
    **base('The Money Map — Was the Auction Price Justified?'),
    xaxis_title='Auction Price (Crore ₹)',
    yaxis_title='Career Runs Per Match',
    shapes=shapes, annotations=annotations,
    legend=dict(bgcolor=BG, bordercolor=GRID, font=dict(color=TEXT))
)
fig1.write_html('outputs/chart1_money_map.html')
print("Saved: chart1_money_map.html")


# ── CHART 2: PRICE INFLATION BY YEAR ──────────────────────────────────────────
yearly = (
    auction[auction['price_crore'] >= 1]
    .groupby('auction_year')
    .agg(avg_price=('price_crore', 'mean'),
         max_price=('price_crore', 'max'))
    .reset_index()
)

top_per_year = (
    auction[auction['price_crore'] >= 1]
    .sort_values('price_crore', ascending=False)
    .groupby('auction_year').first()
    .reset_index()[['auction_year', 'Name', 'price_crore']]
)

fig2 = go.Figure()
fig2.add_trace(go.Scatter(
    x=yearly['auction_year'], y=yearly['avg_price'],
    mode='lines+markers', fill='tozeroy',
    fillcolor='rgba(245,166,35,0.12)',
    line=dict(color=GOLD, width=2.5),
    marker=dict(color=GOLD, size=7),
    name='Avg price',
    hovertemplate='<b>%{x}</b><br>Avg: ₹%{y:.2f}Cr<extra></extra>'
))
fig2.add_trace(go.Scatter(
    x=yearly['auction_year'], y=yearly['max_price'],
    mode='lines+markers',
    line=dict(color=ACCENT, width=1.5, dash='dot'),
    marker=dict(color=ACCENT, size=5),
    name='Top bid',
    hovertemplate='<b>%{x}</b><br>Top bid: ₹%{y:.2f}Cr<extra></extra>'
))

record_years = [2018, 2021, 2023, 2024]
ann2 = []
for _, row in top_per_year[top_per_year['auction_year'].isin(record_years)].iterrows():
    ann2.append(dict(
        x=row['auction_year'], y=row['price_crore'],
        text=f"{row['Name'].split()[-1]}<br>₹{row['price_crore']:.1f}Cr",
        font=dict(color=ACCENT, size=9),
        showarrow=True, arrowhead=0,
        arrowcolor=ACCENT, arrowwidth=1,
        ax=0, ay=-36, bgcolor=BG, borderpad=3
    ))
fig2.update_layout(
    **base('The Inflation Problem — Average Bid Has Tripled Since 2014'),
    xaxis_title='Auction Year',
    yaxis_title='Price (Crore ₹)',
    annotations=ann2,
    legend=dict(bgcolor=BG, bordercolor=GRID, font=dict(color=TEXT))
)
fig2.update_xaxes(dtick=1)

fig2.write_html('outputs/chart2_inflation.html')
print("Saved: chart2_inflation.html")


# ── CHART 3: ANNOTATED BOWLING OVERPAYS ───────────────────────────────────────
rpr_mid = bowl_f['rpr_bowling'].median()
bowl_f['value'] = bowl_f['rpr_bowling'].apply(
    lambda x: 'Good Value' if x >= rpr_mid else 'Poor Value'
)
expensive_bowl = bowl_f[bowl_f['price_crore'] >= 10].copy()

fig3 = go.Figure()
for val, grp in bowl_f.groupby('value'):
    color = TEAL if val == 'Good Value' else ACCENT
    fig3.add_trace(go.Scatter(
        x=grp['price_crore'], y=grp['wickets'],
        mode='markers', name=val,
        marker=dict(color=color, size=grp['price_crore'] * 1.2 + 4,
                    opacity=0.7, line=dict(width=0)),
        hovertemplate=(
            '<b>%{customdata[0]}</b><br>%{customdata[1]}<br>'
            'Price: ₹%{x:.1f}Cr<br>Wickets: %{y}<br>'
            'Economy: %{customdata[2]}<extra></extra>'
        ),
        customdata=grp[['Name', 'TeamName', 'economy']].values
    ))

ann3 = []
for _, row in expensive_bowl.iterrows():
    ann3.append(dict(
        x=row['price_crore'], y=row['wickets'],
        text=f"{row['Name'].split()[-1]}<br>₹{row['price_crore']:.1f}Cr",
        font=dict(color=TEXT, size=9),
        showarrow=True, arrowhead=0,
        arrowcolor=GRID, arrowwidth=1,
        ax=20, ay=-20, bgcolor=BG, borderpad=2
    ))

fig3.update_layout(
    **base('The Bowling Premium — Did the Big Buys Deliver?'),
    xaxis_title='Auction Price (Crore ₹)',
    yaxis_title='Career Wickets in IPL',
    annotations=ann3,
    legend=dict(bgcolor=BG, bordercolor=GRID, font=dict(color=TEXT))
)
fig3.write_html('outputs/chart3_bowling.html')
print("Saved: chart3_bowling.html")


# ── CHART 4: DOMESTIC vs INTERNATIONAL ────────────────────────────────────────
auction['is_indian'] = auction['Nationality'].str.strip().str.lower().apply(
    lambda x: 'Indian' if x == 'indian' else 'Overseas'
)

bat_nat = bat_f.merge(
    auction[['match_key', 'is_indian']].drop_duplicates('match_key'),
    on='match_key', how='left'
).dropna(subset=['is_indian'])

bowl_nat = bowl_f.merge(
    auction[['match_key', 'is_indian']].drop_duplicates('match_key'),
    on='match_key', how='left'
).dropna(subset=['is_indian'])

def nat_summary(df, metric):
    return (
        df.groupby('is_indian')
        .agg(avg_price=('price_crore', 'mean'),
             avg_rpr=(metric, 'mean'),
             count=('Name', 'count'))
        .reset_index()
    )

nat_bat  = nat_summary(bat_nat,  'rpr_batting')
nat_bowl = nat_summary(bowl_nat, 'rpr_bowling')

fig4 = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Batting — Runs Per Rupee', 'Bowling — Wickets Per Rupee'],
    horizontal_spacing=0.14
)

for nat in ['Indian', 'Overseas']:
    color = TEAL if nat == 'Indian' else GOLD
    rb = nat_bat[nat_bat['is_indian'] == nat]
    rl = nat_bowl[nat_bowl['is_indian'] == nat]

    fig4.add_trace(go.Bar(
        name=nat, x=[nat], y=rb['avg_rpr'].values,
        marker_color=color,
        text=[f"Avg ₹{rb['avg_price'].values[0]:.1f}Cr · n={rb['count'].values[0]}"],
        textposition='outside', textfont=dict(color=DIM, size=9),
        showlegend=True, legendgroup=nat
    ), row=1, col=1)

    fig4.add_trace(go.Bar(
        name=nat, x=[nat], y=rl['avg_rpr'].values,
        marker_color=color,
        text=[f"Avg ₹{rl['avg_price'].values[0]:.1f}Cr · n={rl['count'].values[0]}"],
        textposition='outside', textfont=dict(color=DIM, size=9),
        showlegend=False, legendgroup=nat
    ), row=1, col=2)

fig4.update_layout(
    **base('The Overseas Premium — Does Nationality Justify the Price?'),
    height=480, barmode='group',
    legend=dict(bgcolor=BG, bordercolor=GRID, font=dict(color=TEXT))
)
fig4.update_annotations(font=dict(color=DIM, size=12))
fig4.write_html('outputs/chart4_nationality.html')
print("Saved: chart4_nationality.html")


# ── CHART 5: PLAYER VERDICT CARDS (HTML) ──────────────────────────────────────
top5_bat  = bat_f.nlargest(5, 'rpr_batting').reset_index(drop=True)
bot5_bat  = bat_f.nsmallest(5, 'rpr_batting').reset_index(drop=True)
top5_bowl = bowl_f.nlargest(5, 'rpr_bowling').reset_index(drop=True)
bot5_bowl = bowl_f.nsmallest(5, 'rpr_bowling').reset_index(drop=True)

def card(row, verdict, color, emoji, metric_val, metric_label):
    return f"""
<div class="card" style="border-top: 3px solid {color};">
  <div class="verdict-badge" style="color:{color};">{emoji} {verdict}</div>
  <div class="player">{row['Name']}</div>
  <div class="team">{row['TeamName']}</div>
  <div class="year">{int(row['auction_year'])}</div>
  <div class="metrics">
    <div class="metric">
      <div class="val">₹{row['price_crore']:.1f}Cr</div>
      <div class="lbl">PAID</div>
    </div>
    <div class="metric">
      <div class="val">{metric_val}</div>
      <div class="lbl">{metric_label}</div>
    </div>
    <div class="metric">
      <div class="val" style="color:{color};">{verdict}</div>
      <div class="lbl">VERDICT</div>
    </div>
  </div>
</div>"""

def section(title, color, cards_html):
    return f"""
<div class="section">
  <div class="section-title" style="color:{color};">{title}</div>
  <div class="cards">{cards_html}</div>
</div>"""

bat_gems  = ''.join([card(r, 'BARGAIN', TEAL,  '💎', f"{r['runs_per_match']:.1f}", 'RUNS/MATCH') for _, r in top5_bat.iterrows()])
bat_rob   = ''.join([card(r, 'ROBBERY', ACCENT,'🚨', f"{r['runs_per_match']:.1f}", 'RUNS/MATCH') for _, r in bot5_bat.iterrows()])
bowl_gems = ''.join([card(r, 'BARGAIN', TEAL,  '💎', str(int(r['wickets'])), 'WICKETS') for _, r in top5_bowl.iterrows()])
bowl_rob  = ''.join([card(r, 'ROBBERY', ACCENT,'🚨', str(int(r['wickets'])), 'WICKETS') for _, r in bot5_bowl.iterrows()])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Runs Per Rupee — Verdicts</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: {BG}; font-family: Arial, sans-serif; color: {TEXT}; padding: 48px 40px; }}
.header {{ margin-bottom: 52px; }}
.title {{ font-size: 32px; font-weight: 700; letter-spacing: -0.5px; }}
.title span {{ color: {GOLD}; }}
.subtitle {{ color: {DIM}; font-size: 13px; margin-top: 8px; letter-spacing: 0.04em; }}
.section {{ margin-bottom: 52px; }}
.section-title {{ font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid {GRID}; }}
.cards {{ display: flex; gap: 14px; flex-wrap: wrap; }}
.card {{ background: #0d0d1f; border-radius: 10px; padding: 18px 16px 16px; width: 178px; flex-shrink: 0; }}
.verdict-badge {{ font-size: 9px; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 12px; }}
.player {{ font-size: 15px; font-weight: 700; line-height: 1.25; margin-bottom: 3px; }}
.team {{ font-size: 10px; color: {DIM}; line-height: 1.4; }}
.year {{ font-size: 10px; color: {DIM}; margin-bottom: 14px; }}
.metrics {{ display: flex; justify-content: space-between; gap: 4px; }}
.metric {{ text-align: center; flex: 1; }}
.val {{ font-size: 13px; font-weight: 700; }}
.lbl {{ font-size: 7px; color: {DIM}; letter-spacing: 0.06em; margin-top: 3px; }}
.divider {{ border: none; border-top: 1px solid {GRID}; margin: 48px 0; }}
</style>
</head>
<body>
<div class="header">
  <div class="title">Runs Per <span>Rupee</span></div>
  <div class="subtitle">IPL AUCTION VALUE ANALYSIS · 2014–2024 · MIN ₹1CR · MIN 5 MATCHES</div>
</div>
{section('💎 Batting Bargains — Best runs per crore', TEAL, bat_gems)}
{section('🚨 Batting Robberies — Worst runs per crore', ACCENT, bat_rob)}
<hr class="divider">
{section('💎 Bowling Bargains — Best wickets per crore', TEAL, bowl_gems)}
{section('🚨 Bowling Robberies — Worst wickets per crore', ACCENT, bowl_rob)}
</body>
</html>"""

with open('outputs/chart5_verdicts.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Saved: chart5_verdicts.html")

print()
print("All 5 charts saved to outputs/")