import sqlite3
from pathlib import Path

conn = sqlite3.connect(":memory:")
conn.executescript(Path(__file__).with_name("ontology.sql").read_text(encoding="utf-8"))


def show(title, rows, align=None):
    print(f"== {title} ==")
    if not rows:
        print("  (空)")
    for r in rows:
        print("  " + " | ".join(str(x) for x in r))
    print()


show("1. 关系 Instance:谁在什么时候买了多少(关系=枢纽)",
     conn.execute("""
       SELECT c.name AS 用户, pr.name AS 商品, p.qty AS 数量, p.at AS 时间
       FROM purchase p
       JOIN customer c ON c.id = p.customer_id
       JOIN product  pr ON pr.id = p.product_id
       ORDER BY p.at
     """))

show("2. Rule R1:商品 → 分类 → 大类(递归 CTE 推导出顶层分类)",
     conn.execute("""
       WITH RECURSIVE up(id, root) AS (
         SELECT id, id FROM category WHERE parent_id IS NULL
         UNION ALL
         SELECT c.id, up.root FROM category c JOIN up ON c.parent_id = up.id
       )
       SELECT pr.name AS 商品, b.name AS 品牌, rc.name AS 所属大类
       FROM product pr
       JOIN up     u  ON pr.category_id = u.id
       JOIN category rc ON rc.id = u.root
       JOIN brand  b  ON pr.brand_id = b.id
       ORDER BY pr.name
     """))

show("3. Rule R2:买过商品 → 推导买过其品牌",
     conn.execute("""
       SELECT c.name AS 用户, b.name AS 买过的品牌
       FROM (SELECT DISTINCT pur.customer_id AS uid, pr.brand_id AS bid
             FROM purchase pur JOIN product pr ON pr.id = pur.product_id) d
       JOIN customer c ON c.id = d.uid
       JOIN brand    b ON b.id = d.bid
       ORDER BY c.name
     """))

print("== 4. Constraint:价格必须 >= 0 ==")
try:
    conn.execute("INSERT INTO product VALUES (0, '假货', -1, 0, 1, 2)")
    print("  !!! 约束未生效")
except sqlite3.IntegrityError as e:
    print(f"  拦截违规插入: {e}")