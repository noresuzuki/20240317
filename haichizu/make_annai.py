# -*- coding: utf-8 -*-
"""
配置図トレース（make_haichizu.py）をベースに、
  ・施設案内図（ロータリー／入口／各駐車場／いこいの広場／テニスコート／車椅子・駐輪マーク）
  ・アクセスマップ（国道50号・スポーツセンター入口、出入口、臨時バス停、
    事前予約制有料駐車場A/B、車いす席購入者駐車場、関係者駐車場、周辺の目印）
の情報を重ねた「施設案内情報入り配置図」を作る。
"""
import ezdxf
from ezdxf.enums import TextEntityAlignment as A
import make_haichizu as B

doc, msp, T, pm = B.doc, B.msp, B.T, B.pm
F, ftext, frect, fline = B.F, B.ftext, B.frect, B.fline

# ---------------------------------------------------------------- 色（施設案内図に合わせる）
C_PARK = (168, 214, 240)    # 駐車場：水色
C_GYM = (245, 170, 205)     # 体育館：ピンク
C_COURT = (120, 190, 110)   # テニスコート：緑
C_WCHAIR = (160, 82, 45)    # 車いす席購入者駐車場：茶
C_PLAZA = (232, 226, 205)   # 広場：ベージュ
C_ROAD = (215, 215, 215)    # 通路・道路：グレー
C_BLUE = (30, 90, 200)      # マーク

doc.layers.add("案内_塗り", color=7)
doc.layers.add("案内_記号", color=5)
doc.layers.add("案内図", color=7)
for name, col in [("寸法", 8), ("駐車場", 150), ("外構", 94), ("下水管", 140)]:
    doc.layers.get(name).color = col

fills = []


def fill(pts_px, rgb, layer="案内_塗り"):
    h = msp.add_hatch(dxfattribs={"layer": layer})
    h.paths.add_polyline_path(B.TT(pts_px), is_closed=True)
    h.set_solid_fill(color=7, rgb=rgb)
    fills.append(h)
    return h


def texts(old):
    return [e for e in msp.query("TEXT") if e.dxf.text == old]


def retext(old, new, p_px=None, h=None):
    for e in texts(old):
        e.dxf.text = new
        if h:
            e.dxf.height = pm(h)
        if p_px:
            e.set_placement(T(p_px), align=A.MIDDLE_CENTER)


# ---------------------------------------------------------------- ベース図の調整
# 体育館の灰色ハッチはピンク塗りに置き換える
for hch in msp.query("HATCH"):
    v = list(hch.paths)[0].vertices
    if len(v) == 6:
        msp.delete_entity(hch)
        break
retext("市道（上市1号幹線）", "既存道路")
retext("①体育館", "①体育館", p_px=(632, 362))
B.text("（アダストリアみとアリーナ）", (632, 374), 3.2)
for e in texts("道路境界線"):
    if not e.dxf.rotation:
        e.set_placement(T((478, 243)), align=A.MIDDLE_CENTER)
retext("一般利用者用駐車場　291台", "一般利用者用駐車場　291台（設計）", h=3.2)
B.text("イベント時：事前予約制有料駐車場Ａ　280台", (345, 471), 2.6)
retext("駐車場兼イベント広場", "駐車場兼イベント広場　211台（設計）", p_px=(680, 168), h=3.2)
retext("211台", "イベント時：事前予約制有料駐車場Ｂ　100台", p_px=(680, 178), h=2.6)
retext("関係者用駐車場　95台", "関係者用駐車場　95台")
retext("⑩車椅子駐車場2", "⑩車椅子駐車場2")
for e in texts("沢渡川緑地"):
    e.set_placement(T((330, 742)), align=A.MIDDLE_CENTER)
for e in texts("配置図"):
    e.dxf.text = "配置図（施設案内情報入り）"
    e.dxf.height = pm(4.2)

# ---------------------------------------------------------------- ゾーン塗り
fill(B.site, (246, 246, 242))                                         # 敷地
fill([(497, 112), (517, 112), (517, 250), (497, 250)], C_ROAD)        # 出入口通路
fill([(446, 262), (540, 262), (540, 318), (446, 318)], C_ROAD)        # ロータリー
fill([(445, 506), (815, 506), (812, 530), (445, 530)], C_ROAD)        # 連絡路
fill([(410, 249), (471, 249), (471, 262), (410, 262)], C_ROAD)        # 大型バス
# 一般利用者用駐車場（有料駐車場A）
fill([(330, 336), (427, 336), (427, 570), (340, 570), (300, 535),
      (266, 500), (248, 466), (248, 410), (285, 372)], C_PARK)
fill([(232, 548), (472, 640), (526, 690), (296, 602)], C_PARK)
# 駐車場兼イベント広場（有料駐車場B）
fill([(602, 141), (730, 130), (862, 237), (850, 262), (602, 262)], C_PARK)
# 車いす席購入者駐車場（⑩の位置）
fill([(600, 232), (646, 232), (646, 262), (600, 262)], C_WCHAIR)
# 関係者用駐車場
fill([(736, 302), (838, 305), (842, 500), (736, 500)], C_PARK)
# 体育館
fill([(440, 318), (545, 318), (545, 278), (734, 278), (734, 500), (440, 500)], C_GYM)
# テニスコート
fill([(478, 540), (632, 540), (632, 612), (478, 612)], C_COURT)
fill([(550, 630), (632, 630), (632, 706), (550, 706)], C_COURT)
# いこいの広場
fill([(428, 532), (478, 540), (478, 625), (548, 628), (548, 706), (470, 703),
      (430, 662), (427, 600)], C_PLAZA)
fill([(520, 150), (600, 142), (600, 232), (520, 240)], C_PLAZA)       # 北側広場

# 塗りを一番下に描く
msp.set_redraw_order([(h.dxf.handle, f"{i + 1:X}") for i, h in enumerate(fills)])

# ---------------------------------------------------------------- 記号
def tri(p_px, direction="down", s=3.2):
    x, y = T(p_px)
    d = pm(s)
    pts = {"down": [(x - d, y + d), (x + d, y + d), (x, y - d * 0.6)],
           "right": [(x - d, y + d), (x - d, y - d), (x + d * 0.6, y)],
           "left": [(x + d, y + d), (x + d, y - d), (x - d * 0.6, y)]}[direction]
    h = msp.add_hatch(dxfattribs={"layer": "案内_記号"})
    h.paths.add_polyline_path(pts, is_closed=True)
    h.set_solid_fill(color=1, rgb=(200, 30, 60))


def badge(p, label, rgb=C_BLUE, px=True, s=3.0, hgt=1.8):
    x, y = T(p) if px else p
    d = pm(s)
    h = msp.add_hatch(dxfattribs={"layer": "案内_記号"})
    h.paths.add_polyline_path([(x - d, y - d), (x + d, y - d), (x + d, y + d), (x - d, y + d)], is_closed=True)
    h.set_solid_fill(color=5, rgb=rgb)
    t = msp.add_text(label, height=pm(hgt), dxfattribs={"layer": "案内_記号", "style": "JP", "color": 7})
    t.rgb = (255, 255, 255)
    t.set_placement((x, y), align=A.MIDDLE_CENTER)


def wchair(p, px=True):
    """車椅子ピクトグラム（青地に白線）"""
    badge(p, "", px=px)
    x, y = T(p) if px else p
    a = {"layer": "案内_記号", "lineweight": 40}
    W = (255, 255, 255)
    def P(u, v):
        return (x + pm(u), y + pm(v))
    c = msp.add_circle(P(-0.5, 2.1), pm(0.5), dxfattribs=a); c.rgb = W
    c = msp.add_circle(P(-0.3, -1.1), pm(1.4), dxfattribs=a); c.rgb = W
    l = msp.add_lwpolyline([P(-0.8, 1.3), P(-0.8, -0.2), P(1.0, -0.2), P(1.7, -1.9)], dxfattribs=a); l.rgb = W


def bike(p, px=True):
    badge(p, "輪", px=px, hgt=3.0)


def bus(p, px=True):
    badge(p, "バス", rgb=(0, 120, 70), px=px, hgt=1.9)


# 建物出入口（施設案内図の▼）
tri((553, 238), "down")
tri((432, 334), "right")
# 車椅子使用者用駐車場
wchair((460, 274))
wchair((418, 346))
wchair((623, 247))
B.text("車いす席購入者駐車場", (623, 224), 2.0)
# 駐輪場
bike((413, 285))
bike((470, 505))
# 臨時バス停
bus((440, 238))
B.text("東町運動公園体育館前", (405, 222), 2.4)
B.text("（臨時バス停）", (405, 230), 2.0)

# 出入口と国道50号方向の矢印
B.pl([(497, 112), (497, 250)], "道路")
B.pl([(517, 112), (517, 157)], "道路")
B.text("出入口", (507, 255), 3.0)
x0, y0 = T((507, 235))
x1, y1 = T((507, 135))
msp.add_line((x0, y0), (x1, y1), dxfattribs={"layer": "案内_記号", "lineweight": 70, "color": 1})
h = msp.add_hatch(dxfattribs={"layer": "案内_記号"})
d = pm(2.5)
h.paths.add_polyline_path([(x1 - d, y1 - d * 1.2), (x1 + d, y1 - d * 1.2), (x1, y1 + d)], is_closed=True)
h.set_solid_fill(color=1, rgb=(200, 30, 60))
B.text("至 国道50号", (480, 186), 2.8, align=A.MIDDLE_RIGHT)
B.text("（スポーツセンター入口 交差点）", (480, 196), 2.2, align=A.MIDDLE_RIGHT)

# いこいの広場・テニスコート
B.text("いこいの広場", (452, 610), 3.2)
tri((440, 690), "left", s=2.0)

# ---------------------------------------------------------------- 凡例（左上）
LY = 488
ftext("施設案内 凡例", 10, LY, 3.2)
rows = [("tri", "建物出入口"), ("wc", "車椅子使用者用駐車場"), ("bk", "駐輪場（自転車・バイク）"),
        ("bus", "臨時バス停留所")]
swatch = [(C_GYM, "体育館（アダストリアみとアリーナ）"), (C_PARK, "駐車場"),
          (C_WCHAIR, "車いす席購入者駐車場"), (C_COURT, "テニスコート"), (C_PLAZA, "広場")]
for i, (k, lab) in enumerate(rows):
    y = LY - 9 - i * 8
    p = F(16, y)
    if k == "tri":
        x, yy = p
        dd = pm(2.5)
        hh = msp.add_hatch(dxfattribs={"layer": "案内_記号"})
        hh.paths.add_polyline_path([(x - dd, yy + dd), (x + dd, yy + dd), (x, yy - dd * 0.6)], is_closed=True)
        hh.set_solid_fill(color=1, rgb=(200, 30, 60))
    elif k == "wc":
        wchair(p, px=False)
    elif k == "bk":
        bike(p, px=False)
    else:
        bus(p, px=False)
    ftext(lab, 24, y, 2.6)
for i, (rgb, lab) in enumerate(swatch):
    y = LY - 9 - i * 8
    hh = msp.add_hatch(dxfattribs={"layer": "案内_記号"})
    hh.paths.add_polyline_path([F(82, y - 2.5), F(92, y - 2.5), F(92, y + 2.5), F(82, y + 2.5)], is_closed=True)
    hh.set_solid_fill(color=7, rgb=rgb)
    frect(82, y - 2.5, 92, y + 2.5)
    ftext(lab, 95, y, 2.6)

# ---------------------------------------------------------------- 案内図（アクセスマップ）
IX, IY, IS = 8, 46, 150          # 用紙上の位置・大きさ(mm)
def M(mx, my):
    return F(IX + mx * IS / 1000, IY + IS - my * IS / 1000)
def mpoly(pts, rgb=None, layer="案内図", closed=True, lw=None, color=None):
    P = [M(*p) for p in pts]
    if rgb:
        hh = msp.add_hatch(dxfattribs={"layer": layer})
        hh.paths.add_polyline_path(P, is_closed=True)
        hh.set_solid_fill(color=7, rgb=rgb)
    a = {"layer": layer}
    if lw:
        a["lineweight"] = lw
    if color:
        a["color"] = color
    msp.add_lwpolyline(P, close=closed, dxfattribs=a)
def mtext(s, mx, my, h=2.4, align=A.MIDDLE_CENTER, rot=0, rgb=None):
    t = msp.add_text(s, height=pm(h), dxfattribs={"layer": "案内図", "style": "JP", "rotation": rot})
    if rgb:
        t.rgb = rgb
    t.set_placement(M(mx, my), align=align)
def mroad(p0, p1, w):
    import math
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    nx, ny = -(y1 - y0) / L * w / 2, (x1 - x0) / L * w / 2
    mpoly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)],
          rgb=(255, 255, 255), color=8)

# 背景
mpoly([(0, 0), (1000, 0), (1000, 1000), (0, 1000)], rgb=(222, 222, 222), lw=50)
# 道路（白）
for p0, p1, w in [((0, 40), (1000, 205), 55),          # 国道50号
                  ((120, 175), (680, 262), 26), ((680, 262), (1000, 280), 26),
                  ((40, 205), (60, 600), 26),
                  ((600, 0), (690, 270), 26), ((690, 270), (980, 960), 26),
                  ((830, 0), (870, 250), 26),
                  ((330, 425), (530, 420), 24), ((530, 420), (1000, 330), 24),
                  ((560, 480), (690, 600), 22),
                  ((0, 600), (140, 520), 22)]:
    mroad(p0, p1, w)
# 敷地
mpoly([(20, 620), (195, 470), (330, 432), (525, 425), (610, 540), (585, 560), (605, 700),
       (570, 745), (390, 745), (385, 975), (320, 980), (205, 820), (105, 760), (20, 650)], rgb=(165, 165, 165))
mpoly([(30, 625), (95, 585), (208, 578), (208, 780), (100, 780), (30, 700)], rgb=(255, 240, 60))   # 有料A
mpoly([(345, 442), (520, 442), (570, 500), (570, 585), (478, 585), (476, 555), (330, 555)], rgb=(255, 240, 60))  # 有料B
mpoly([(328, 510), (370, 510), (370, 555), (328, 555)], rgb=C_WCHAIR)
mpoly([(215, 605), (318, 556), (474, 556), (474, 720), (215, 720)], rgb=(20, 20, 150))           # アリーナ
mpoly([(480, 590), (572, 590), (550, 720), (480, 720)], rgb=(110, 110, 110))                     # 関係者
mtext("アダストリア", 345, 625, 3.2, rgb=(255, 240, 60))
mtext("みとアリーナ", 345, 665, 3.2, rgb=(255, 240, 60))
mtext("有料駐車場Ａ", 118, 655, 2.4)
mtext("280台", 118, 700, 2.4)
mtext("有料駐車場Ｂ", 470, 495, 2.4)
mtext("100台", 515, 535, 2.4)
mtext("関係者", 526, 640, 2.0, rgb=(255, 255, 255))
mtext("車いす席購入者駐車場", 470, 380, 2.0)
msp.add_line(M(470, 392), M(350, 530), dxfattribs={"layer": "案内図"})
# 出入口・ルート
msp.add_line(M(320, 440), M(360, 120), dxfattribs={"layer": "案内図", "color": 1, "lineweight": 70})
mtext("出入口", 300, 470, 2.6)
mtext("▲", 360, 128, 2.6, rgb=(220, 30, 60))
# 信号・ラベル
mpoly([(300, 85), (430, 85), (430, 135), (300, 135)], rgb=(255, 255, 255))
for i, c in enumerate([(240, 80, 110), (250, 230, 0), (70, 90, 200)]):
    mtext("●", 325 + i * 40, 110, 3.6, rgb=c)
mtext("スポーツセンター入口", 365, 55, 2.4)
mtext("国道50号", 470, 168, 2.4, rot=-9)
mtext("偕楽園北口", 640, 185, 2.2)
mtext("至 水戸駅北口", 965, 120, 2.4, rot=-90)
mtext("大工町三丁目", 860, 300, 2.2)
mtext("（バス停）", 860, 330, 1.8)
mtext("歴史館入口", 880, 935, 2.2)
mtext("臨時バス停", 225, 480, 2.0)
mtext("（体育館前）", 225, 505, 1.8)
mtext("■", 245, 535, 2.4, rgb=(0, 120, 70))
mtext("案内図（概略・縮尺なし）", 500, -28, 3.2)
mtext("N↑", 960, 960, 3.0)

# ---------------------------------------------------------------- 注記・表題
ftext("※施設案内図・アクセスマップの情報を重ねて表示。駐車台数は設計台数（配置図）とイベント時の運用台数"
      "（事前予約制）を併記。マーク位置は案内図からの概略位置。", 172, B.TB + 12, 2.6)

if __name__ == "__main__":
    doc.saveas("haichizu_A-005_annai.dxf")
    print("ok")
