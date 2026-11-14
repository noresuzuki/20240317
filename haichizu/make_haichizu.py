# -*- coding: utf-8 -*-
"""
東町運動公園体育館建設工事 配置図（A-005）のトレース図を生成する。

原図の写真（1279x960px）上で読み取った座標(px)を、通り芯 X1-X16 / Y16-Y1 の
4交点を基準にした射影変換で実寸(mm)へ変換して DXF を作る。
  X1-X16 = 115,000mm（原図の寸法表記より）
  Y16-Y1 =  92,600mm（原図の寸法表記より）
写真からの読み取りのため、形状・位置は概略（誤差 数m程度）。
"""
import math
import numpy as np
import ezdxf
from ezdxf.enums import TextEntityAlignment

# ---------------------------------------------------------------- 座標変換
SRC = np.array([[440, 281], [710, 278], [440, 505], [712, 503]], float)  # 写真px
DST = np.array([[0, 92600], [115000, 92600], [0, 0], [115000, 0]], float)  # 実寸mm


def homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, vt = np.linalg.svd(np.array(A))
    return vt[-1].reshape(3, 3) / vt[-1][-1]


H = homography(SRC, DST)


def T(p):
    x, y = p
    u, v, w = H @ np.array([x, y, 1.0])
    return (u / w, v / w)


def TT(pts):
    return [T(p) for p in pts]


SCALE = 600            # 1/600（A1）
def pm(mm):            # 用紙上の mm → モデル mm
    return mm * SCALE


# ---------------------------------------------------------------- DXF 準備
doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.MM
doc.header["$LTSCALE"] = 600
doc.styles.new("JP", dxfattribs={"font": "msgothic.ttc"})

LAYERS = {
    "図枠":       (7, "CONTINUOUS"),
    "通り芯":     (1, "CENTER"),
    "敷地境界":   (1, "DASHDOT"),
    "隣地・道路境界": (6, "DASHED"),
    "道路":       (8, "CONTINUOUS"),
    "建物":       (7, "CONTINUOUS"),
    "建物ハッチ": (9, "CONTINUOUS"),
    "屋根":       (8, "CONTINUOUS"),
    "駐車場":     (5, "CONTINUOUS"),
    "外構":       (3, "CONTINUOUS"),
    "等高線":     (8, "DASHED"),
    "下水管":     (4, "DASHDOT"),
    "寸法":       (2, "CONTINUOUS"),
    "文字":       (7, "CONTINUOUS"),
}
for name, (color, lt) in LAYERS.items():
    doc.layers.add(name, color=color, linetype=lt)

msp = doc.modelspace()


def pl(pts, layer, closed=False, px=True, lw=None):
    pts = TT(pts) if px else pts
    a = {"layer": layer}
    if lw:
        a["lineweight"] = lw
    return msp.add_lwpolyline(pts, close=closed, dxfattribs=a)


def text(s, p, h_paper=2.5, layer="文字", px=True, rot=0.0,
         align=TextEntityAlignment.MIDDLE_CENTER):
    q = T(p) if px else p
    t = msp.add_text(s, height=pm(h_paper),
                     dxfattribs={"layer": layer, "style": "JP", "rotation": rot})
    t.set_placement(q, align=align)
    return t


def hatch(pts, layer="建物ハッチ", color=9, px=True):
    h = msp.add_hatch(color=color, dxfattribs={"layer": layer})
    h.paths.add_polyline_path(TT(pts) if px else pts, is_closed=True)
    h.set_solid_fill(color=color)
    h.transparency = 0.6
    return h


def circle(c, r_paper, layer, px=True):
    return msp.add_circle(T(c) if px else c, pm(r_paper), dxfattribs={"layer": layer})


def offset_line(p0, p1, d):
    """モデル座標の線分 p0-p1 を左側に d だけ平行移動"""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    nx, ny = -dy / L, dx / L
    return (p0[0] + nx * d, p0[1] + ny * d), (p1[0] + nx * d, p1[1] + ny * d)


def stall_row(a_px, b_px, depth=5000, pitch=2500, side=1, layer="駐車場"):
    """a→b に沿った駐車ます列（side=+1 で進行方向左側に奥行き）"""
    a, b = T(a_px), T(b_px)
    a2, b2 = offset_line(a, b, side * depth)
    msp.add_lwpolyline([a, b, b2, a2], close=False, dxfattribs={"layer": layer})
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    n = int(L // pitch)
    for i in range(1, n + 1):
        t = i * pitch / L
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        q = (a2[0] + (b2[0] - a2[0]) * t, a2[1] + (b2[1] - a2[1]) * t)
        msp.add_line(p, q, dxfattribs={"layer": layer})
    return n


def double_row(a_px, b_px, **kw):
    """中央分離帯をはさんだ 2 列の駐車ます"""
    n = stall_row(a_px, b_px, side=+1, **kw)
    n += stall_row(a_px, b_px, side=-1, **kw)
    return n


# ================================================================ 通り芯
for name, x, y0, y1 in [("X1", 440, 92, 512), ("X16", 711, 90, 510)]:
    pl([(x, y0 + 10), (x, y1)], "通り芯")
    circle((x, y0), 4.0, "通り芯")
    text(name, (x, y0), 3.0, "通り芯")
for name, y, x0, x1 in [("Y16", 280, 207, 936), ("Y1", 504, 207, 936)]:
    pl([(x0 + 10, y), (x1 - 10, y)], "通り芯")
    circle((x0, y), 4.0, "通り芯")
    circle((x1, y), 4.0, "通り芯")
    text(name, (x0, y), 3.0, "通り芯")
    text(name, (x1, y), 3.0, "通り芯")

# 寸法（主要寸法のみ）
d = msp.add_linear_dim(base=(0, T((440, 88))[1]), p1=(0, 92600), p2=(115000, 92600),
                       text="115,000", dimstyle="EZDXF", override={"dimlfac": 1, "dimtxt": pm(2.5), "dimasz": pm(2.0),
                                                   "dimexe": pm(1), "dimexo": pm(1),
                                                   "dimtxsty": "JP"},
                       dxfattribs={"layer": "寸法"})
d.render()
d = msp.add_linear_dim(base=(T((918, 400))[0], 0), p1=(115000, 0), p2=(115000, 92600),
                       angle=90, text="92,600", dimstyle="EZDXF",
                       override={"dimlfac": 1, "dimtxt": pm(2.5), "dimasz": pm(2.0), "dimexe": pm(1),
                                 "dimexo": pm(1), "dimtxsty": "JP"},
                       dxfattribs={"layer": "寸法"})
d.render()

# ================================================================ 敷地境界
site = [(517, 157), (545, 149), (600, 142), (730, 130), (862, 237), (828, 282),
        (838, 305), (842, 512), (800, 521), (611, 556), (604, 700), (590, 832),
        (494, 752), (400, 703), (300, 657), (230, 592), (165, 525), (152, 503),
        (175, 462), (250, 400), (330, 306), (372, 262), (412, 248), (517, 240)]
pl(site, "敷地境界", closed=True, lw=50)
text("敷地境界線", (690, 128), 2.0, rot=4)
text("隣地境界線", (420, 722), 2.0, rot=-25)
text("隣地境界線", (705, 532), 2.0, rot=10)
text("道路境界線", (450, 244), 2.0)
text("道路境界線", (262, 384), 2.0, rot=48)

# ================================================================ 道路（既存・新設）
# 北側市道
pl([(440, 112), (600, 106), (735, 98), (770, 70)], "道路")
pl([(440, 126), (600, 120), (725, 112), (760, 82)], "道路")
text("市道（上市1号幹線）", (600, 113), 2.0, rot=3)
# 西側道路
pl([(110, 455), (240, 360), (322, 290), (362, 252), (412, 233), (545, 229)], "道路")
pl([(128, 472), (250, 382), (330, 304)], "道路")
text("既存道路", (205, 400), 2.2, rot=38)
# 北東側の既存道路
pl([(860, 228), (958, 312)], "道路")
pl([(733, 128), (772, 96), (860, 160)], "道路")
# 新設アクセス道路
pl([(835, 330), (1085, 230)], "道路", lw=35)
pl([(843, 360), (1108, 254)], "道路", lw=35)
text("新設アクセス道路", (930, 312), 3.5, rot=21)
# 東側の既存道路（第1種住居地域側）
pl([(1060, 196), (1140, 410)], "道路")
pl([(1088, 192), (1168, 404)], "道路")
text("第1種住居地域", (1060, 250), 1.8, rot=21)

# ================================================================ 建物（今回申請建物）
# 体育館 外形（1F）
gym_out = [(440, 318), (545, 318), (545, 278), (734, 278), (734, 500), (440, 500)]
hatch(gym_out)
pl(gym_out, "建物", closed=True, lw=50)
# メインアリーナ屋根
roof = [(548, 288), (718, 288), (718, 498), (548, 498)]
pl(roof, "屋根", closed=True, lw=35)
for i in range(1, 42):                       # 屋根葺き方向の線
    y = 288 + i * 5
    if y < 498:
        pl([(548, y), (718, y)], "屋根")
pl([(548, 304), (620, 309), (718, 293)], "屋根", lw=35)   # 棟・けらば
pl([(548, 482), (620, 478), (718, 494)], "屋根", lw=35)
# サブアリーナ
sub = [(462, 386), (548, 386), (548, 494), (462, 494)]
pl(sub, "屋根", closed=True, lw=35)
pl([(467, 405), (545, 405), (545, 488), (467, 488)], "屋根", closed=True)
for i in range(1, 16):
    pl([(467 + i * 5, 405), (467 + i * 5, 488)], "屋根")
pl([(462, 395), (505, 386), (548, 395)], "屋根")
# 北西 低層部・階段
pl([(445, 345), (545, 345), (545, 383), (445, 383)], "建物", closed=True)
pl([(505, 362), (545, 362), (545, 378), (505, 378)], "外構", closed=True)
for i in range(1, 8):
    pl([(505 + i * 5, 362), (505 + i * 5, 378)], "外構")
# 東側 廊下
pl([(718, 290), (734, 290)], "建物")
# エントランス大屋根（ロータリー側の曲面庇）
pl([(548, 243), (546, 280), (530, 305), (500, 318), (440, 328)], "建物", lw=35)
pl([(560, 243), (558, 290), (540, 318), (505, 333), (445, 340)], "建物", lw=35)
hatch([(548, 243), (560, 243), (558, 290), (540, 318), (505, 333), (445, 340),
       (440, 328), (500, 318), (530, 305), (546, 280)])

text("①体育館", (590, 372), 5.0)
text("設計GL=27.20", (650, 386), 2.0)
text("SGL+19800", (650, 396), 1.8)
text("サブアリーナ", (505, 440), 2.8)
text("SGL+15300", (505, 452), 1.8)
text("SGL+1300", (490, 352), 1.8)
text("メインアリーナ", (650, 440), 3.0)

# 小規模建物（②〜⑫）
small = {
    "⑥": ([(504, 638), (540, 638), (540, 650), (504, 650)], "屋外トイレ・倉庫棟", (522, 658)),
    "⑦": ([(563, 246), (584, 246), (584, 256), (563, 256)], "上屋1", (573, 240)),
    "⑧": ([(588, 252), (600, 252), (600, 260), (588, 260)], "上屋2", (594, 266)),
    "⑨": ([(452, 280), (468, 280), (468, 292), (452, 292)], "車椅子駐車場1", (440, 276)),
    "⑩": ([(600, 238), (640, 238), (640, 252), (600, 252)], "車椅子駐車場2", (620, 232)),
    "②": ([(402, 290), (410, 290), (410, 296), (402, 296)], "", None),
    "③": ([(402, 299), (410, 299), (410, 305), (402, 305)], "", None),
    "④": ([(414, 290), (424, 290), (424, 297), (414, 297)], "", None),
    "⑤": ([(414, 300), (424, 300), (424, 307), (414, 307)], "", None),
    "⑪": ([(388, 300), (396, 300), (396, 306), (388, 306)], "", None),
    "⑫": ([(388, 309), (396, 309), (396, 315), (388, 315)], "", None),
}
for no, (pts, name, lp) in small.items():
    hatch(pts)
    pl(pts, "建物", closed=True)
    if name:
        text(f"{no}{name}", lp, 1.8)
text("SGL+3600", (522, 632), 1.6)
# 北西の小建物 引出し凡例（原図左上の位置）
legend_nw = ["⑤自転車置場2", "④自転車置場1", "③バイク置場2", "②バイク置場1",
             "⑫受水槽ポンプ室2", "⑪受水槽ポンプ室1"]
for i, s in enumerate(legend_nw):
    y = 197 + i * 7
    x = 285 if i < 4 else 250
    text(s, (x, y), 1.8, align=TextEntityAlignment.MIDDLE_LEFT)
    pl([(x + 40 if i < 4 else x + 48, y), (400, 300)], "文字")

# ================================================================ ロータリー・広場
rot_out = [(452, 262), (535, 262), (540, 270), (540, 318), (452, 318), (446, 310), (446, 270)]
pl(rot_out, "道路", closed=True)
island = [(470, 276), (515, 276), (515, 304), (470, 304)]
pl(island, "外構", closed=True)
text("ロータリー", (492, 290), 3.2)
pl([(410, 250), (470, 250), (470, 261), (410, 261)], "駐車場", closed=True)
text("大型バス2台駐車スペース", (440, 255), 1.6)
# 北側広場
pl([(520, 150), (600, 142), (600, 240), (520, 240)], "外構", closed=True)
for y in (160, 172, 184, 196):
    pl([(560, y), (568, y), (568, y + 7), (560, y + 7)], "外構", closed=True)
text("広場", (548, 212), 3.0)
text("SGL+8290", (550, 225), 1.6)
text("KBM1  H=27.812", (450, 168), 2.0)

# ================================================================ 駐車場
# 一般利用者用駐車場 291台
n_gen = 0
for y, x0 in [(352, 322), (386, 290), (420, 256), (454, 256), (488, 272), (522, 302), (556, 345)]:
    n_gen += double_row((x0, y), (412, y))
pl([(412, 340), (425, 340), (425, 565), (412, 565)], "駐車場", closed=True)
text("一般利用者用駐車場　291台", (345, 437), 3.5)
# 斜面沿いの駐車ます
n_gen += stall_row((235, 560), (470, 650), side=-1)
n_gen += stall_row((300, 590), (520, 680), side=+1)

# 駐車場兼イベント広場 211台（ます列は南北向き）
n_evt = 0
for x0, x1, y0, y1 in [(605, 725, 150, 150), (605, 760, 200, 200), (605, 815, 250, 250)]:
    pass
for y in (150, 197, 244):
    x_end = {150: 735, 197: 790, 244: 845}[y]
    n_evt += stall_row((605, y), (x_end, y - 3 if y == 150 else y), side=-1)
for y in (197, 244):
    x_end = {197: 790, 244: 845}[y]
    n_evt += stall_row((605, y), (x_end, y), side=+1)
text("駐車場兼イベント広場", (660, 172), 4.0)
text("211台", (660, 182), 3.5)
text("大型バス 14台", (760, 320), 2.0)

# 関係者用駐車場 95台
n_rel = 0
n_rel += stall_row((737, 345), (737, 498), side=+1)
n_rel += double_row((782, 360), (782, 498))
n_rel += stall_row((826, 360), (826, 498), side=+1)
pl([(740, 305), (835, 305), (835, 340), (740, 340)], "駐車場", closed=True)
text("関係者用駐車場　95台", (759, 425), 3.2, rot=90)
pl([(790, 338), (812, 338), (812, 350), (790, 350)], "建物", closed=True)
text("ゴミ置場", (801, 344), 1.6)

# ================================================================ 外構
# 連絡路兼サービス路
pl([(445, 510), (815, 510)], "道路")
pl([(445, 528), (812, 528)], "道路")
text("連絡路兼サービス路", (640, 520), 3.2)
text("自転車置場50台", (505, 505), 2.0)
# 管理用通路（関係者駐車場〜南側）
pl([(800, 385), (792, 460), (775, 497), (700, 522), (640, 532), (606, 552), (601, 700), (585, 830)], "道路")
pl([(810, 385), (802, 462), (786, 503), (705, 530), (645, 540), (614, 558), (610, 700), (595, 832)], "道路")
# 雨水流出抑制槽（地下）
tank = [(490, 516), (578, 516), (578, 540), (490, 540)]
pl(tank, "外構", closed=True)
pl([tank[0], tank[2]], "外構")
pl([tank[1], tank[3]], "外構")
text("雨水流出抑制槽（地下）", (534, 528), 1.6)
# テニスコート 6面
courts = [(487, 547, 520, 607), (523, 547, 557, 607), (560, 547, 588, 607), (596, 547, 624, 607),
          (558, 638, 588, 698), (596, 638, 624, 698)]
for x0, y0, x1, y1 in courts:
    pl([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "外構", closed=True)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) * 0.32, (y1 - y0) * 0.36
    pl([(cx - w, cy - h), (cx + w, cy - h), (cx + w, cy + h), (cx - w, cy + h)], "外構", closed=True)
    pl([(cx - w, cy), (cx + w, cy)], "外構")
    pl([(cx, cy - h * 0.55), (cx, cy + h * 0.55)], "外構")
pl([(478, 540), (632, 540), (632, 612), (478, 612)], "外構", closed=True)
pl([(550, 630), (632, 630), (632, 706), (550, 706)], "外構", closed=True)
text("テニスコート６面", (560, 620), 3.5)
# 円形広場
c = T((450, 573))
msp.add_ellipse(c, major_axis=(0, pm(11.7)), ratio=0.77, dxfattribs={"layer": "外構"})
circle((450, 573), 2.5, "外構")
# 新設階段
st = [(430, 660), (452, 668), (470, 703), (448, 696)]
pl(st, "外構", closed=True)
for i in range(1, 8):
    t = i / 8
    a = (st[0][0] + (st[3][0] - st[0][0]) * t, st[0][1] + (st[3][1] - st[0][1]) * t)
    b = (st[1][0] + (st[2][0] - st[1][0]) * t, st[1][1] + (st[2][1] - st[1][1]) * t)
    pl([a, b], "外構")
text("新設階段", (405, 682), 2.8)

# ================================================================ 等高線・周辺
for k in range(4):
    o = k * 7
    pl([(305 + o, 662 + o * 0.6), (380 + o, 692 + o), (470 + o, 735 + o), (550, 790 + o), (585, 815 + o * 0.4)], "等高線")
for k in range(5):
    o = k * 8
    pl([(640 + o, 560), (650 + o, 640), (660 + o, 720), (640 + o * 0.5, 800)], "等高線")
pl([(470, 762), (500, 740), (540, 750), (575, 800)], "等高線")
pl([(735, 600), (790, 575)], "道路")
pl([(735, 600), (700, 640), (690, 700)], "道路")
text("既存施設", (735, 610), 2.2)
text("沢渡川緑地", (215, 705), 3.0)

# 下水管（凡例に対応する本管ルート：概略）
pl([(606, 556), (640, 532), (790, 512)], "下水管")
text("既設下水道本管へ接続", (660, 560), 1.6)

# ================================================================ 方位
nc = T((832, 687))
r = pm(9)
msp.add_circle(nc, r, dxfattribs={"layer": "図枠"})
ang = math.radians(98)                      # 原図の北は上からわずかに西寄り
tip = (nc[0] + r * math.cos(ang), nc[1] + r * math.sin(ang))
tail = (nc[0] - r * math.cos(ang), nc[1] - r * math.sin(ang))
msp.add_line(tail, tip, dxfattribs={"layer": "図枠", "lineweight": 70})
msp.add_line((nc[0] - r, nc[1]), (nc[0] + r, nc[1]), dxfattribs={"layer": "図枠"})
t = msp.add_text("N", height=pm(4), dxfattribs={"layer": "文字", "style": "JP"})
t.set_placement((tip[0] - pm(1.5), tip[1] + pm(5)), align=TextEntityAlignment.MIDDLE_CENTER)

# ================================================================ 図枠（A1, 1/600）
# 図枠の左下を写真の (28, 902) 付近に合わせる
fx0, fy0 = T((28, 902))
FW, FH = 841 - 20, 594 - 20                  # 余白 10mm
fx0 -= pm(4)
def F(x, y):                                 # 図枠内 用紙mm → モデル
    return (fx0 + pm(x), fy0 + pm(y))
def frect(x0, y0, x1, y1, lw=None):
    a = {"layer": "図枠"}
    if lw:
        a["lineweight"] = lw
    msp.add_lwpolyline([F(x0, y0), F(x1, y0), F(x1, y1), F(x0, y1)], close=True, dxfattribs=a)
def fline(x0, y0, x1, y1):
    msp.add_line(F(x0, y0), F(x1, y1), dxfattribs={"layer": "図枠"})
def ftext(s, x, y, h=3.0, align=TextEntityAlignment.MIDDLE_LEFT):
    t = msp.add_text(s, height=pm(h), dxfattribs={"layer": "文字", "style": "JP"})
    t.set_placement(F(x, y), align=align)

frect(0, 0, FW, FH, lw=70)

# 表題欄
TB = 34
frect(0, 0, FW, TB, lw=50)
fline(70, 0, 70, TB)
for y in (TB / 3, TB * 2 / 3):
    fline(0, y, 70, y)
ftext("施工者 担当", 3, TB * 5 / 6, 2.5)
ftext("監理者 担当", 3, TB * 3 / 6, 2.5)
ftext("備考", 3, TB / 6, 2.5)
fline(420, 0, 420, TB)
ftext("トレース図（原図：株式会社 大建設計 作成 配置図）", 425, TB * 0.70, 3.0)
ftext("原図日付 2018.10.12（写真からの読取り）", 425, TB * 0.30, 2.5)
fline(560, 0, 560, TB)
fline(560, TB / 2, FW, TB / 2)
ftext("工事名称", 562, TB * 0.88, 2.0)
ftext("東町運動公園体育館建設工事", 575, TB * 0.70, 4.5)
ftext("図面名称", 562, TB * 0.38, 2.0)
ftext("配置図", 575, TB * 0.20, 5.0)
fline(760, 0, 760, TB)
ftext("縮尺", 762, TB * 0.88, 2.0)
ftext("A1 1/600", 765, TB * 0.70, 3.5)
ftext("図番", 762, TB * 0.38, 2.0)
ftext("A-005", 770, TB * 0.20, 4.5)

# 凡例（右側）
LX = 640
y = 355
ftext("新設アクセス道路", LX, y, 3.0); y -= 6
ftext("・完成予定時期（建物と同時期完成）", LX + 3, y, 2.5); y -= 5
ftext("・公園園路（イベント時に使用）", LX + 3, y, 2.5); y -= 10
ftext("下水管等現況　凡例", LX, y, 3.0); y -= 7
frect(LX + 4, y - 1.5, LX + 20, y + 1.5)
fline(LX + 12, y - 1.5, LX + 12, y + 1.5)
ftext("既設下水道本管　2000φ", LX + 26, y, 2.5); y -= 7
msp.add_line(F(LX + 4, y), F(LX + 20, y), dxfattribs={"layer": "下水管", "lineweight": 50})
ftext("既設下水道本管　900φ", LX + 26, y, 2.5); y -= 10
ftext("道路種別", LX, y, 3.0); y -= 6
ftext("<42-1-1>　建築基準法42条第一項1号", LX + 6, y, 2.5); y -= 5
ftext("<42-2>　 建築基準法42条第二項", LX + 6, y, 2.5); y -= 9
ftext("その他凡例", LX, y, 3.0); y -= 8
frect(LX + 4, y - 2.5, LX + 24, y + 2.5)
h = msp.add_hatch(color=9, dxfattribs={"layer": "建物ハッチ"})
h.paths.add_polyline_path([F(LX + 4, y - 2.5), F(LX + 24, y - 2.5), F(LX + 24, y + 2.5), F(LX + 4, y + 2.5)], is_closed=True)
h.transparency = 0.6
ftext("今回申請建物", LX + 30, y, 2.5); y -= 7
ftext("SGL+□□□□", LX + 2, y, 2.2)
ftext("各建物毎の設計GLからの高さを示す", LX + 30, y, 2.5); y -= 7
frect(LX + 8, y - 2.5, LX + 16, y + 2.5)
ftext("水戸市建築基準条例39条　前面空地（奥行4.5m）", LX + 30, y, 2.5); y -= 7
frect(LX + 8, y - 2.5, LX + 16, y + 2.5)
ftext("水戸市建築基準条例40条　前面空地（幅2.0m）", LX + 30, y, 2.5); y -= 10
ftext("接道長さ", LX, y, 3.0)
ftext("（写真の解像度では数値判読不可・原図参照）", LX + 22, y, 2.5)

# 建物一覧表
cols = [("番号", 14), ("建物名", 46), ("建築面積", 26), ("延床面積", 26),
        ("最高高さ", 22), ("最高軒高", 22), ("設計GL(m)", 23)]
rows = [
    ("①", "体育館", "13,709.71", "16,366.71", "22.98", "20.81", "27.20"),
    ("②", "バイク置場1", "12.30", "12.30", "2.18", "2.18", "27.20"),
    ("③", "バイク置場2", "12.30", "12.30", "2.18", "2.18", "27.20"),
    ("④", "自転車置場1", "30.20", "30.20", "2.14", "2.16", "※"),
    ("⑤", "自転車置場2", "30.20", "30.20", "2.14", "2.16", "※"),
    ("⑥", "屋外トイレ・倉庫棟", "77.50", "77.50", "2.60", "2.60", "※"),
    ("⑦", "上屋1", "68.00", "68.00", "3.425", "3.425", "※"),
    ("⑧", "上屋2", "22.00", "22.00", "3.425", "3.425", "※"),
    ("⑨", "車椅子駐車場1", "60.27", "60.27", "3.208", "3.208", "※"),
    ("⑩", "車椅子駐車場2", "100.45", "100.45", "3.208", "3.208", "※"),
    ("⑪", "受水槽ポンプ室1", "12.00", "12.00", "5.380", "4.385", "※"),
    ("⑫", "受水槽ポンプ室2", "13.00", "13.00", "4.385", "3.880", "※"),
]
TX, TYtop, RH = 640, 190, 7.0
TW = sum(w for _, w in cols)
nrow = len(rows) + 1
frect(TX, TYtop - RH * nrow, TX + TW, TYtop, lw=35)
x = TX
for i, (name, w) in enumerate(cols):
    if i:
        fline(x, TYtop - RH * nrow, x, TYtop)
    ftext(name, x + w / 2, TYtop - RH / 2, 2.5, align=TextEntityAlignment.MIDDLE_CENTER)
    x += w
for r in range(1, nrow):
    fline(TX, TYtop - RH * r, TX + TW, TYtop - RH * r)
for r, row in enumerate(rows, start=1):
    x = TX
    yc = TYtop - RH * r - RH / 2
    for (name, w), val in zip(cols, row):
        if name == "建物名":
            ftext(val, x + 2, yc, 2.5)
        elif name == "番号":
            ftext(val, x + w / 2, yc, 2.5, align=TextEntityAlignment.MIDDLE_CENTER)
        else:
            ftext(val, x + w - 2, yc, 2.5, align=TextEntityAlignment.MIDDLE_RIGHT)
        x += w
ftext("※ 写真から判読できない値（原図で要確認）。面積の単位は㎡、高さはm。",
      TX, TYtop - RH * nrow - 5, 2.2)

# 左上の注記（面積・出入口幅）
NX, NY = 30, 545
notes = [
    "車椅子駐車場1 ：  60.27㎡",
    "車椅子駐車場2 ： 100.45㎡",
    "バイク置場1　 ：  12.30㎡",
    "バイク置場2　 ：  12.30㎡",
    "自転車置場面積：（判読不可）",
    "水戸市建築基準条例",
    "　第27条・第39条・第40条 に関する出入口幅・前面空地の検討（詳細は原図参照）",
    "【1階】日常的に使用される出入口幅 / 必要前面空地 ほか（数値判読不可）",
]
for i, s in enumerate(notes):
    ftext(s, NX, NY - i * 5.5, 2.4)

ftext("※本図は原図写真からのトレースによる概略図です。寸法・位置は通り芯 X1–X16=115,000、"
      "Y16–Y1=92,600 を基準に換算（誤差 数m程度）。施工・申請には原図を使用してください。",
      10, TB + 6, 2.6)

if __name__ == "__main__":
    doc.saveas("haichizu_A-005_trace.dxf")
    print("stalls: general", n_gen, " event", n_evt, " staff", n_rel)
