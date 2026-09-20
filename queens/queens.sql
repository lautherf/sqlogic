-- N 皇后:递归 CTE + 位运算剪枝
-- 三个 bitmask:列占用 cols / 主对角线 d1 / 副对角线 d2
-- 用法:占位符 {N} 由 run.py 注入,也可直接改本文件底部的 8
WITH RECURSIVE
  num(c) AS (
    SELECT 1 UNION ALL SELECT c + 1 FROM num WHERE c < {N}
  ),
  q(rown, cols, d1, d2, path) AS (
    SELECT 0, 0, 0, 0, json('[]')
    UNION ALL
    SELECT rown + 1,
           cols | (1 << c),
           d1   | (1 << (rown - c + {N})),
           d2   | (1 << (rown + c)),
           json_insert(path, '$[#]', c)
    FROM q, num
    WHERE rown < {N}
      AND (cols & (1 << c)) = 0
      AND (d1   & (1 << (rown - c + {N}))) = 0
      AND (d2   & (1 << (rown + c))) = 0
  )
SELECT row_number() OVER () AS no, path AS solution
FROM q
WHERE rown = {N};