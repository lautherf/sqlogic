-- ============ TBox 公理 ============
-- subClass: 分类层级
INSERT INTO axiom VALUES ('subClass', '旗舰机', '手机');
INSERT INTO axiom VALUES ('subClass', '手机', '数码');
INSERT INTO axiom VALUES ('subClass', '数码', '商品');
INSERT INTO axiom VALUES ('subClass', '家电', '商品');

-- subProperty: 属性层级
INSERT INTO axiom VALUES ('subProperty', '购买', '拥有');     -- 买即拥有
INSERT INTO axiom VALUES ('subProperty', '拥有', '处置');     -- 拥有即可处置

-- domain / range
INSERT INTO axiom VALUES ('domain', '购买', '用户');          -- 购买者必须是用户
INSERT INTO axiom VALUES ('range',  '购买', '商品');          -- 购买对象必须是商品
INSERT INTO axiom VALUES ('domain', '供货', '供应商');

-- inverse
INSERT INTO axiom VALUES ('inverse', '供货', '被供应');

-- transitive / symmetric
INSERT INTO axiom VALUES ('transitive', 'partOf', '');           -- 位于某部件中,可传递
INSERT INTO axiom VALUES ('symmetric',  '同盒', '');

-- disjoint:一致性约束
INSERT INTO axiom VALUES ('disjoint', '数码', '家电');       -- 商品不同时是数码和家电

-- ============ ABox 事实(种子) ============
INSERT INTO fact VALUES ('张三', 'type', '用户',     'seed');
INSERT INTO fact VALUES ('iPhone17', 'type', '旗舰机','seed');
INSERT INTO fact VALUES ('小米14',  'type', '手机',   'seed');
INSERT INTO fact VALUES ('冰箱',    'type', '家电',   'seed');

-- 购买行为
INSERT INTO fact VALUES ('张三', '购买', 'iPhone17', 'seed');
INSERT INTO fact VALUES ('李四', '购买', '小米14',   'seed');

-- 物理构成:可传递的 partOf
INSERT INTO fact VALUES ('A16芯片', 'partOf', 'iPhone17', 'seed');
INSERT INTO fact VALUES ('镜头模组', 'partOf', 'iPhone17', 'seed');
INSERT INTO fact VALUES ('iPhone17', 'partOf', '数码区',   'seed');

-- 对称关系
INSERT INTO fact VALUES ('张三', '同盒', '李四',     'seed');

-- 供应链
INSERT INTO fact VALUES ('富士康', '供货', 'iPhone17', 'seed');

-- 故意制造一个冲突:同一对象同时是数码与家电 → 触发 disjoint
INSERT INTO fact VALUES ('样机', 'type', '数码', 'seed');
INSERT INTO fact VALUES ('样机', 'type', '家电', 'seed');

-- ============ 用户自定义复合规则 ============
-- r1 ∘ r2 ⊑ out
-- J1: 购买∘partOf ⊑ 购买  (买了手机,则手机内的部件也算购买到的)
INSERT INTO rule VALUES ('购买', 'partOf', '购买', 'J1');
-- J2: 供货∘partOf ⊑ 供货 (供应商供货给整机,则其部件也算该供应商的货物)
INSERT INTO rule VALUES ('供货', 'partOf', '供货', 'J2');