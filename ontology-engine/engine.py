# sqlogic 本体论引擎
#
# 三层数据存储:
#   fact(s,p,o,src)    ABox/物化闭包 —— s,p,o 分别为主语/谓词/宾语三元组
#   axiom(a,x,y)       TBox 公理     —— a 是公理类型, x,y 是两个参数
#   rule(r1,r2,out,jp) 用户自定义复合规则 —— r1∘r2 ⊑ out
#
# 推理层(内建原语,owl2rl 风格):
#   R1  subClass 传递        subClass(x,y) ∧ subClass(y,z) → subClass(x,z)
#   R2  type 提升            type(x,y) ∧ subClass(y,z)     → type(x,z)
#   R3  subProperty 传递     同理
#   R4  subProperty 应用     x p y ∧ subProperty(p,q)      → x q y
#   R5  domain              x p y ∧ domain(p,C)           → type(x,C)
#   R6  range               x p y ∧ range(p,C)            → type(y,C)
#   R7  inverse             x p y ∧ inverse(p,q)          → y q x
#   R8  transitive          x p y ∧ transitive(p) ∧ y p z  → x p z
#   R9  symmetric           x p y ∧ symmetric(p)           → y p x
#   R10 自定义复合           (见 rule 表,J1/J2 两种接法)
#
# 一致性:disjoint(A,B) 且 type(x,A) ∧ type(x,B) → 冲突报告

import sqlite3
import sys
from pathlib import Path


class OntologyEngine:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript("""
          CREATE TABLE fact(s TEXT, p TEXT, o TEXT, src TEXT);
          CREATE TABLE axiom(a TEXT, x TEXT, y TEXT);
          CREATE TABLE rule(r1 TEXT, r2 TEXT, out TEXT, jp TEXT);
          CREATE INDEX IF NOT EXISTS ix_fact ON fact(s,p,o);
        """)
        self.rounds = 0
        self.new_count = 0

    def load(self, module):
        self.conn.executescript(Path(module).read_text(encoding="utf-8"))

    def facts(self):
        return self.conn.execute("SELECT s,p,o FROM fact").fetchall()

    # ---- 一条推理原语:从闭包推出候选新事实 ----
    def _add(self, rows):
        if not rows:
            return 0
        cur = self.conn.execute("SELECT s,p,o FROM fact")
        have = {(r[0], r[1], r[2]) for r in cur}
        fresh = [(s, p, o, src) for s, p, o, src in rows if (s, p, o) not in have]
        self.conn.executemany("INSERT INTO fact VALUES (?,?,?,?)", fresh)
        self.new_count += len(fresh)
        return len(fresh)

    def rules_apply(self):
        n = 0

        # R1 subClass 传递
        n += self._add(
            (x, "subClass", z, "R1")
            for x, y in
            self.conn.execute("SELECT x,y FROM axiom WHERE a='subClass'")
            for z, in
            self.conn.execute("SELECT y FROM axiom WHERE a='subClass' AND x=?", (y,))
        )

        # R2 type 提升
        n += self._add(
            (s, "type", z, "R2")
            for s, p, y in self.facts() if p == "type"
            for z, in
            self.conn.execute("SELECT y FROM axiom WHERE a='subClass' AND x=?", (y,))
        )

        # R3 subProperty 传递
        n += self._add(
            (x, "subProperty", z, "R3")
            for x, y in
            self.conn.execute("SELECT x,y FROM axiom WHERE a='subProperty'")
            for z, in
            self.conn.execute(
                "SELECT y FROM axiom WHERE a='subProperty' AND x=?", (y,))
        )

        # R4 subProperty 应用
        n += self._add(
            (s, q, o, "R4")
            for s, p, o in self.facts()
            for q, in
            self.conn.execute(
                "SELECT y FROM axiom WHERE a='subProperty' AND x=?", (p,))
            if q != p
        )

        # R5 domain
        n += self._add(
            (s, "type", C, "R5")
            for s, p, o in self.facts()
            for C, in
            self.conn.execute("SELECT y FROM axiom WHERE a='domain' AND x=?", (p,))
        )

        # R6 range
        n += self._add(
            (o, "type", C, "R6")
            for s, p, o in self.facts()
            for C, in
            self.conn.execute("SELECT y FROM axiom WHERE a='range' AND x=?", (p,))
        )

        # R7 inverse
        n += self._add(
            (o, q, s, "R7")
            for s, p, o in self.facts()
            for q, in
            self.conn.execute("SELECT y FROM axiom WHERE a='inverse' AND x=?", (p,))
        )

        # R8 transitive
        tlist = [y for _, y, _ in
                 self.conn.execute("SELECT a,x,y FROM axiom WHERE a='transitive'")]
        for t in tlist:
            edges = [(s, o) for s, p, o in self.facts() if p == t]
            n += self._add(
                (a, t, c, "R8")
                for a, b in edges for b2, c in edges if b == b2
            )

        # R9 symmetric
        slist = [y for _, y, _ in
                 self.conn.execute("SELECT a,x,y FROM axiom WHERE a='symmetric'")]
        for m in slist:
            n += self._add(
                (o, m, s, "R9")
                for s, p, o in self.facts() if p == m
            )

        # R10 自定义复合规则(rule 表)
        for r1, r2, out, jp in self.conn.execute("SELECT * FROM rule"):
            if jp == "J1":      # a.o = b.s → 结论 (a.s, out, b.o)
                n += self._add(
                    (x, out, z, f"R10[{r1}∘{r2}]")
                    for x, p1, y in self.facts() if p1 == r1
                    for y2, p2, z in self.facts() if p2 == r2 and y2 == y
                )
            else:               # J2: a.o = b.o → 结论 (a.s, out, b.s)
                n += self._add(
                    (x, out, z, f"R10[{r1}∘{r2}]")
                    for x, p1, y in self.facts() if p1 == r1
                    for z, p2, y2 in self.facts() if p2 == r2 and y2 == y
                )
        return n

    def materialize(self, max_rounds=100):
        """不动点迭代:直到某一轮没有任何新事实"""
        while True:
            got = self.rules_apply()
            self.rounds += 1
            if got == 0 or self.rounds >= max_rounds:
                break
        return self.rounds

    def inconsistency(self):
        """disjoint 检测:type(x,A) ∧ type(x,B)"""
        bad = []
        for _, A, B in self.conn.execute("SELECT a,x,y FROM axiom WHERE a='disjoint'"):
            for s, p, C in self.facts():
                if p == "type" and C == A:
                    if (s, "type", B) in {(r[0], r[1], r[2])
                                          for r in self.facts()}:
                        bad.append((s, A, B))
        return bad

    def report(self, head="fact", verb="⊢"):
        """按谓词分组输出推理结论"""
        rows = self.conn.execute(
            "SELECT p, s, o, src FROM fact ORDER BY p, s, o").fetchall()
        groups = {}
        for s, p, o, src in rows:
            groups.setdefault(p, []).append((s, o, src))
        print(f"== 物化闭包({head}) ==")
        for p, items in groups.items():
            print(f"  [{p}] {len(items)} 条")
            for s, o, src in items:
                print(f"    {s} {verb} {o}   ({src})")
        print()

    def seed_stats(self):
        return self.conn.execute("SELECT COUNT(*) FROM fact").fetchone()[0]


def main():
    module = sys.argv[1] if len(sys.argv) > 1 else "demo.sql"
    eng = OntologyEngine()
    seed = eng.seed_stats()
    eng.load(module)
    seed = eng.seed_stats()

    print(f"加载 {module}: ABox 种子事实 {seed} 条")
    print()

    rounds = eng.materialize()
    print(f"不动点迭代 {rounds} 轮收敛,共新增 {eng.new_count} 条事实")
    print()

    eng.report()
    bad = eng.inconsistency()
    if bad:
        print("== 一致性检查 ==")
        for s, A, B in bad:
            print(f"  ✗ 冲突:{s} 同时是 {A} 和 {B}(disjoint 违反)")
    else:
        print("== 一致性检查 ==")
        print("  ✓ 无冲突")


if __name__ == "__main__":
    main()