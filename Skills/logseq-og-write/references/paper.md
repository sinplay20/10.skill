## Paper 页

### 用途与对象身份

承载数学论文的索引信息和内容的笔记页面，包括已发表并被数据库收录的期刊论文、预印本和会议论文。

一篇论文对应唯一页面，包括其版本的持续演化，如

- 预印本发表后更新名称和元数据；不因版本或发表状态另建重复页面。

页面由三类信息组成：书目元数据（通过原始索引记录或 Zotero 核实）、原始信息（包括索引信息、论文原文、原始参考文献等），以及加工后的信息（包括结构化总结、评论等）。

### 页面名称

| 作品状态 | 名称格式 |
|---|---|
| 期刊论文 | `A. Author, B. Author; J. Abbrev.; 2024` |
| 未正式发表的预印本 | `A. Author, B. Author; arXiv:2403.12345` |
| 会议论文 | `A. Author, B. Author; Conference Abbrev.; 2024` |

- 按原始顺序列出所有作者，使用名字首字母与姓氏，不使用 `et al.`。
- 作者之间使用 `, `，身份字段之间使用 `; `，名称末尾不加句点。
- 论文正式标题通过已核实的原始索引记录或 Zotero 条目保留和核对；默认不创建页面 alias 或重复的本地标题字段。
- 期刊缩写使用有依据的正式缩写，不猜造；没有可确认缩写时另行确定。
- 会议没有通行缩写时，按既有约定使用会议地点。
- 名称冲突时在年份后添加 `a`、`b` 等后缀，依次根据发表次序、期号、首页或文章编号、标题判定。

### Paper marker and bibliographic text

Default Paper pages have no native page alias and no bibliographic properties. The first top-level block contains only `#Paper`. Verify the complete title, authors, publication and version against original index records or Zotero; do not automatically transcribe them into an additional local bibliography or field list.

```text
- #Paper
- ## Index information
  - **Preprint version**
    - <Verified preprint access or original arXiv record>
  - **Published version (Current version)**
    - [Zotero item](<Verified item-select URI>)
    - <Verified MathSciNet record, when available>
  - #Comment on Version
    - <Version correspondence or selected-import scope> #<Verified author>
```

- Mark the group supplying the current main text as `Preprint version (Current version)` or `Published version (Current version)`. Only one group per Paper carries `(Current version)`; it denotes the version actually adopted for the note, not merely the latest available version. The suffix is ordinary text, not a new tag or property.
- Version groups are ordinary blocks, in Preprint version / Published version order. Bold the entire group label, including `(Current version)` when present: `**Published version (Current version)**`. Place each verified access link and original index record under the version it actually describes. Omit unavailable records and unpopulated groups in actual imports, unless the user explicitly asks for an empty structure preview; never invent a MathSciNet record. Do not infer version identity from a filename alone.
- Reuse complete bibliographic information already supplied by a faithful MathSciNet/arXiv record or the linked Zotero item. Do not add an independently assembled title/Authors/Journal/Year/Volume block unless explicitly requested.
- When ordinary bibliographic text is actually needed, keep it as text, without author/journal page references or `authors::`, `journal::`, `year::`, `volume::`, `title::` and `alias::` properties. Preserve original index-source wording and formatting requirements.
- `#Comment on Version` is a `#Comment` tag followed by the plain caption `on Version`, not a new tag or Markdown heading. It is a direct child of Index information and a sibling of Preprint version and Published version, after those groups. It is not a child of a version or Zotero item. Its children hold version correspondence, source-selection scope or other actual version comments, each with a reliable author signature.
- Keep `#Paper` as the type marker without `tags:: Paper`; do not create a page-properties pre-block merely to store a title.
- A page alias is optional only for an explicitly requested alternate name. Verify its native relationship if used. This does not change descriptive inline block aliases such as `[result](((UUID)))`.
- During migration, preserve source identity through verified index records or a Zotero entry before removing redundant local metadata and alias properties. Keep the canonical page, mathematical result UUIDs and their citations.
- Do not add routine PDF-page link children to numbered definitions or results. Keep optional PDF locators when they help identify a figure, unnumbered passage, ambiguous source location or explicitly requested one-click target. Removing redundant links must preserve mathematical content, original result numbers, central source access and necessary exceptional locators.

### Querying Paper notes

Keep the block-reference query:

```text
{{query [[Paper]]}}
```

This finds the type-marker blocks and their containing pages. `(page-tags Paper)` is not equivalent; do not add a page tag to change the convention. After migration, verify the unique `#Paper` marker and its native indexed tag reference.

Year and other bibliographic fields are ordinary text. Previous filters such as `(and [[Paper]] (property year 2024))` are not supported by the default format. If structured bibliographic filtering is later needed, design it explicitly rather than silently recreating properties to make an old query pass.

### 顶层结构

存在时，按下列顺序排列：

```text
- #Paper
- ## Summary
- ## Index information
  - **Preprint version**
    - <Verified preprint sources>
  - **Published version (Current version)**
    - [Zotero item](<Verified item-select URI>)
    - <Verified published index-source records>
  - #Comment on Version
    - <Version and import-scope notes with author signatures>
- ## Full-text
- ## References
```

根据完成度保留相应部分，不保留空的可选章节，同名章节不重复建立。

Index information 先按 Preprint version、Published version 分组，各版本下放对应 Zotero 入口和索引来源。版本、编号对应和选录范围说明放在最后的 `#Comment on Version`，与版本分组同级，不嵌在 Published version 内。其他编辑评论仍位于 Full-text 之外。

### Summary

Summary 是研究理解，按以下顺序组织：

```text
- ## Summary
  - ### Research problem
    - **Setting.** <数学背景与对象>
    - **Problem.** <中心问题>
    - **Gap.** <已有工作的局限；可省略>
  - ### Main results
    - #Theorem <Original number and name, when present>
      - <Shared hypotheses in their source wording>
      - (a) <First conclusion with its case-specific conditions>
      - (b) <Second conclusion with its case-specific conditions, if present>
    - <Other Introduction results, retained completely>
  - ### Main ingredients
    - <关键技术输入或中间机制>
  - ### Main methods
    - <方法名称，或指向已确认方法页的引用>
      - **Source.** <来源或本文原创部分>
      - **Role.** <该方法在本文中的作用>
      - **Dependencies.**
        - <依赖条件或工具>
      - **Mechanism.**
        - <实现机制或步骤>
      - **Used for.** <用于获得哪些结果>
  - ### Key words
    - [[规范化概念一]]
    - [[规范化概念二]]
```

各部分的内容要求：

| 部分 | 要求 |
|---|---|
| Research problem | `Setting`、`Problem` 必需，`Gap` 可选。 |
| Main results | 覆盖完整 Introduction 中陈述的本文全部结果，包括次要、补充、重叠、特殊情形与无编号结果；保留编号、名称、条件和结论。不含证明。 |
| Main ingredients | 提炼驱动主要结果的技术输入与中间机制，不把其他结论简单改称为 ingredients。完整条目至少一项。 |
| Main methods | 每个方法包含示例中的五个字段。区分继承方法和本文扩展；本文原创时明确说明。完整方法至少一项。 |
| Key words | 每项为一个普通页面引用，不使用标签或附加解释。约 3–8 项作为指引，聚焦主要对象与结果层面的性质。 |

- Main results 不把背景文献的结论当作本文结果，不为无编号陈述补造编号。
- 不因结果次要、重叠或属于特例而省略其独立陈述；只被提及而未在引言中陈述的后文结果不自动补录。
- 未获取完整引言或未核实结果覆盖时，不宣称 Summary 已完整。
- 方法来源仅链接能够可靠匹配的页面；已有方法页未确认时保留名称，不为填充字段创造页面。
- 证明工具与技术输入保留在 Main ingredients、Main methods 或正文中，不因使用过就列为 Key words。
- 评论采用 tags.md 中已经确认的 `#Comment` 结构。

### Theorem block structure

Apply this structure to every `#Theorem` in Paper `Summary > Main results` and `Full-text`:

- Keep the theorem tag, original number, and source name on the result root.
- Put the shared hypotheses in one or more direct child blocks, followed by separate direct child blocks for the conclusions. Never combine the shared hypotheses and a conclusion in one child block, or nest the conclusions under the hypothesis block.
- Give each source-labeled conclusion, such as (a)–(d), its own direct child block. Preserve the original labels and order; do not invent labels for an unnumbered or unlettered statement.
- Keep additional case-specific assumptions attached to the conclusion they qualify. For example, convexity required only for part (d) must not become a shared hypothesis for (a)–(c). Preserve all mathematical conditions, inequalities, spaces, constants, endpoint qualifications, and formulas without changing the theorem's meaning.
- An additional unlettered conclusion must also be separate from the shared hypotheses. Do not turn a result established elsewhere into an extra assumption merely because it was placed in the same paragraph.
- Only change block boundaries and necessary presentation; preserve existing root UUIDs and reuse affected child UUIDs where possible. Preserve already compliant parts and unrelated manual edits. Keep each complete display formula intact in its associated conclusion subtree; a numbered display occupies its own formula-only block.
- `Summary > Main results` contains no proof. In `Full-text`, a source-associated `#Proof` remains under the theorem root after its statement, as specified in tags.md.

### Index information

本节复用原始索引记录和 Zotero 已提供的书目信息，不默认另建手工拼装的完整标题／作者／期刊／年份／卷号块。入口和索引记录按 Preprint version / Published version 分组，Zotero item 在相应版本下保留一行；`#Comment on Version` 与版本分组同级。以下 MathSciNet、arXiv 等来源仍严格按既定格式保存，不能因入口简化而删除原始索引记录或用访问链接冒充记录。

Save the source records with their wording, punctuation, capitalization, order, and meaningful multiline structure. For MathSciNet, apply only the explicit presentation exceptions below: omit the repeated leading MR header from the bibliography child, bold the paper title, and separate reviewer identity from review text. Zotero identifies the work and helps discover sources; it is not a source heading in this section.

本节可以保留简短的 Zotero 条目访问入口；它与后面的原始索引来源条目分工不同。未取得符合既定格式的真实索引记录时，不将 PDF 首页信息自行拼成 Publisher 索引条目，也不以 Zotero 父条目的 MR 字段补造 MathSciNet 来源。

已有两种确定的来源结构：

```text
- ## Index information
  - **Preprint version**
    - [arXiv: <编号>](<不带版本号的 arXiv 摘要 URL>)
      - [<原始提交／修订说明>]
        **<原标题>**
        <按来源顺序排列的作者>
      - Abstract
        - <当前版本的完整摘要>
      - Subjects: <原始学科分类>
      - Submission history
        - From: <提交者> [view email]
        - [v1](<对应版本的摘要 URL>) <完整时间戳> (<文件大小>)
        - <其他版本，按来源顺序>
  - **Published version (Current version)**
    - [Zotero item](<Verified item-select URI>)
    - MathSciNet: [MR<Identifier>](<MathSciNet record URL>)
      - <Source authors and affiliations>
        **<Official paper title including its terminal punctuation>** <Source language note, if present>
        <Remaining source publication details>
      - Classifications
        - <Source classification text>
      - Review
        - *Reviewer: [[Reviewer One]], [[Reviewer Two]]*
        - <One complete review text>
```

MathSciNet：

- 仅在 Zotero 子笔记明确证明其收录，或直接子快照来自 MathSciNet 文章 URL 且包含可读、匹配的 MR 记录时纳入。父条目元数据只能佐证。
- 未满足上述条件时完全省略该来源，不建立空标题。
- Keep the MR identifier and its link on the MathSciNet source root. The first bibliography child is one multiline block containing the rest of the source record, without the leading MR header line, such as `MR2253739 (2007d:35078)`. Omit that whole repeated header line, but retain authors, affiliations, title, language note, publication details, and other bibliographic content. Do not remove MR references occurring elsewhere in the source text.
- Bold the complete paper title, including its final period or other terminal punctuation. Keep the source language note outside bold, for example: `**Regularity of radial minimizers and extremal solutions of semilinear elliptic equations.** (English summary)`. Do not invent a language note absent from the source.
- Under `Review`, put the reviewer identity and the complete review text in two separate direct child blocks, at the same level and in that order. The complete review text remains a single multiline block, not a child of the Reviewer block and not merged into it. Keep the singular label `Reviewer:` even for joint reviewers, and represent reviewer names as page references. For multiple independent reviews, retain each reviewer/text pair in source order without combining their bodies.
- Completely omit unavailable Classifications or Review sections. When a page already has the correct Reviewer/text sibling structure, retain it rather than inserting duplicates.
- Corrigendum 的结构尚未定义，遇到时另行确认，不自行处理。

arXiv：

- 写入前在线查询编号所对应的 arXiv 记录，不能以 Zotero 元数据代替来源原文。
- 来源根使用不带版本号的摘要链接，不另加泛称 `arXiv` 标题。
- 根下恰有四个直接子块：提交／标题／作者多行块、Abstract、Subjects、Submission history。
- 完整摘要放在 Abstract 下的一个子块中；版本历史保留所有版本、对应链接、完整时间戳及文件大小。
- 保留显示的提交者行，不复制或解码邮箱地址。
- 不添加 `Cite as`、arXiv 分配的 DOI、Zotero key 或作者搜索链接等未约定字段。

版本分组顺序为 Preprint version、Published version，最后放 #Comment on Version。各版本下可先放一行 Zotero 入口，再按 MathSciNet、zbMATH、arXiv、Publisher、其他排列实际可用的原始索引来源；后几类来源的具体格式仍未确定，不因列出顺序而自行创建。来源和版本必须匹配；缺失来源或没有已导入来源的版本分组不留空标题。展开首个可用来源，折叠后续来源。

### Full-text

默认保存当前主版本的完整 Introduction 原文，不等于整篇文章。

- 用户已选定当前版本时，以该版本为准，不因另有更新版或正式版而静默切换。未指定时，默认来源优先级为正式发表版、最新 arXiv 版、其他完整作者版或出版方版本。Current version 标记必须对应实际正文来源。
- 保留章节、段落、数学环境、公式及编号、引文标记和有意义的脚注。
- 不在本节另加 Source 子块，来源记录归入 Index information。
- 默认不导入 Introduction 之后的章节、图和表；参考文献单独放在 References。
- 来源没有明确的 Introduction 时，先明确开篇内容的范围。
- 用户明确选定 Introduction 之外的定义、结果或章节时，按指定节选范围导入；明确要求整篇时才导入整篇。上述范围选择不产生新的完成度等级，也不自动扩展到未选定内容。

#### Full-text 功能单元内的内容格式

- 原文的节标题作为根块，其内容与子节按实际层级嵌套；保留段落边界。
- `## Full-text` 下的原文章节使用 `###` 标题，其子节依次使用更深层级；保留原章节编号与名称。标题层级和实际块的父子层级应同时正确，不能仅用普通段落充当节标题。
- 行内公式使用 `$...$`。行间公式的起止 `$$` 各占独立物理行；同块中与前后正文用空行分隔。 有编号的公式必须单独成块，后续编号引用指向该公式块；按共同规则中的“编号公式与引用”执行。
- 保留反斜杠、原始公式编号和多行环境。过宽公式可用来源相容的 `aligned`、`gathered` 等环境换行；`\tag{...}` 放在内部环境结束之后、闭合 `$$` 之前。
- Keep the mathematical environment tag, original number, and name on one root. For `#Theorem`, shared hypotheses and conclusions must be distinct direct child blocks, with each source-labeled conclusion separate; apply the Theorem block structure above. A source-associated `#Proof` is nested under the result it proves.
- 定义、评注与例子按内容组织子块；不补造来源没有的编号、名称或结论分句。
- 每次公式写入后读回原始内容，检查分隔符物理行、环境配对、LaTeX 换行以及本转录内容树中的编号唯一性；可访问界面时再核验渲染。


### References

保存论文完整原始参考文献，每条为一个直接子项，保留编号、顺序、作者拼写、完整引文、DOI、URL 和标识。

可靠匹配到已有页面时，保留原始引文作为显示文字：

```text
- ## References
  - [<编号>] [<完整原始引文>]([[已有规范页面名]])
```

没有可靠匹配时，保留普通原始引文：

```text
- ## References
  - [<编号>] <完整原始引文>
```

不因列入参考文献就自动创建每个被引作品的页面，不为匹配规范页名而改写显示的原始引文。

### 内容完成度

| 等级 | 最低要求 |
|---|---|
| Bibliographic | 合规名称、已核实的作品身份，以及至少一个按既定格式保存的原始索引记录；完整书目信息随该记录保留，不另抄重复字段块。 |
| Research-ready | 包含 Bibliographic，并有完整 Summary。 |
| Full-text | 包含 Research-ready，并有完整 Introduction 原文及完整 References。 |

等级累积，不另存为状态属性。完整收录时由用户明确选择等级；用户已明确限定定义、命题或章节等节选范围时按该范围执行，不强迫选择或扩展为某个等级。既有页面的局部修正不要求重新选择等级。版本和节选范围记在 Index information 下的 #Comment on Version；未满足最低要求时不宣称达到 Bibliographic、Research-ready 或 Full-text。较低等级或节选操作不授权删除其他既有内容。
