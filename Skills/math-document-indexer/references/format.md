# Index 文档格式与仓库映射

本格式是正式 `id + Original` 数学条目的文献内预处理表示。唯一的条目标识改动是：`id` 改为连续整数 `index`，关系 target 改为整数。Original 的字段结构及 14 种类型、7 种关系保持既有设计。

```text
format: math-document-indexed
format_version: 1.0
source: document/title/authors/edition/kind/sha256/metadata_verified/synthetic/complete/processed_pages
review: status(draft|agent_checked|human_checked), actor, notes
items: [{index, Original: {indexing, content, relations}}]
reading_order: [{index, part(body|proof), optional page}]
unresolved: 未解决项，保留原文及原因
anchors: 可选的标签、物理页、源文件行定位辅助
```

`source.title` 的文件名占位及元数据均需核实后才能正式入库。`source.document` 是来源版本 URI；印刷页码放在 Original.indexing.location.page 或阅读位置的 page 中，物理 PDF 页放 anchors／证据记录中。processed_pages 记录 PDF 实际处理页，complete 明确是否覆盖整份来源。

sha256 绑定输入原文件。TeX 项目若有 input/include，准备工具还记录 inputs 文件指纹与 project_sha256（展开后文本指纹），入库计划会重新核对项目内容；缺失的包含文件留在 unresolved。元数据缺失不应冒充已核实的出版信息。

类型：statement、definition、notation、axiom、assumption、theorem、proposition、lemma、corollary、conjecture、example、remark、exercise、problem。

关系：depends_on、implies、equivalent_to、special_case_of、example_of、counterexample_to、related_to。条目为关系源，target 是目标 index；equivalent_to 和 related_to 语义对称。每条关系的 basis 为 explicit 或 inferred，可附 explanation。

阅读顺序覆盖每个 body 和每个非空 proof 各一次。一个条目的完整正文／证明字符串不可在阅读顺序中任意切片；未覆盖的复杂交错情况应保留说明，不能丢失上下文。

## 仓库交付

待导入稿保存到 `logs/submissions/<source-id>/`，属于过程材料，可版本管理但不是总库权威数据。`checks.json` 记录实际格式检查和文档自述审阅状态，不替代数学审阅。

`plan-import` 只生成首次导入计划：创建 index→UUID 映射、重写关系和阅读顺序，并调用目标仓库的 Schema 与全局一致性检查。候选 JSON 本身不改为 UUID。若 edition 为空，适配器使用明确的 `file-sha256:<指纹>` 或 `project-sha256:<指纹>` 作为来源文件版本标签，不能把它解释为出版社版次。

批次尚未 apply 时可审阅或重新生成；只应用一次并沿用已保存的批次 ID 与映射。原来源已登记时适配器拒绝重新生成身份。原文件不会自动上传到 GitHub，也不会由这一步复制进 sources/files。
