import sqlite3
from pathlib import Path

sql = Path(__file__).with_name("chase.sql").read_text(encoding="utf-8").rstrip().rstrip(";")
conn = sqlite3.connect(":memory:")
base = conn.execute("""
  WITH fact(sub, pred, obj) AS (
    VALUES
      ('c1', 'rdf:type',     'course'),
      ('c2', 'rdf:type',     'course'),
      ('c3', 'rdf:type',     'course'),
      ('t1', 'rdf:type',     'instructor'),
      ('c1', 'instructedBy', 't1')
  ) SELECT * FROM fact
""").fetchall()

print("== ABox 种子事实 ==")
for sub, pred, obj in base:
    print(f"  {sub:<3} {pred:<13} {obj}")
print()

need = conn.execute("""
  WITH fact(sub, pred, obj) AS (
    VALUES
      ('c1', 'rdf:type', 'course'), ('c2', 'rdf:type', 'course'),
      ('c3', 'rdf:type', 'course'), ('t1', 'rdf:type', 'instructor'),
      ('c1', 'instructedBy', 't1')
  )
  SELECT sub FROM fact WHERE pred='rdf:type' AND obj='course'
  EXCEPT SELECT sub FROM fact WHERE pred='instructedBy'
""").fetchall()
print("== 触发 R1(存在量词)的课程 ==")
print("  " + ", ".join(r[0] for r in need))
print("  → 为它们生成全新个体 f_<课程>")
print()

for title, query in [
    ("== 物化闭包全部事实(R1 新个体 + R2 逆关系) ==",
     "SELECT sub, pred, obj FROM (" + sql + ") ORDER BY sub, pred, obj"),
    ("== 课程 → 教师(物化后) ==",
     "SELECT o.sub, o.obj FROM (" + sql + ") o WHERE o.pred='instructedBy'"),
    ("== 教师 → 课程(逆关系推导) ==",
     "SELECT o.sub, o.obj FROM (" + sql + ") o WHERE o.pred='teaches'"),
    ("== 新生成的个体类型断言 ==",
     "SELECT o.obj||' → '||o.pred||' '||o.sub FROM (" + sql + ") o "
     "WHERE o.obj LIKE 'f_%'"),
]:
    print(title)
    for row in conn.execute(query):
        print(f"  {' | '.join(str(x) for x in row)}")
    print()

print("== 闭包收敛检查:仍有缺教师的课程吗? ==")
left = conn.execute(
    "WITH m AS (" + sql + ") "
    "SELECT DISTINCT sub FROM m "
    "WHERE pred='rdf:type' AND obj='course' "
    "EXCEPT SELECT sub FROM m WHERE pred='instructedBy'"
).fetchall()
print("  无(物化一轮后每个课程都有教师)" if not left else f"  仍有: {left}")
conn.close()