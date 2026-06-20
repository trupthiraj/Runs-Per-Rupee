# Runs Per Rupee

What did IPL franchises actually get for their money?

Every year, franchise owners spend hundreds of crores in an auction room that runs on instinct, reputation, and occasionally panic. This project asks the question those owners probably should have asked first: when you look at what a player actually delivered on the pitch versus what you paid for them at auction, how does the maths work out?

Runs Per Rupee is the metric this project builds to answer that. Career output per match divided by crore paid. Applied to 1,085 real auction purchases across 11 seasons.

---

## What the data found

The best value buys in this dataset share one thing in common. They were all bought cheap, either because the franchise spotted something others missed, or because the player had not yet become expensive. Devon Conway at 1 crore for Chennai. KL Rahul at 1 crore for Sunrisers before anyone had priced him properly. Imran Tahir at 1 crore taking 86 wickets across his CSK career.

The worst value buys are the ones that made headlines. Mitchell Starc at 24.75 crore, the most expensive purchase in IPL history, returned 59 wickets at an economy that hurt KKR more than it helped them. Kyle Jamieson at 15 crore averaged 9.3 runs per match as a batter. Sam Curran at 18.5 crore, Ben Stokes at 16.25 crore, both sitting at the bottom of the bowling value table.

Rajasthan Royals top the franchise bowling table by a distance. They have consistently identified wicket-takers that the rest of the room undervalued. Chennai Super Kings are strong on both axes. Punjab Kings sit last with close to 400 crore spent and the worst value return of any permanent franchise in the dataset.

The pattern holds across every year in the data. The auction rewards reputation. The metric rewards performance.

---

## The Metric

Runs Per Rupee = career runs per match / crore paid at auction (batters)

Wickets Per Rupee = career wickets per match / crore paid at auction (bowlers)

Filters applied: minimum 1 crore purchase price, minimum 5 matches played. Both thresholds remove noise from base price fills and players who barely featured.

---

## Explore the Dashboard

Search any player by name to see every auction they appeared in, the price their franchise paid, and their RPR verdict.

[Open on Tableau Public](https://public.tableau.com/app/profile/trupthi.raj/viz/RunsPerRupeeIPLAuctionValueAnalysis20142024/RunsPerRupeeIPLAuctionValueAnalysis20142024)

---

## Data Sources

Ball-by-ball delivery data from Cricsheet via Kaggle, covering every IPL match from 2008 to 2024. 260,920 delivery records across 1,095 matches.

Auction price records from Kaggle covering 2014 to 2024. One row per player per auction year, including role, franchise, and final price paid.

No simulated data anywhere in this project. Every number came from a real delivery bowled or a real paddle raised.

---

## Project Structure
```

Runs Per Rupee/

├── data/

│   ├── deliveries.csv

│   ├── matches.csv

│   └── IPL_Auction/

│       ├── IPL_Auction_2014_Sold_Player.csv

│       └── ... (2014 to 2026)

├── scripts/

│   ├── 01_clean_and_join.py

│   ├── 02_calculate_rpr.py

│   ├── 03_franchise_analysis.py

│   ├── 04_visualise.py

│   └── analysis.sql

├── outputs/

│   ├── auction_clean.csv

│   ├── batting_rpr.csv

│   ├── bowling_rpr.csv

│   ├── franchise_scores.csv

│   ├── chart1_money_map.html

│   ├── chart2_inflation.html

│   ├── chart3_bowling.html

│   └── chart5_verdicts.html

├── explore.py

└── README.md

```

---

## Run It

```bash
python scripts/01_clean_and_join.py
python scripts/02_calculate_rpr.py
python scripts/03_franchise_analysis.py
python scripts/04_visualise.py
```

Python, pandas, Plotly, SQL, Tableau.

---

## Limitations

The performance data covers 2008 to 2024, but auction records only go back to 2014, so the overlap window is 2014 to 2024. Career stats use the full available history rather than just the season following each auction, which means a player bought in 2018 is judged on their entire IPL career rather than just their 2018 season performance. This is a deliberate choice; career output is a more stable signal than one season, but it is worth knowing.

---

## About

Built by Trupthi Raj, a data analyst with a focus on retail, commercial, luxury, sports, healthcare and consumer analytics.

[GitHub](https://github.com/trupthiraj) &nbsp;|&nbsp; [Tableau](https://public.tableau.com/app/profile/trupthi.raj) &nbsp;|&nbsp; [LinkedIn](https://www.linkedin.com/in/trupthi-raj/)
