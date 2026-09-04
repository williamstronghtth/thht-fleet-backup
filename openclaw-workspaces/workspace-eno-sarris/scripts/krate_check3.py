from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

players = ['Schanuel', 'Dingler', 'Perdomo', 'Rocchio']

for year in [2025, 2024]:
    df = batting_stats(year, qual=50)
    print(f"\n=== {year} ===")
    for p in players:
        row = df[df['Name'].str.contains(p, case=False, na=False)]
        if not row.empty:
            r = row.iloc[0]
            print(f"{r['Name']}: K%={r['K%']:.1%}, BB%={r['BB%']:.1%}, wOBA={r['wOBA']:.3f}, PA={int(r['PA'])}")
        else:
            print(f"{p}: not found (under 50 PA)")
