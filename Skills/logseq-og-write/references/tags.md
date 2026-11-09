# 标签约定

## 适用范围

适用于本知识库的 Logseq OG Markdown 文件图谱。继承截至 2026-11-08 的既有标签约定；页面属性与完整功能单元按 [Paper](paper.md)、[Book](book.md)、[Research／Topic](research-topic.md)、[Lecture](lecture.md) 与 [Session](sessions.md) 分别规定。`#Research`、`#Problem`、`#Assumption` 已纳入；保留已有 `#Conjecture` 及其他已确认约定。

示例中的占位文字用于说明格式，不代表真实来源。本文不授权写入或修改现有图谱内容。

## 页面类型标记

Page types are represented by inline tags on the first top-level body block. Paper and Book pages default to a property-free `#Paper` or `#Book` marker respectively, with no native alias pre-block. This is a knowledge-base convention for OG Markdown graphs, rather than a DB-native type or property-inheritance mechanism.

OG 查询可能因路径引用返回类型根块及其后代。判定块类型时检查块自身的标签；子块出现在查询结果中不表示它具有相同类型，也不表示数学条件继承。

| 标签 | 使用位置 | 含义 |
|---|---|---|
| `#Paper` | First top-level type-marker block | 数学论文的索引与内容笔记，具体收录范围见对应页面参考文件。 |
| `#Book` | First top-level type-marker block | 一本书的索引与选定内容笔记；Chapter 层级和范围见 Book 规范。 |
| `#Lecture-note`（试用） | Lecture note 页的首个顶层元数据块 | 一次讲座的选定课件内容与明确要求补入的听讲笔记。 |
| `#Session-note` | Session note 页的首个顶层元数据块 | 一个真实会话中明确选定轮次的原始问答记录。 |
| `#Conversation-note`（试用） | Conversation note 页的首个顶层元数据块 | ChatGPT 对话中明确选定轮次的原始问答记录。 |
| `#Topic` | Topic 页的首个顶层元数据块 | 含义相对稳定并重复出现的数学名词笔记；该元数据块不附加任何属性。 |
| `#Research` | Research 页的首个顶层块 | 围绕明确数学问题组织目标、论证、结果及缺口；该类型块不附加属性。 |

### `#Paper`

The first top-level block contains only `#Paper`; source access is concise:

```text
- #Paper
- ## Index information
  - **Preprint version**
    - <Verified preprint access or original arXiv record>
  - **Published version (Current version)**
    - [Zotero item](<Verified item-select URI>)
    - <Verified MathSciNet record, when available>
  - #Comment on Version
    - <Version comment> #<Verified author>
```

- Preserve the exact spelling `#Paper` and `{{query [[Paper]]}}`.
- Do not automatically add a local bibliography/field list, native bibliographic properties, linked author/journal values, `tags:: Paper` or an alias pre-block. Verify metadata against original index records or the linked Zotero item.
- Preprint and published versions share one Paper page. Identify the version actually imported and preserve original index-source formats. PDF-page links are optional; do not repeat them for ordinary numbered results.
- `#Comment on Version` uses the existing Comment tag with an ordinary caption. Do not introduce a separate Version page/type to express it.
- Descriptive block aliases remain citation presentation; a native page alias is a separate optional feature.

- 当前主版本的分组标题附 `(Current version)`；同页仅一组。它是普通文字，不新增标签或属性。示例采用正式版为当前版本，实际以笔记正文来源为准。

### `#Book`

```text
- #Book
```

- 首个顶层块只放 #Book，不同时使用 #Paper，不附书目属性或默认 alias。
- Index information、版本评论、数学环境和公式沿用 Paper；完整规则见 [book.md](book.md)。
- Full-text 下 Chapter 使用 ###，Section 使用 ####；#### 以下的标题只加粗，保留真实块嵌套，不再建立更深的 Markdown 标题显示层级。
- 类型查询使用 `{{query [[Book]]}}`；书籍的相关概念和当前研究仍分别归属 Topic／Research。

### `#Session-note`

首个顶层块采用以下结构：

```text
- #Session-note
  session-id:: <真实会话 ID>
```

- 保留准确拼写 `#Session-note`。
- `session-id` 必须是真实来源会话的 ID，并附属于同一个类型标记块。
- 不将 ID 放在独立属性前置块中，也不增加冗余的 `tags::` 属性。
- 不能仅凭页面标题或正文中出现标签、会话 ID 就认定它是对应的归档页；需要核对首块的标签及匹配的 `session-id`。

### `#Conversation-note`（试用）

用于 ChatGPT Desktop 来源，首块格式为：

```text
- #Conversation-note
  conversation-id:: <实际取得的对话 ID>
  conversation-url:: <实际取得的原始对话链接>
```

- 保留准确拼写 `#Conversation-note`，不与 Pi 来源的 `#Session-note` 混用。
- 身份属性附属于同一个首块，不增加冗余的 `tags::`。
- 仅保留能核实的属性值，缺失时省略；完整身份要求见对应页面参考文件。
- 这是本知识库的试用标签与属性约定，不表示 ChatGPT 原生提供这些 Logseq 字段。

### `#Lecture-note`（试用）

```text
- #Lecture-note
  speakers:: [[Speaker]]
  date:: <YYYY-MM-DD>
  event:: [[Event or seminar series]]
  source:: <Actual source link or exact source filename>
```

- 保留准确拼写 `#Lecture-note`，每页只用一个类型首块；元数据均附属于该块，不增加冗余的 `tags::`。
- `source` 记录实际使用的课件；讲者、日期与活动仅记录已核实值，未知时省略。来源身份和属性规则见 [lecture.md](lecture.md)。
- 课件帧标题是随后直接排列的普通顶层块，`source-pages` 附属于各帧；不将帧标题转成页面类型标签。
- 课件内明确标识的数学环境沿用下方数学环境标签；额外听讲笔记或解释沿用 `#Comment` 与署名规则。

### `#Topic`

Topic 页的首个顶层元数据块为：

```text
- #Topic
```

- 保留准确拼写 `#Topic`。
- 该块正文只有 `#Topic`，不附加任何属性。

### `#Research`

```text
- #Research
```

- 保留准确拼写 `#Research`；一个研究页只有一个页面类型标记块。
- 首块正文只有该标签。正文、来源、结果与依赖按 research-topic.md 的 Research 约定组织。
- 该标签不声明原创性、证明完成或核验通过。

## 数学环境标签

下列标签放在相应内容块的开头：

| 标签 | 含义 |
|---|---|
| `#Theorem` | 定理 |
| `#Lemma` | 引理 |
| `#Proposition` | 命题 |
| `#Corollary` | 推论 |
| `#Conjecture` | 猜想 |
| `#Definition` | 定义 |
| `#Remark` | 评注 |
| `#Example` | 例子 |
| `#Exercise` | 练习；保留来源编号和完整题目子树 |
| `#Proof` | 证明 |
| `#Problem` | 可独立跟踪的数学问题；可关联背景、已知结果、尝试、障碍和进展 |
| `#Assumption` | 需要独立引用、比较或复用的假设或条件组 |

使用规则：

- 使用表中的准确拼写与大小写。
- 标签、来源中的编号及名称保留在同一个块中；没有编号或名称时不补造。
- 来源中的 Exercise 使用 `#Exercise <原编号>` 作为练习根，条件、分项和公式放在其子树中；保留既有 UUID 与章节／证明内的真实位置，不把练习改成待办或已证明结论。
- 后文引用已收录数学环境时采用真实块引用；目标辨认、重复编号和原文显示方式见 [数学环境的引用](conventions.md#数学环境的引用)。
- 当来源明确证明与结果的对应关系时，`#Proof` 块嵌套在它所证明的结果块下。
- Paper／Book 的 `Summary > Main results` 不包含 `#Proof`。
- For every Paper or Book `#Theorem`, shared hypotheses and conclusions must be separate direct children of the theorem root. Keep each original lettered conclusion in its own sibling block, preserving its label, order, mathematical content, and any additional conditions specific to that part. Do not combine assumptions and conclusions in one child or make conclusions children of the assumptions. Apply the [Theorem block structure](paper.md#theorem-block-structure) in both Summary and Full-text.

格式示例：

```text
- #Theorem <Original number> <Original name>
  - <Shared hypotheses only, in their source wording>
  - (a) <First conclusion, including conditions specific to this part>
  - (b) <Second conclusion, including conditions specific to this part>
  - #Proof
    - <Source proof content; Full-text only>
```

Retain only source-supported parts. The (a) and (b) labels illustrate an already lettered source; do not add labels to an unlettered theorem. The required distinction is between the hypothesis blocks and the conclusion blocks, not a new prose label. Include a source-associated proof only where the page format permits it; Summary contains no proof.

### Problem、Conjecture 与 Assumption

- `#Problem` 提出待解决的数学问题；`#Conjecture` 表达预期成立、具有明确条件和结论的命题。一个问题可以关联多个猜想，不强制为每个问题生成猜想。
- 核验或编辑进度不自动转成待办块；必要的证明与核验限制用普通文字记录。默认不添加 `TODO`、`DOING`、`LATER` 等任务标记，不据此新增 `#Claim` 或自动改变数学环境。
- `#Assumption` 的条件完整保存在其子树中。其他研究结果在假设部分引用它；父子位置不产生条件继承。普通局部假设可直接写在结果中，不逐条强制标记。
- 对 Research 中采用的假设，保留真实编号与数学条件，默认不逐条添加重复 Source 子块或稿件路径；来源与标签对应集中记录。使用处可显示为 `Assumption (F0)` 等简短块别名。外部文献特有的假设按需要附简短文献或原始定义引用。
- 新标签用于整理研究知识；Paper／Book 原文仍保留原环境、原条件和原编号，不为统一内部模型而改写来源对象。

## 评论与署名标签

`#Comment` 标记评论容器，采用以下结构：

```text
- #Comment
  - <评论内容> #<生成者或作者>
```

- 普通评论容器的父块正文只有 `#Comment`。版本评论使用用户确认的标题 `#Comment on Version`；其中只有 Comment 是标签，on Version 是普通标题文字。
- 沿用单数 `#Comment`，不另建 `#Comments` 作为同义类型。整理者关于收录范围、转述性质、证明提纲或核验限制的编辑性说明属于评论；定理条件、结论及原文数学评注按各自身份保留。
- Paper／Book 的 Preprint version、Published version 与 #Comment on Version 均为 Index information 的直接子块；Zotero、MathSciNet 等来源位于对应版本下。版本评论与版本分组同级，其他编辑评论仍在 Full-text 外；Research 评论仍可附在对应结果下。
- 每个评论子块以其生成者或作者标签结尾。
- 实际生成模型可核实时，优先使用对应模型署名，例如 `#GPT-6.1-Sol`；无法核实时保留可靠的工具或代理署名，例如 `#Codex`。不能用当前模型猜填历史评论的生成模型。仅搬运或调整结构时保留原始署名，实质改写按实际贡献记录。
- 署名标签只归属于对应评论子块，不表示页面或数学对象的类型。
- 不使用 `generator::` 属性，也不在评论以外的生成内容上仅为标注生成来源而附加作者或生成者标签。
- 署名按每条评论的可核实来源确定，不把某个模型名设为所有未来评论的固定默认值。

## 标签与其他表示方式的边界

- Paper 的 `Summary > Key words` 使用普通页面引用 `[[概念名]]`，不用标签代替。
- Paper／Book 书目信息优先复用原始索引记录或链接的 Zotero 条目，不默认另抄字段块；需要保存的文字保持普通文本，不创建作者／期刊页面引用、标签或原生属性。
- `Bibliographic`、`Research-ready`、`Full-text` 是 Paper 的内容完成要求，不新增相应标签或仅为记录完成度而新增状态属性；这些完成度也不套用于 Lecture note、Session note 或 Conversation note。
- 原始会话归档保留问题和回答中的原始标签文本；不能为了套用本文件而改写归档原文。
- `Proof structure`、`Sources` 等是普通栏目；应用、记号和计算先使用普通子树。`#Notation`、`#Application`、`#Computation`、`#Question`、`#Claim` 尚未纳入本版类型。

## 尚待设计

- 研究者、学术期刊和可复用方法的页面类型规范尚未确定。既有材料提及的 `#researcher`、`#Academic-Journal`、`#Method` 不作为本阶段已经确定的标签方案，也不直接套用 Paper 首块结构。

## 约定来源

继承 logseq-knowledge-base 截至 2026-11-08 的已确认标签约定，并纳入 Morrey／Garofalo–Rotz 试写确认的 Assumption、评论位置和署名规则。全部运行规范随本包提供，无需读取原规范的历史工作目录。

