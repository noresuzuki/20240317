import sys, ezdxf
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy, TextPolicy
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
doc = ezdxf.readfile(sys.argv[1])
for st in doc.styles:
    if st.dxf.font.lower().startswith("msgothic"):
        st.dxf.font = "wqy-zenhei.ttc"   # 表示用の代替フォント
fig = plt.figure(figsize=(841/25.4, 594/25.4))
ax = fig.add_axes([0,0,1,1])
cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=(ColorPolicy.COLOR if __import__("os").environ.get("COLOR") else ColorPolicy.MONOCHROME_LIGHT_BG),
                    lineweight_scaling=0.6, min_lineweight=0.12, text_policy=TextPolicy.FILLING)
Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(doc.modelspace())
ax.set_aspect("equal"); ax.margins(0.01)
for out in sys.argv[2:]:
    fig.savefig(out, dpi=int(__import__("os").environ.get("DPI","150")) if out.endswith('.png') else None, facecolor="white")
