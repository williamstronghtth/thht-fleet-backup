from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

players = ['Walker, Jordan', 'Langeliers', 'Herrera', 'Langford', 'Montgomery, Colson', 'Mayo']

for year in [2025, 2024]:
    df = batting_stats(year, qual=50)
    print(f"\n=== {year} ===")
    searches = [
        ('Jordan Walker', 'Walker'),
        ('Shea Langeliers', 'Langeliers'),
        ('Ivan Herrera', 'Herrera'),
        ('Wyatt Langford', 'Langford'),
        ('Colson Montgomery', 'Montgomery'),
        ('Coby Mayo', 'Mayo'),
    ]
    for label, search in searches:
        row = df[df['Name'].str.contains(search, case=False, na=False)]
        if len(row) > 1:
            # Try to narrow by first name
            first = label.split()[0]
            row2 = row[row['Name'].str.contains(first, case=False, na=False)]
            if not row2.empty:
                row = row2
        if not row.empty:
            r = row.iloc[0]
            print(f"  {r['Name']}: K%={r['K%']:.1%}, BB%={r['BB%']:.1%}, wOBA={r['wOBA']:.3f}, PA={int(r['PA'])}")
        else:
            print(f"  {label}: not found (under 50 PA)")
