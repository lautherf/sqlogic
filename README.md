# sql-logic

用 **SQL 递归 CTE + 集合式推理**做逻辑编程(SQLite 可终止的 Datalog 子集)。

一句话哲学:**表 = 谓词,行 = 事实,递归 CTE = 规则,WHERE = 剪枝/约束。**

## 五个演示

| 模块 | 问题 | 演示点 |
|---|---|---|
| `queens/` | N 皇后 | 回溯搜索:集合式穷举 × bitmask 剪枝 |
| `farmer/` | 农民过河 | BFS 状态搜索:16 状态 × 危险过滤 × 防环 |
| `zebra/` | Einstein 五户迷题 | 120⁵ 组合空间 × 15 线索分层剪枝,唯一解 |
| `ontology/` | 电商本体 | 知识表示:关系为枢纽,规则推导新事实 |
| `elclosure/` | EL 组合闭包 | 多规则复合(partOf∘isA 等)bottom-up 迭代到不动点 |
| `chase/` | A⊑∃R.B 物化 | 走出 RDFS:存在量词生成全新个体 |

## 运行

```bash
python3 queens/run.py            # 默认 8 皇后
python3 queens/run.py 10         # 任意 N
python3 farmer/run.py            # 农民过河:7 步最短解
python3 zebra/run.py             # Einstein 五户迷题:唯一解
python3 ontology/run.py          # 六要素 + 两条推理规则 + 约束拦截
python3 elclosure/run.py         # EL 组合闭包:5 条规则复合,4 轮迭代收敛
python3 chase/run.py             # 存在量词物化:生成全新个体 + 逆关系迭代
```

## 映射:本体的六要素

```
Class      → 表             brand / category / product / customer
Property   → 列(带类型)      price / stock / name / qty / at
Relation   → 关联表(=枢纽)   purchase:谁(direction=domain)→买→什么(range)
Instance   → 行              李四 / iPhone 17 / Apple
Constraint → CHECK + FK      price >= 0, stock >= 0, qty > 0
Rule       → 递归 CTE/派生   分类→大类;买过商品→买过其品牌
```

与 Prolog 的对照:

| Prolog | 本实现 |
|---|---|
| fact / goal | 表 / 查询 |
| rule(子句) | 递归 CTE(`UNION ALL` 分支) |
| findall / setof | `SELECT ... WHERE` |
| negation as failure | `NOT EXISTS` / 反联接 |
| 回溯 | 集合式穷举(无顺序语义,故无 `cut`) |
| 合一 + 逻辑变量 | 无(只有等值匹配)——可终止子集,换完全性 |

## 边界

- 只覆盖**可终止**的逻辑:无函数符号、无 `call/N`、无负位移
- `1 <<`, `json_insert` 为 SQLite 方言,要求 ≥ 3.38
- 剪枝位运算用 N 做平移偏移,保证位移恒非负