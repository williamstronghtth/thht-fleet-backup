from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

players = ['Rocchio', 'Lowe, Brandon']

for year in [2025, 2024]:
    df = batting_stats(year, qual=50)
    print(f"\n=== {year} ===")
    for p in ['Rocchio', 'Brandon Lowe']:
        row = df[df['Name'].str.contains(p.split()[-1], case=False, na=False)]
        # filter for first name if multiple results
        if 'Brandon' in p and len(row) > 1:
            row = row[row['Name'].str.contains('Brandon', case=False, na=False)]
        if not row.empty:
            r = row.iloc[0]
            cols = ['Name', 'PA', 'K%', 'BB%', 'AVG', 'wOBA', 'xwOBA', 'xBA', 'Barrel%', 'HardHit%', 'O-Swing%', 'SwStr%', 'BABIP']
            available = [c for c in cols if c in r.index]
            print(f"\n{r['Name']}:")
            for c in available:
                val = r[c]
                if isinstance(val, float):
                    if c in ['K%', 'BB%', 'Barrel%', 'HardHit%', 'O-Swing%', 'SwStr%']:
                        print(f"  {c}: {val:.1%}")
                    else:
                        print(f"  {c}: {val:.3f}")
                else:
                    print(f"  {c}: {val}")
        else:
            print(f"{p}: not found")
