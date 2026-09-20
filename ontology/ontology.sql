-- 电商本体:关系为枢纽,六要素显式建模
--
--   Class      → 表              (brand / category / product / customer)
--   Property   → 列(带类型)       (price / stock / name / qty / at)
--   Relation   → 关联表(最重要)    (purchase:方向=谁→买→什么,自带属性 qty/at)
--   Instance   → 行               (李四 / iPhone 17 / Apple)
--   Constraint → CHECK + 引用完整性
--   Rule       → 递归 CTE / 派生  (分类层级、买过商品→买过其品牌)

-- ---------- TBox: Class + Property + Relation ----------
CREATE TABLE brand(id INTEGER PRIMARY KEY, name TEXT NOT NULL);

-- 自递归:category 既是 Class 又挂着父级关系 parent_id
CREATE TABLE category(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  parent_id INTEGER REFERENCES category(id)
);

CREATE TABLE product(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price REAL    CHECK (price >= 0),
  stock INTEGER CHECK (stock >= 0),
  brand_id  INTEGER NOT NULL REFERENCES brand(id),
  category_id INTEGER NOT NULL REFERENCES category(id)
);

CREATE TABLE customer(id INTEGER PRIMARY KEY, name TEXT NOT NULL);

-- 关系:谁(domain) —购买→ 什么(range),属性:数量+时间
CREATE TABLE purchase(
  customer_id INTEGER NOT NULL REFERENCES customer(id),
  product_id  INTEGER NOT NULL REFERENCES product(id),
  qty INTEGER NOT NULL CHECK (qty > 0),
  at TEXT NOT NULL,
  PRIMARY KEY (customer_id, product_id)
);

-- ---------- ABox: Instance ----------
INSERT INTO brand VALUES (1, 'Apple'), (2, '小米');

INSERT INTO category VALUES
  (1, '数码', NULL),
  (2, '手机', 1),
  (3, 'iPhone', 2),
  (4, '小米手机', 2),
  (5, '穿戴设备', 1);

INSERT INTO product VALUES
  (1, 'iPhone 17',   6999.0, 100, 1, 3),
  (2, '小米14',      3999.0,  50, 2, 4),
  (3, 'Apple Watch', 2999.0,  20, 1, 5);

INSERT INTO customer VALUES (1, '李四'), (2, '王五');

INSERT INTO purchase VALUES
  (1, 1, 1, '2026-09-20'),
  (1, 2, 2, '2026-09-21'),
  (2, 3, 1, '2026-09-01');