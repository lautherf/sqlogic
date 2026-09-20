import sqlite3
from pathlib import Path

sql = Path(__file__).with_name("farmer.sql").read_text(encoding="utf-8").rstrip().rstrip(";")
conn = sqlite3.connect(":memory:")
rows = conn.execute(sql).fetchall()
conn.close()

solutions = sorted(rows, key=lambda r: r[1])
best = solutions[0][1]

print(f"安全状态数: 10 个(16 个中剔除 6 个危险状态)")
print(f"最短步数: {best}")
print(f"最短解法数: {sum(1 for _, s in solutions if s == best)}")
print()

def describe(state):
    f, w, g, c = (state >> 3) & 1, (state >> 2) & 1, (state >> 1) & 1, state & 1
    def bank(x): return "左岸" if x == 0 else "右岸"
    return (f"F={bank(f)} W={bank(w)} G={bank(g)} C={bank(c)}")

for route, steps in solutions[:3]:
    states = [int(x, 2) for x in route.split()]
    print(f"-- {steps} 步 --")
    prev = None
    for i, st in enumerate(states):
        if i == 0:
            print(f"  初态           ({st:04b}) " + describe(st))
            prev = st
            continue
        crossed = []
        pf, pw, pg, pc = (prev >> 3)&1, (prev >> 2)&1, (prev >> 1)&1, prev&1
        nf, nw, ng, nc = (st >> 3)&1, (st >> 2)&1, (st >> 1)&1, st&1
        if pf != nf: crossed.append("农民")
        if pw != nw: crossed.append("狼")
        if pg != ng: crossed.append("羊")
        if pc != nc: crossed.append("菜")
        print(f"  第{i}步  过河: {'、'.join(crossed):<5} ({st:04b}) " + describe(st))
        prev = st
    print()