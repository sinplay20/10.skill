# Book 页

书籍写入现已纳入本规范。Index information、版本、评论、引用、数学环境、公式、按需 PDF 定位与 MCP 写入核验沿用 [Paper 规范](paper.md)；下文只规定书籍身份、选定范围及 Chapter 层级的差异。共同语言规则仍适用。

## 对象与来源

- Book 承载一本书，Paper 承载论文。优先复用用户指定或图谱中已核实的同一书籍页；新页可用真实正式书名，需要区分同名作品、卷册或版次时采用最少的已核实信息，不猜造后缀。
- 写前从实际书籍、Zotero 或原始索引核对书名、作者／编者、卷册、版次和实际文件。区分全书、选定章节与独立发表的论文；不因书中引用某篇论文就合并对象。
- 同一书籍的不同版本复用同页的版本组织；不得把不同版次的正文、页码或定理编号静默拼接。确属独立卷册或同名异书时按实际对象区分。
- 默认不设页面 alias，不增加作者／出版社链接、ISBN 等原生属性或重复本地书目字段块。原始索引中已有的出版、版次、ISBN 等信息忠实保留为原记录内容。

## 类型与页面结构

首个顶层块只有 `#Book`，不同时添加 `#Paper`，不附书目属性。类型查询使用 `{{query [[Book]]}}`。

```text
- #Book
- ## Summary
  - <Summary of the explicitly selected material, when requested>
- ## Index information
  - **Preprint version**
    - <Verified preprint source, when available>
  - **Published version (Current version)**
    - [Zotero item](<Verified item-select URI>)
    - <Verified MathSciNet record in the agreed format, when available>
  - #Comment on Version
    - <Actual edition, volume, imported scope or version correspondence> #<Verified author>
- ## Full-text
  - ### Chapter 1. <Original chapter title>
    - #### 1.1 <Original section title>
      - **1.1.1 <Original lower-level title>**
        - **<Further original heading, when present>**
          - <Source content>
- ## References
  - <Original bibliography entries in the selected scope>
```

示例只说明结构，不代表真实书籍或写入授权。Summary、References、版本组和索引来源按实际范围与材料保留，不创建空占位。

## Index information：与 Paper 一致

- 版本组依次为 Preprint version、Published version，标题整体加粗。实际正文采用的唯一版本组附 `(Current version)`；它不是“自动选择最新版”。版次、卷册及编号对应在必要处用已核实的普通文本说明。
- Zotero item 是所属版本下的一行入口，不附 PDF／DOI 子树，不重复本地完整书目字段。Zotero 保持只读。
- MathSciNet、arXiv 等原始索引记录严格沿用 Paper 的纳入条件、格式和内容边界。没有合规来源就省略；不能因用户给了结构示例而补造书评、MR 记录或空标题。
- `#Comment on Version` 是 Index 的直接子块，与版本组同级；它使用已有 Comment 标签及普通文字 caption。保留原署名，新评论按可靠实际作者／模型署名。

## Chapter 与正文层级

Chapter 用 ###，Section 用 ####；#### 以下的标题统一加粗，不定义额外的显示层级，也不删除原书的实际内容归属。

| 原书层级 | 显示标题 | 实际归属 |
|---|---|---|
| Chapter | `###` | Full-text 的直接子块，或真实 Part／卷册分组中的章节 |
| Section | `####` | 所属 Chapter 的子块 |
| Section 以下的标题 | `**原始标题**` | 只加粗，继续保留原书真实块嵌套；不再细分显示层级或追加 Markdown # |

- 保留原章、节的编号与标题；不要把每个 Chapter 新建为页面，或把章节标题变成标签。仅选择某一章或某节时，仍保留其实际 Chapter／Section 身份与定位，不将 Section 提升为 Chapter。
- 原书的 Part 或卷册不是 Chapter，可用普通分组块保留真实归属，Chapter 显示仍从 `###` 开始。前言、引言和附录等被选入的章级内容也使用 `###`，不补造章号。
- 原书的数学段落、列表、定理环境、证明和公式归属其章节。定理保留原编号及名称，共享条件与结论分为直接子块，Proof 嵌在对应结果下；引用具体结论仍须带上适用条件。
- 原书按章列出的参考文献保留其章内归属；全书统一书目在选定范围内时使用页面的 References。内容只维护一份，不在两处重复转录。

## 公式、引用与实际写入

沿用 [Full-text 公式规则](paper.md#full-text-功能单元内的内容格式)：行内 `$...$`，行间起止 `$$` 各占独立物理行，完整多行环境保持同块，保留反斜杠和原公式编号。每个编号公式独立成块，后文以保留编号的块引用指向它；前后说明与公式分开，仍属于原陈述或证明子树。块的原子边界、原生引用检查及 UUID 保护同 Paper。

行文优先引用图谱中的 Book 页或其真实结果块，采用描述性块链接。书籍原定理属于 Book；研究加工、当前记号的转换和应用属于 Research。编号在不同章节／版次重复时，通过真实章节和来源身份区分，不猜造编号。

普通编号定义、结果默认不逐条附补加的 PDF 链接；图表、无编号／难定位内容及明确跳转需求按需保留。此简化不删除原文引文、参考文献 URL 或有意义的来源定位。

## 范围与核验

- 本次只导入用户选定的章、节或整本书。明确节选无需另选完成度，也不因相关章节存在而自动导入；已经清楚的范围不重复确认。
- 复用 Paper 的完成度术语和如实报告原则，不新增 Book 状态属性。Bibliographic、Research-ready、Full-text 的完成情况必须与明确选定的对象和范围对应；一章完成不能报告为整本完成。
- Paper 默认 Full-text 的 Introduction 范围不机械套到 Book。书籍正文以本次选定章／节／整本为边界；Summary 和完整书目也按请求范围核验，不要求先总结整本才写选定章节。
- 通过 MCP 按 Chapter 小批量写入并读回类型首块、版本与范围、标题层级、数学内容和引用。保留已有 UUID 与人工批注；超时先读回。来源缺页、图示未能保留或整本导入尚未结束时说明实际覆盖。
- 结构读回、PDF 原文视觉核对、Logseq 渲染、数学证明核验与阅读器点击跳转分别报告。本 skill 的更新本身不代表已经实际写入一本书。
