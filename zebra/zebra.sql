-- Zebra(爱因斯坦)五户迷题
--
-- 5 栋房子从左到右 1..5,每栋 5 个属性(颜色/国籍/饮料/烟/宠物),
-- 每个类别恰好一栋一值。15 条线索见 run.py。求解:谁喝水?谁养斑马?
--
-- 方法:
--   1. 每个类别 5!=120 种排列,编码为 5 字符字符串,位置即房子号
--   2. 递归 CTE 按类别分层拼接:颜色→国籍→饮料→烟→宠物,
--      每层只用"当前类型已齐"的线索剪枝,组合爆炸逐层砍掉
--
-- 线索依赖层级:
--   L1 颜色:绿在象牙右邻
--   L2 国籍:+英国人住红屋、挪威人住1号、挪威挨着蓝屋
--   L3 饮料:+绿屋喝咖啡、乌克兰人喝茶、中间屋喝奶
--   L4 烟:+黄屋抽Kools、日本人抽Parliament、Lucky抽橙汁
--   L5 宠物:+西班牙人养狗、OldGold养蜗牛、Chesterfield挨狐狸、Kools挨马

WITH RECURSIVE
  -- 每类别 5 值编码成字母,房子 = 字符位置(1..5)
  letter(cat, ch, bit) AS (
    VALUES
      ('color','G',1),('color','I',2),('color','R',4),('color','B',8),('color','Y',16),
      ('nat',  'E',1),('nat',  'S',2),('nat',  'N',4),('nat',  'U',8),('nat',  'J',16),
      ('drink','C',1),('drink','T',2),('drink','M',4),('drink','O',8),('drink','W',16),
      ('smoke','K',1),('smoke','C',2),('smoke','O',4),('smoke','L',8),('smoke','P',16),
      ('pet',  'D',1),('pet',  'S',2),('pet',  'F',4),('pet',  'H',8),('pet',  'Z',16)
  ),
  -- 通用排列生成器(每类别 120 种)
  per(cat, done, used, s) AS (
    SELECT DISTINCT cat, 0, 0, '' FROM letter
    UNION ALL
    SELECT l.cat, per.done+1, per.used | l.bit, per.s || l.ch
    FROM per JOIN letter l ON l.cat = per.cat AND (per.used & l.bit) = 0
  ),
  perm(cat, s) AS (SELECT cat, s FROM per WHERE done = 5),
  -- 分层求解:每层与对应候选排列拼接 + 当层线索剪枝
  sol(color, nat, drink, smoke, pet, lvl) AS (
    -- L1 颜色
    SELECT c.s, '', '', '', '', 1 FROM perm c
    WHERE c.cat = 'color'
      AND instr(c.s, 'G') = instr(c.s, 'I') + 1      -- 绿紧挨象牙右侧
    UNION ALL
    -- L2 国籍
    SELECT sol.color, n.s, sol.drink, sol.smoke, sol.pet, 2
    FROM sol JOIN perm n ON n.cat = 'nat'
    WHERE sol.lvl = 1
      AND instr(n.s, 'E') = instr(sol.color, 'R')     -- 英国人住红屋
      AND instr(n.s, 'N') = 1                         -- 挪威人住1号
      AND abs(instr(n.s, 'N') - instr(sol.color, 'B')) = 1  -- 挪威挨着蓝屋
    UNION ALL
    -- L3 饮料
    SELECT sol.color, sol.nat, d.s, sol.smoke, sol.pet, 3
    FROM sol JOIN perm d ON d.cat = 'drink'
    WHERE sol.lvl = 2
      AND instr(d.s, 'C') = instr(sol.color, 'G')     -- 绿屋喝咖啡
      AND instr(sol.nat, 'U') = instr(d.s, 'T')       -- 乌克兰人喝茶
      AND instr(d.s, 'M') = 3                         -- 中间屋喝奶
    UNION ALL
    -- L4 烟
    SELECT sol.color, sol.nat, sol.drink, m.s, sol.pet, 4
    FROM sol JOIN perm m ON m.cat = 'smoke'
    WHERE sol.lvl = 3
      AND instr(m.s, 'K') = instr(sol.color, 'Y')     -- 黄屋抽Kools
      AND instr(sol.nat, 'J') = instr(m.s, 'P')       -- 日本人抽Parliament
      AND instr(m.s, 'L') = instr(sol.drink, 'O')     -- Lucky抽橙汁
    UNION ALL
    -- L5 宠物
    SELECT sol.color, sol.nat, sol.drink, sol.smoke, p.s, 5
    FROM sol JOIN perm p ON p.cat = 'pet'
    WHERE sol.lvl = 4
      AND instr(sol.nat, 'S') = instr(p.s, 'D')       -- 西班牙人养狗
      AND instr(sol.smoke, 'O') = instr(p.s, 'S')     -- OldGold养蜗牛
      AND abs(instr(sol.smoke, 'C') - instr(p.s, 'F')) = 1  -- Chesterfield挨狐狸
      AND abs(instr(sol.smoke, 'K') - instr(p.s, 'H')) = 1  -- Kools挨着马
  )
SELECT color, nat, drink, smoke, pet
FROM sol WHERE lvl = 5;