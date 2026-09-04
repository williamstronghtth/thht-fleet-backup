from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

df = batting_stats(2025, qual=50)
players = ['Canzone', 'Raley']
for p in players:
    row = df[df['Name'].str.contains(p, case=False, na=False)]
    if not row.empty:
        r = row.iloc[0]
        kpct = r.get('K%', 'N/A')
        bbpct = r.get('BB%', 'N/A')
        woba = r.get('wOBA', 'N/A')
        pa = r.get('PA', 'N/A')
        print(f"{r['Name']} (2025): K%={kpct}, BB%={bbpct}, wOBA={woba}, PA={pa}")
    else:
        print(f"{p}: not found")
