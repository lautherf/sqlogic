import json, sqlite3, sys
from pathlib import Path

n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
sql = Path(__file__).with_name("queens.sql").read_text(encoding="utf-8").format(N=n)

conn = sqlite3.connect(":memory:")
rows = conn.execute(sql).fetchall()
conn.close()

print(f"{n} 皇后解数: {len(rows)}")
for no, sol in rows[:8]:
    print(f"  #{no}: {sol}")

if len(rows) > 0:
    first = json.loads(rows[0][1])
    print("第一个解的棋盘布局:")
    for q in first:
        print("  " + " ".join("Q" if i + 1 == q else "." for i in range(n)))