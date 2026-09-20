-- Chase / 本体物化:处理存在量词 A ⊑ ∃R.B
--
-- TBox 规则(RDFS/EL 之上的关键一步):
--   R1  course ⊑ ∃instructedBy.instructor  每个课程至少有一个教师
--   R2  x instructedBy y  ⟹  y teaches x     逆关系推导
--
-- ABox:c1 已有教师 t1;c2、c3 没有 → R1 要为它们【生成新个体】。
-- 这是 OWL 与纯 RDFS 的本质差别:不是查询既有数据,而是产生不存在的个体。

WITH RECURSIVE
  -- ---------- ABox(种子事实)----------
  fact(sub, pred, obj) AS (
    VALUES
      ('c1', 'rdf:type',     'course'),
      ('c2', 'rdf:type',     'course'),
      ('c3', 'rdf:type',     'course'),
      ('t1', 'rdf:type',     'instructor'),
      ('c1', 'instructedBy', 't1')
  ),
  -- 缺教师的课程 → 存在规则的一次触发判定
  -- (静态判定即可:物化一轮后它们全都有了教师,闭包收敛)
  need(id) AS (
    SELECT sub FROM fact WHERE pred='rdf:type' AND obj='course'
    EXCEPT
    SELECT sub FROM fact WHERE pred='instructedBy'
  ),
  -- ---------- 物化闭包 ----------
  chase(sub, pred, obj) AS (
    SELECT sub, pred, obj FROM fact
    UNION ALL
    -- R1:引入新个体 f_<课程>,并断言它是 instructor
    SELECT id,          'instructedBy', 'f_'||id FROM need
    UNION ALL
    SELECT 'f_'||id,    'rdf:type',     'instructor' FROM need
    UNION ALL
    -- R2:逆关系
    SELECT obj, 'teaches', sub FROM chase WHERE pred='instructedBy'
  )
SELECT row_number() OVER (ORDER BY sub, pred, obj) AS no,
       sub, pred, obj
FROM chase;