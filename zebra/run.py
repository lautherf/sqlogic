import sqlite3
from pathlib import Path

sql = Path(__file__).with_name("zebra.sql").read_text(encoding="utf-8").rstrip().rstrip(";")
conn = sqlite3.connect(":memory:")
rows = conn.execute(sql).fetchall()
conn.close()

print("Zebra(爱因斯坦)五户迷题")
print("15 条线索:")
CLUES = [
    "1) 英国人住红屋",
    "2) 西班牙人养狗",
    "3) 绿屋喝咖啡",
    "4) 乌克兰人喝茶",
    "5) 绿屋紧挨象牙屋右侧",
    "6) Old Gold 牌者养蜗牛",
    "7) Kools 牌者在黄屋",
    "8) 中间(3号)屋喝奶",
    "9) 挪威人住 1 号屋",
    "10) Chesterfield 者挨着养狐狸者",
    "11) Kools 者挨着养马者",
    "12) Lucky Strike 者喝橙汁",
    "13) 日本人抽 Parliament",
    "14) 挪威人挨着蓝屋",
]
print(f"  {len(CLUES)} 条线索 → 解的数量会唯一")
print()

VAL = {
    "color": {"G": "绿", "I": "象牙", "R": "红", "B": "蓝", "Y": "黄"},
    "nat": {"E": "英国人", "S": "西班牙人", "N": "挪威人", "U": "乌克兰人", "J": "日本人"},
    "drink": {"C": "咖啡", "T": "茶", "M": "牛奶", "O": "橙汁", "W": "水"},
    "smoke": {"K": "Kools", "C": "Chester", "O": "OldGold", "L": "Lucky", "P": "Parli."},
    "pet": {"D": "狗", "S": "蜗牛", "F": "狐狸", "H": "马", "Z": "斑马"},
}

print(f"解的数量: {len(rows)}")
for color, nat, drink, smoke, pet in rows:
    print()
    for house in range(1, 6):
        c, n, d, m, p = color[house-1], nat[house-1], drink[house-1], smoke[house-1], pet[house-1]
        print(f"  {house}号: {VAL['color'][c]:<4} {VAL['nat'][n]:<5} "
              f"{VAL['drink'][d]:<3} {VAL['smoke'][m]:<8} {VAL['pet'][p]}")
    who = {s: (i+1) for i, s in enumerate(nat)}
    h_water = drink.index("W") + 1
    h_zebra = pet.index("Z") + 1
    print()
    print(f"  喝水的住在 {h_water} 号 → {VAL['nat'][nat[h_water-1]]}")
    print(f"  养斑马的住在 {h_zebra} 号 → {VAL['nat'][nat[h_zebra-1]]}")