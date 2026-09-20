import sqlite3
from pathlib import Path

conn = sqlite3.connect(":memory:")
conn.executescript(Path(__file__).with_name("elclosure.sql").read_text(encoding="utf-8"))

seed = set(conn.execute("SELECT s,p,o FROM cl").fetchall())
n_seed = len(seed)

def rules():
    return conn.execute("SELECT r1,r2,out,jpat FROM rule").fetchall()

def apply(rows):
    conn.executemany("INSERT INTO cl(s,p,o) VALUES (?,?,?)", rows)

def all_triples():
    return set(conn.execute("SELECT s,p,o FROM cl").fetchall())

print("== TBox(规则=数据,关系复合) ==")
for r1, r2, out, jpat in rules():
    print(f"  {r1:<8} ∘ {r2:<8} ⊑ {out:<7} [{jpat}]")
print()

# bottom-up 半朴素求值:每轮所有规则同时应用,直到不动点
round_no = 0
while True:
    round_no += 1
    new = set()
    for r1, r2, out, jpat in rules():
        q = None
        if jpat == "J1":   # a.x--r1-->a.o, a.o--r2-->b.o
            q = ("SELECT a.s, ?, b.o FROM cl a JOIN cl b ON a.o=b.s "
                 "WHERE a.p=? AND b.p=?")
        else:              # J2: a.x--r1-->a.o, b.s--r2-->a.o
            q = ("SELECT a.s, ?, b.s FROM cl a JOIN cl b ON a.o=b.o "
                 "WHERE a.p=? AND b.p=?")
        for row in conn.execute(q, (out, r1, r2)):
            new.add(tuple(row))
    new -= all_triples()
    if not new:
        break
    apply(list(new))
    print(f"  第 {round_no} 轮:新增 {len(new)} 条事实")
    for s, p, o in sorted(new):
        print(f"    {s:<5} {p:<8} {o}")
print(f"  收敛于第 {round_no} 轮(不动点),闭包共 {len(all_triples())} 条(种子 {n_seed})")
print()

term = {"partOf": "是…的部分", "isA": "是", "owns": "拥有", "buys": "买下"}
print("== 关键结论 ==")
questions = [
    ("李四买了 发动机/活塞/轮胎？", "SELECT o FROM cl WHERE s='李四' AND p='buys' AND o IN ('发动机','活塞','轮胎')"),
    ("李四拥有 发动机/活塞/轮胎？", "SELECT o FROM cl WHERE s='李四' AND p='owns' AND o IN ('发动机','活塞','轮胎')"),
    ("豪华发动机也是汽车的零件？", "SELECT COUNT(*) FROM cl WHERE s='豪华发动机' AND p='partOf' AND o='汽车'"),
    ("活塞属于动力系统？", "SELECT COUNT(*) FROM cl WHERE s='活塞' AND p='partOf' AND o='动力系统'"),
    ("王五拥有'车'品类？", "SELECT COUNT(*) FROM cl WHERE s='王五' AND p='owns' AND o='车'"),
]
for qname, q in questions:
    r = conn.execute(q).fetchall()
    ok = bool(r) and (r[0][0] if len(r) == 1 and isinstance(r[0][0], int) else bool(r))
    print(f"  {'◯' if ok else '✗'} {qname} {'(' + '、'.join(str(x[0]) for x in r) + ')' if ok else ''}")
conn.close()