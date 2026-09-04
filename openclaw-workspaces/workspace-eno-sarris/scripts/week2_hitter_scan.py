from pybaseball import batting_stats
import warnings
warnings.filterwarnings('ignore')

targets = [
    'Alvarez, Yordan', 'Baldwin, Drake', 'Aranda', 'Caminero',
    'Harris II', 'Arozarena', 'Witt Jr', 'Freeman', 'Herrera, Ivan',
    'Rocchio', 'Polanco', 'Manzardo', 'Varsho', 'Cronenworth',
    'Thomas, Alek', 'Jung', 'Bailey, Patrick', 'Dingler',
    'Stewart, Sal', 'Robert Jr', 'Walker, Jordan', 'Garcia, Maikel',
    'Cruz, Oneil', 'Bogaerts', 'Rice, Ben', 'Kurtz',
    'Greene, Riley', 'Perez, Salvador', 'Sánchez, Jesús',
    'Raley, Luke', 'Naylor, Josh', 'Grisham', 'Marte, Ketel',
    'Schwarber'
]

df = batting_stats(2025, qual=100)
print("=== 2025 K% Deep Dive — Week 2 Targets ===\n")

# Sort into buckets
low_k = []
mid_k = []
high_k = []

for t in targets:
    last = t.split(',')[0] if ',' in t else t.split()[-1]
    row = df[df['Name'].str.contains(last, case=False, na=False)]
    if len(row) > 1 and ',' in t:
        first = t.split(',')[1].strip().split()[0]
        row2 = row[row['Name'].str.contains(first, case=False, na=False)]
        if not row2.empty:
            row = row2
    if not row.empty:
        r = row.iloc[0]
        kpct = r['K%']
        entry = (r['Name'], kpct, r['BB%'], r['wOBA'], int(r['PA']))
        if kpct < 0.18:
            low_k.append(entry)
        elif kpct < 0.24:
            mid_k.append(entry)
        else:
            high_k.append(entry)

print("🟢 LOW K% (under 18%) — Format Gold")
for name, k, bb, woba, pa in sorted(low_k, key=lambda x: x[1]):
    print(f"  {name:<22} K%={k:.1%}  BB%={bb:.1%}  wOBA={woba:.3f}  PA={pa}")

print(f"\n🟡 MID K% (18-24%) — Manageable")
for name, k, bb, woba, pa in sorted(mid_k, key=lambda x: x[1]):
    print(f"  {name:<22} K%={k:.1%}  BB%={bb:.1%}  wOBA={woba:.3f}  PA={pa}")

print(f"\n🔴 HIGH K% (24%+) — Tax in our format")
for name, k, bb, woba, pa in sorted(high_k, key=lambda x: x[1]):
    print(f"  {name:<22} K%={k:.1%}  BB%={bb:.1%}  wOBA={woba:.3f}  PA={pa}")
