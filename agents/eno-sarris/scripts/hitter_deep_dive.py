from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

# Players to check K-rates for based on Statcast signals
targets = [
    'Altuve', 'Yandy Diaz', 'Aranda', 'Schanuel', 'Frelick',
    'Perdomo', 'Langeliers', 'Herrera', 'Caminero', 'Alvarez',
    'Jordan Walker', 'Wiemer', 'Caissie', 'Rutschman',
    'Nimmo', 'De La Cruz', 'Freeman'
]

df = batting_stats(2025, qual=100)
print("=== 2025 K% for Key Names ===")
for t in targets:
    last = t.split()[-1]
    row = df[df['Name'].str.contains(last, case=False, na=False)]
    if len(row) > 1 and len(t.split()) > 1:
        first = t.split()[0]
        row2 = row[row['Name'].str.contains(first, case=False, na=False)]
        if not row2.empty:
            row = row2
    if not row.empty:
        r = row.iloc[0]
        print(f"  {r['Name']:<22} K%={r['K%']:.1%}  BB%={r['BB%']:.1%}  wOBA={r['wOBA']:.3f}  PA={int(r['PA'])}")
    else:
        print(f"  {t:<22} not found (under 100 PA)")
