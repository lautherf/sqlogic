-- EL 组合闭包:供应链商品本体推理
--
-- ABox:partOf / isA / owns / buys 四种关系实例
-- TBox:规则的唯一形式都是"关系复合",所以规则本身也物化为一张表：
--       rule(r1, r2, out, jpat)  表示  r1 ∘ r2 ⊑ out
--       jpat     决定复合的接头方式:
--                 J1  a.o = b.s  → 结论 (a.s, out, b.o)   [同类传递/归类]
--                 J2  a.o = b.o  → 结论 (a.s, out, b.s)   [前缀关系吸收后缀]
--
-- 运行:run.py 用 bottom-up 半朴素求值迭代到不动点。
-- (SQLite 递归 CTE 限制:递归表不可自连接,多条复合规则需在外部迭代。)

-- ---------- ABox ----------
CREATE TABLE cl(s TEXT, p TEXT, o TEXT);
INSERT INTO cl VALUES
  ('活塞',     'partOf', '发动机'),
  ('发动机',   'partOf', '汽车'),
  ('轮胎',     'partOf', '汽车'),
  ('豪华发动机','isA',   '发动机'),
  ('发动机',   'isA',   '动力系统'),
  ('汽车',     'isA',   '车'),
  ('自行车',   'isA',   '车'),
  ('车',       'isA',   '交通工具'),
  ('李四',     'owns',  '汽车'),
  ('王五',     'owns',  '自行车'),
  ('李四',     'buys',  '汽车');

-- ---------- TBox(规则=数据)----------
CREATE TABLE rule(r1 TEXT, r2 TEXT, out TEXT, jpat TEXT);
INSERT INTO rule VALUES
  ('partOf','partOf','partOf','J1'),   -- R1 partOf 传递
  ('isA',   'isA',   'isA',   'J1'),   -- R2 isA 传递
  ('partOf','isA',   'partOf','J1'),   -- R3 活塞partOf发动机, 发动机isA动力系统 → 活塞partOf动力系统
  ('owns',  'partOf','owns',  'J2'),   -- R4 拥有汽车 → 拥有发动机/活塞/轮胎
  ('buys',  'partOf','buys',  'J2'),   -- R5 买下汽车 → 买下其零件
  ('owns',  'isA',   'owns',  'J1'),   -- R6 拥有汽车 → 拥有"车"品类
  ('isA',   'partOf','partOf','J1');   -- R7 豪华发动机(isA)也是汽车零件