# sciglyph

**用纯 matplotlib 画顶刊级科研插图 —— 不需要 BioRender,不需要 Illustrator。**

[English](README.md) | 简体中文

论文开篇的总览图和算法架构图,通常是在订阅制工具里手工画的。画得漂亮,但**不可复现**:
没法 diff、数据一变就得重画、也进不了版本管理。

`sciglyph` 提供图元,让你把同样的图**写成代码**。

<p align="center">
  <img src="gallery/overview_figure.png" width="88%">
</p>

<p align="center">
  <img src="gallery/architecture.png" width="100%">
</p>

<sub>上面两张图完全由 <a href="examples/">examples/</a> 里的脚本生成,没有任何手工修饰。
内容是合成的,换成你自己的数据即可复用整套版式。</sub>

## 为什么

| | 订阅制工具 | `sciglyph` |
|---|---|---|
| 可复现 | ✗ 手工挪像素 | ✓ 一个脚本 |
| 版本管理 | ✗ 二进制文件 | ✓ 可 diff 的源码 |
| 数据驱动 | ✗ 数字要重新誊 | ✓ 直接读实验结果 |
| 矢量输出 | ~ 取决于导出设置 | ✓ PDF/SVG 且文字可编辑 |
| 成本 | 订阅费 | 免费,MIT |

## 安装

```bash
pip install sciglyph
```

只依赖 `matplotlib` 和 `numpy`。

## 快速开始

```python
import matplotlib.pyplot as plt
from sciglyph import bio, set_canvas, report, RC

plt.rcParams.update(RC)
fig = plt.figure(figsize=(7.2, 3.0), dpi=300)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
set_canvas(fig)                      # 非正方形画布必须先调用

bio.person(ax, .08, .55, s=.30)
bio.dna(ax, .25, .55, w=.05, h=.45, n=2)
bio.cell(ax, .42, .55, r=.06, seed=1)

report(fig, ax)                      # 存图前查文字碰撞
fig.savefig("figure.pdf", bbox_inches="tight")
```

## 包含什么

**`sciglyph.bio`** —— Nature/Science 式总览图图元:
`person`(队列人群)· `dna` · `cell` · `lipid` · `metabolite` ·
`nucleosome_chain` · `umap_layer`(斜叠图集卡片)· `seq_logo`(按信息量缩放字母,
不需要 logomaker)· `stacked_planes` · `rbox` · `arr`

**`sciglyph.arch`** —— 算法架构图图元:
`cuboid` / `feature_stack`(3D 特征块)· `trapezoid`(编码器)·
`module_stack`(`Conv|BN|ReLU` 条)· `dashed_group`(`(a)/(b)/(c)` 分区)·
`flow` · `op_circle` · `snowflake`(冻结骨干)· `image_thumb` ·
`embedding_space`(对比学习嵌入)· `loss_tag` · `bracket`

**`sciglyph.layout`** —— 出图前碰撞检测。

## 出图前就把布局问题查出来

图崩掉时,问题几乎从来不在图元,而在布局。`report()` 用**真实渲染 bbox**
自动找出重叠文字,不必肉眼去翻:

```python
report(fig, ax)
# [sciglyph.layout] 36 text objects
#   ! 'CD4 Treg/-FOXP3' x 'SMR' overlap 92%
```

也支持命令行:`python -m sciglyph.layout my_figure.py`

**它只覆盖"文字 vs 文字"**。被图元遮住的文字它看不见 —— 最后一步永远要亲眼看渲染图。

## 踩过的坑(都写进代码注释了)

- **务必先 `set_canvas(fig)`**:`[0,1]` 坐标下"圆"的物理尺寸是 `r·W × r·H`,
  12×3 的画布上每个圆都会被拉成橄榄球。
- **箭头锚点用 `feature_stack` 的返回值**,别写死坐标,否则块数一改全错位。
- **别在图里写 Unicode 符号**:`❄`(U+2744)多数无衬线字体没有该字形,会变豆腐块,
  要画出来(`arch.snowflake`)。
- **多条半透明填充叠加会糊成一色**:填充压到 `alpha<=0.15`、每条描实线、**并且**错开峰位,
  只调 alpha 没用。
- **字体**:Linux 上常常没有 Arial/Helvetica。`RC` 回退到 Liberation Sans
  (与 Arial metric-compatible),并设 `pdf.fonttype=42` 保证 PDF 里文字可编辑
  —— 这是多数期刊的硬要求。
- **别看哪儿空就往哪儿搬元素**:空白会搬家,不会消失。先想清楚元素属于哪一行,
  整组移动,再用象限墨水分布验收。

## 能力边界

它能做到"干净的扁平示意 + 数据面板混排",也就是 Nature/Science 总览图和 TPAMI
架构图的语域。**做不到**手绘插画(带阴影的器官、有质感的细胞、渐变高光)。
那类需求请嵌入 CC-BY 素材并标注来源,不要硬凑。

## 许可

MIT © Guo Cheng
