# 東町運動公園体育館建設工事 配置図（A-005）トレース図

原図の写真から起こした配置図です。

| ファイル | 内容 |
|---|---|
| `haichizu_A-005_trace.dxf` | CAD データ（単位 mm・実寸、A1 1/600 の図枠付き。AutoCAD / Jw_cad などで開けます） |
| `haichizu_A-005_trace.pdf` | A1 サイズの PDF |
| `haichizu_A-005_trace.png` | 確認用の画像 |
| `make_haichizu.py` | DXF を作るスクリプト（読み取った座標を直すときはここを編集） |
| `render.py` | DXF から PDF / PNG を書き出すスクリプト |

## 作り方と精度
- 写真上の座標を、通り芯 X1–X16（115,000）と Y16–Y1（92,600）の4交点を基準に射影変換し、実寸に直しています。
- 写真の解像度が低いため、形状・位置は概略です（誤差は数 m 程度）。駐車ますは区画の形から 2.5m×5.0m で並べ直したもので、台数は原図と一致しません。
- 一覧表のうち読めなかった値は「※」、接道長さの数値は「判読不可」としています。

## レイヤー
図枠 / 通り芯 / 敷地境界 / 道路 / 建物 / 建物ハッチ / 屋根 / 駐車場 / 外構 / 等高線 / 下水管 / 寸法 / 文字

## 再生成
```
pip install ezdxf matplotlib numpy
python3 make_haichizu.py
python3 render.py haichizu_A-005_trace.dxf haichizu_A-005_trace.pdf haichizu_A-005_trace.png
```
