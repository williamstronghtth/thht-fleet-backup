from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

df = batting_stats(2025, qual=50)

# Search more broadly for Raley
raley = df[df['Name'].str.contains('Rale', case=False, na=False)]
print("Raley search results:")
print(raley[['Name', 'K%', 'BB%', 'wOBA', 'PA']].to_string())

# Also check 2024 for both
df24 = batting_stats(2024, qual=50)
for p in ['Canzone', 'Raley']:
    row = df24[df24['Name'].str.contains(p, case=False, na=False)]
    if not row.empty:
        r = row.iloc[0]
        print(f"{r['Name']} (2024): K%={r['K%']}, BB%={r['BB%']}, wOBA={r['wOBA']}, PA={r['PA']}")
