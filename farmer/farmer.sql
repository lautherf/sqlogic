-- 农民、狼、羊、菜过河
--
-- 状态 = 4 位二进制 s = (F,W,G,C),0=左岸 1=右岸,起点 0000 终点 1111。
--   (s>>3)&1=F, (s>>2)&1=W, (s>>1)&1=G, s&1=C
-- 危险:农民不在场时,狼羊同岸 或 羊菜同岸。
-- BFS:递归 CTE 逐层展开,天然按步数层进;seen 位掩码防环。

WITH RECURSIVE
  states(s) AS (SELECT 0 UNION ALL SELECT s+1 FROM states WHERE s < 15),
  safe(f, w, g, c, s) AS (
    SELECT (s>>3)&1, (s>>2)&1, (s>>1)&1, s&1, s
    FROM states
    WHERE NOT ((s>>2)&1 = (s>>1)&1 AND (s>>1)&1 <> (s>>3)&1)  -- 狼羊同岸且农民在对岸
      AND NOT ((s>>1)&1 = s&1 AND s&1 <> (s>>3)&1)            -- 羊菜同岸且农民在对岸
  ),
  path(f, w, g, c, s, seen, route) AS (
    SELECT 0,0,0,0, 0, 1, '0000 '
    UNION ALL
    SELECT n.f, n.w, n.g, n.c, n.s,
           path.seen | (1 << n.s),
           path.route || printf('%d%d%d%d ', n.f,n.w,n.g,n.c)
    FROM path, safe n
    WHERE path.s <> 15
      AND (path.seen & (1 << n.s)) = 0
      AND (
           -- 农民独自
           (n.f = 1-path.f AND n.w = path.w AND n.g = path.g AND n.c = path.c)
        OR (-- 带狼(农民须与狼同岸)
           n.f = 1-path.f AND n.w = 1-path.w AND n.g = path.g AND n.c = path.c
           AND path.w = path.f)
        OR (-- 带羊
           n.f = 1-path.f AND n.w = path.w AND n.g = 1-path.g AND n.c = path.c
           AND path.g = path.f)
        OR (-- 带菜
           n.f = 1-path.f AND n.w = path.w AND n.g = path.g AND n.c = 1-path.c
           AND path.c = path.f)
       )
  )
SELECT route, length(route) - length(replace(route,' ','')) - 1 AS moves
FROM path WHERE s = 15
ORDER BY moves;