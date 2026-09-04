from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

targets = ['Hamilton, David', 'Gimenez', 'Dubon', 'Young, Cole', 'Rocchio']

for year in [2025, 2024]:
    df = batting_stats(year, qual=50)
    print(f"\n=== {year} ===")
    for t in targets:
        last = t.split(',')[0] if ',' in t else t.split()[-1]
        row = df[df['Name'].str.contains(last, case=False, na=False)]
        if len(row) > 1 and ',' in t:
            first = t.split(',')[1].strip()
            row2 = row[row['Name'].str.contains(first, case=False, na=False)]
            if not row2.empty:
                row = row2
        if not row.empty:
            r = row.iloc[0]
            print(f"  {r['Name']:<22} K%={r['K%']:.1%}  BB%={r['BB%']:.1%}  wOBA={r['wOBA']:.3f}  SB={int(r.get('SB', 0))}  PA={int(r['PA'])}")
        else:
            print(f"  {t:<22} not found (under 50 PA)")
