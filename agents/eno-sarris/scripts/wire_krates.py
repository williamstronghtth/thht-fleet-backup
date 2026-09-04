from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

targets = [
    "O'Hearn", 'Vargas, Miguel', 'Isbel', 'Wiemer', 'Gimenez',
    'Young, Cole', 'Bell, Josh', 'Aranda', 'Garcia Jr',
    'Muncy, Max', 'Simpson', 'Bauers', 'Smith, Dominic',
    'Stanton', 'Alvarez, Francisco', 'Dingler'
]

df = batting_stats(2025, qual=50)
print("=== Wire Targets K% ===\n")
for t in targets:
    last = t.split(',')[0] if ',' in t else t.split()[-1]
    row = df[df['Name'].str.contains(last, case=False, na=False)]
    if len(row) > 1:
        if ',' in t:
            first = t.split(',')[1].strip().split()[0]
        elif len(t.split()) > 1:
            first = t.split()[0]
        else:
            first = None
        if first:
            row2 = row[row['Name'].str.contains(first, case=False, na=False)]
            if not row2.empty:
                row = row2
    if not row.empty:
        r = row.iloc[0]
        print(f"  {r['Name']:<24} K%={r['K%']:.1%}  BB%={r['BB%']:.1%}  wOBA={r['wOBA']:.3f}  PA={int(r['PA'])}")
    else:
        print(f"  {t:<24} not found")
