# Morrey／Garofalo–Rotz 实例

这是 2026-11-08 已执行的 OG 试写及修正实例，用于理解知识分配和核验边界，不是新的数学证明。下列 UUID、Zotero key 与页码只属于当时的图谱和文献版本；后续操作先读取实际对象，不能在其他图谱直接复用。

## 页面与子树的分配

| 对象 | 所在页面／类型 | 块或子树 |
|---|---|---|
| 当前端点估计研究 | Endpoint estimates for cylindrical stable Heisenberg solutions／Research | 问题、设定、假设、主结果、证明结构、支持结果、研究来源 |
| Morrey 概念与通用定义 | Morrey spaces／Topic | 范数约定、适用条件、相关结果引用；不为每个指数再建页 |
| 对称性概念 | Cylindrical symmetry／Topic | 当前语境下的定义，引用 Garofalo–Rotz 原定义；区分 cylindrical 与 polyradial |
| Discrepancy 概念 | Discrepancy on Carnot groups／Topic | 当前记号及与原定义的对应，引用 Paper 原文块 |
| 外部论文 | N. Garofalo, K. Rotz; Calc. Var. Partial Differential Equations; 2015／Paper | 原 Definition 5.4、Definition 6.10、Proposition 6.11 及其证明 |

完整结果是一棵子树，而不是一个物理块，也不自动变成独立页面。Topic 不强制套固定章节；此表是本研究已有内容的实际分配。

## Research 内部拆分

- 保留 Heisenberg normalization 汇总根；坐标、群运算、Haar 测度、水平向量场、水平梯度、sub-Laplacian、能量、伸缩、生成元、齐次维数、规范、距离、球各有完整子块。具体计算引用所需子块，整体设定仍可引用汇总根。
- `#Assumption (F0)` 的子树保存 $f\in C^1(\mathbb R)$；`#Assumption (F+)` 保存 $f(s)\geq0$ 对所有 $s\in\mathbb R$。光滑性／稳定性、对称性与增长假设按真实使用分别组织。
- 主定理保留一个来源身份；共同条件、BMO 结论、Morrey 结论分别是直接子块。证明提纲属于该定理下的 `#Proof`，提纲性质在 `#Comment` 中说明。
- 独立的函数分析命题以其实际能量增长条件为假设。它在 PDE 解上的应用作为 Research 中的应用论证，不把 PDE 定理误列为该通用命题的证明前提。
- 稿件版本、路径、原标签与当前块的对应集中在研究来源。会话用真实标题的 Codex 深链接作入口，字面编号如 `261102#2a` 采用 code 等表示，避免 `#2a` 变成意外标签。

生成条件段时，把记号链接融入句子，例如：

> …, where the notation is as in [Heisenberg conventions](((6af02a9d-7432-4eb5-8c06-c04cd5baba51))), [endpoint exponents](((6af02a9e-7564-429a-a6ed-f737cdbaf242))) and [Morrey norm convention](((6af02ab0-0e5e-4fb1-ae95-29f4bda64137))).

不能用一句 “Use these conventions” 代替结果中完整的数学条件。

## 实际依赖如何表示

| 使用位置 | 依赖／来源 | 关系与限制 |
|---|---|---|
| 当前 discrepancy 定义 | Paper Definition 5.4 | 原定义来源；当前记号另行对应 |
| 当前 cylindrical 定义 | Definition 6.10(a) | 定义的特化；不混入 (b) 的 polyradial 条件 |
| 当前零 discrepancy 应用 | Proposition 6.11(a)，需要时明确引用 (b) | 引用原命题的群与对称性限制；在当前归一化下单独核对 |
| Orbit packing | 当前研究的完整 cylindrical symmetry 假设 | 独立要求；不能从零 discrepancy 自动推出 |
| 函数分析命题的应用 | 衰减结果中的具体能量结论 + 通用函数分析命题 | 应用依赖；不把整个包含 Morrey 结论的定理作为输入造成假循环 |
| 源稿件的直接计算 | 本地稿件和当前记号 | 新增文献依据是补充或替代解释，不能倒写成原稿已引用该论文 |

源稿还提到独立推论 `h:cor:smooth-growth` 中的 critical gradient $M^{2,2}$ bound；本次没有导入该推论。此范围说明放主结果的署名评论中，不把它当作已导入结论或创建无内容的依赖块。

## Paper 的实际结构

下面是结构示意，角括号内容代表当次实际已核实文本；示意本身不作为待写入原文。

```text
- #Paper
- ## Index information
  - **Published version (Current version)**
    - [Zotero item](zotero://select/library/items/5C44I6JZ)
  - #Comment on Version
    - <Original selected-import scope> #GPT-6.1-Sol
    - <Verified preprint/published numbering correspondence> #Codex
- ## Full-text
  - ### 5 First variation of the energy and discrepancy
    - #Definition 5.4 (Discrepancy)
      - <Complete source definition>
      - <Source continuation>
  - ### 6 Analysis of the discrepancy in Carnot groups of Heisenberg type
    - <Original notation preceding Definition 6.10>
    - #Definition 6.10
      - <Shared setting>
      - (a) <Cylindrical symmetry>
      - (b) <Polyradial symmetry>
    - #Proposition 6.11
      - <Shared setting>
      - (a) <Original conclusion and its conditions>
      - (b) <Original conclusion and its conditions>
      - #Proof
        - <Original proof paragraphs, in order>
```

本次不存在合规的 Zotero MathSciNet 子笔记／快照，不能从父条目的 MR 字段补造记录。自拟 Published version 书目块已移除。Index 中的链接提供访问，不代表完整索引记录或某个 Paper 完成度。

上述署名来自当次可核实的历史评论。新生成的评论按实际作者／模型署名；搬运历史评论保留原始署名。

## 当次定位与验证证据

| 原文单元 | 正式版编号 | 预印本编号 | Printed page | PDF physical page |
|---|---|---|---|---|
| Discrepancy | Definition 5.4 | Definition 6.4 | 2211 | 15 |
| Symmetry | Definition 6.10 | Definition 9.10 | 2217 | 21 |
| Symmetry and vanishing discrepancy | Proposition 6.11 | Proposition 9.11 | 2218 | 22 |

正式版 DOI 为 `10.1007/s00526-015-0862-x`；parent key 为 `5C44I6JZ`，PDF attachment key 为 `AQD3EIWR`，二者不是同一对象。

可核对的历史结果块包括：

| 对象 | UUID |
|---|---|
| Definition 5.4 | `6af036fe-f286-4ca8-aa16-33a2c76f0cb6` |
| Definition 6.10(a) | `6af036ff-583a-4e02-bbd1-10db600c9568` |
| Definition 6.10(b) | `6af036ff-7b1e-4097-857f-af8646136021` |
| Proposition 6.11(a) | `6af036ff-e562-43f5-abdc-62d1d9d94e44` |
| Proposition 6.11(b) | `6af036ff-96e8-4f0f-b4d9-f334f6a43bd8` |
| Research endpoint theorem | `6af02ab1-2d22-4237-9680-5b2e996f025a` |
| Morrey conclusion | `6af02ab1-25e4-45e3-9111-eb65506cee4a` |

当前结构的核验状态（2026-11-08）：

- Paper 共 29 块，Full-text 内有 21 个节标题、数学陈述和证明块。默认无页面 alias、书目属性或重复书目字段块。
- Index 的当前分组是 **Published version (Current version)**，其下仅保留 Zotero item；#Comment on Version 是 Index 的另一个直接子块，保存选录范围和编号对应。当前版本不等于自动采用最新版本。
- 未导入预印本索引记录，Zotero 中也没有符合纳入条件的 MathSciNet 子记录，因此未补空来源或空分组。
- 三个整理者补加的逐结果 PDF 定位块已删除；其余数学内容、原结果编号、结果块 UUID 与研究引用保持。普通编号结果不默认添加 PDF 链接，图表、无编号／难定位段落及明确跳转需求按需保留。上面的页码表是来源核验记录，不要求抄入正文。
- 导入范围仍是 Definition 5.4、Definition 6.10、Proposition 6.11 及对应原文证明；不据此声称达到某个完整 Paper 收录等级。Research 的 Morrey 证明仍按实际状态标明提纲，架构核验不等于证明完成。
- 原文 PDF 指定页面已进行视觉核对，MCP 块结构和原生引用已读回；未观察 Logseq 公式界面渲染或操作系统打开 Zotero 的点击结果。

该实例只陈述已核实的最终布局和验证边界；历史中间布局不作为当前写入规则。
