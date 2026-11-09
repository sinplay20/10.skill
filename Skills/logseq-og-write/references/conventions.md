# 共同写作与来源规范

继承 logseq-knowledge-base 截至 2026-11-08 的已确认规则；页面类型的格式见各专用参考文件。

## English-language policy

This policy applies to Paper, Book, Research, Lecture note, Session note, Conversation note, and Topic pages.

- Use English for all note prose: generated page names, headings, round summaries, research summaries, explanations, method descriptions, comments, keywords, and descriptive property values.
- Keep English source prose verbatim where the page format requires original text. For non-English source prose being imported, provide a complete, faithful English translation and identify the affected source container or passage as `English translation of the source text`. Retain the original source record or a reliable source link, together with its actual identity, so the translation can be checked. Do not present a translation as verbatim original wording.
- The preceding translation rule is an explicit language-only exception to the original-wording requirements below. Preserve the meaning, completeness, order, paragraph and list boundaries, mathematical hypotheses, conclusions, qualifications, and uncertainty. Do not summarize, shorten, or silently correct the source while translating. Apply heading mapping after translation, retaining the source hierarchy.
- Preserve exact identifiers, URLs, source filenames and paths, proper names, official publication and lecture titles, bibliographic records, code, and mathematical notation. These source identity or literal fields are not generated prose; do not invent English replacements or translate executable content.
- When bringing an existing page into compliance, update the affected blocks in place and preserve its identity, hierarchy, metadata, citations, and unaffected source material. Read back the result and verify that all note prose is English and any retained non-English text belongs to an exact source identity, bibliographic, or literal field.

## Block references in generated prose

- Use descriptive aliases for inline block references in generated prose: `[descriptive English text](((UUID)))`. The text should name the actual definition, assumption, result, proof step or source being used, and fit the surrounding sentence.
- Retain the real target UUID. An alias changes the displayed wording, not the referenced object, its hypotheses or its dependency role. A reference to one conclusion should be labeled as that conclusion rather than the whole theorem.
- Obtain the target UUID before writing the link. On read-back, check both the stored alias syntax and the native indexed reference to that same target; preserving the visible text alone is insufficient.
- Standalone block references may retain `((UUID))` when appropriate. Faithful source transcriptions and conversation archives preserve their original reference wording unless the user requests an edited presentation. Numbered-equation and named mathematical-unit links follow the rules below while retaining the visible source reference wording.

## 数学环境的引用

- 后文引用已收录的定理、引理、命题、推论、定义、评注、例子或练习时，必须链接到对应数学环境根块，使用 `[Theorem 3.2.1](((真实结果块 UUID)))` 这样的描述性块引用，保留原文可见的环境名称、编号和标点。明确引用某一分项时可指向已存在的具体结论块，并保留分项编号和适用条件；不能拿公式块代替结果块。
- 按实际作品、版本、章节、环境类型、编号和上下文识别目标。同一来源重复编号时须核对其数学含义，不能仅按编号或就近位置自动匹配。未收录、目标不明或来源不符时保留原文字并说明，不猜造 UUID，也不自动导入其他章节来补齐引用。
- 数学环境自身的标题、编号及 `Proof of Theorem ...` 这类归属标题保留原样，不改成自引用。原文中的引用只补链接标记，不改动数学内容；保存后同时核对实际目标和 Logseq 原生 refs，保留已有公式引用及所有既有结果 UUID。

## 编号公式与引用

- 数学笔记中的每个编号公式单独成块：块正文只保留完整公式与原始 `\tag{...}`，不混入前后说明文字。一个原编号下的 `aligned`、`cases` 等完整多行环境保持同块；不同编号不合并。公式仍归属原陈述、条件、结论或证明子树，不因独立成块改变数学条件的作用范围，也不新建 Equation 标签。
- 后文引用已收录的编号公式时，使用 `[(3.18)](((真实公式块 UUID)))` 这类保留原显示编号的块引用，目标是公式本身，不是包含它的整段或定理根。先创建、读回并保存稳定的公式块身份，再写引用；跨章或跨版本编号必须核实来源。未收录且无可靠目标的公式保留原编号，不猜造 UUID，也不因引用而擅自扩大导入。
- 编号识别必须区分公式、定理／命题、章节、文献序号与公式自身的 `\tag`；不做盲目的全局数字替换。原文转录只补链接标记，保留可见引用文字及数学内容。迁移时保留既有结果、证明和段落根 UUID，将公式及后续文字拆入其逻辑子树，保护原有脚注与人工批注；核验每个编号恰有一个公式块、公式文本未变、后文引用的原生 refs 指向同一真实块。

## Zotero linkage

- Prefer an existing canonical Logseq Paper or Book page, matched to the actual work type, as the citation entry point. Search page names, aliases and identifiers, then read candidate pages to verify work identity. Use Zotero metadata and attachment records to reconcile ambiguous matches; a similar title alone is insufficient. Reuse the page shared by preprint and published versions.
- Cite an entire work through its Paper or Book page, with a short display label. When using an imported definition, proposition or individual conclusion, prefer a descriptive block alias to that exact source unit. If the Paper/Book page exists without that result, cite the page with an explicit verified locator rather than fabricating a result UUID.
- Zotero supplies library access and underlying documents. Organize Index information by ordinary version-group blocks: `Preprint version`, then `Published version`. Place each atomic `[Zotero item](...)` line and faithful index-source record under its verified version. Keep `#Comment on Version` as a direct Index child, after the version groups, never nested inside a version or Zotero entry. Do not attach a PDF/DOI subtree or duplicate version label to the Zotero line by default. Original source formats remain unchanged; per-result PDF links are optional rather than repeated by default; access links do not establish a completion level. Mark only the group actually adopted for the note as `(Current version)`; this is not necessarily the latest available version.
- Resolve library scope and item keys from real connector records. A personal-library select link uses `zotero://select/library/items/ITEMKEY`; a PDF link uses `zotero://open-pdf/library/items/ATTACHMENTKEY?page=N`. The parent work and its PDF have different keys. Group-library links require the actual group scope. Do not substitute a numeric local database item ID for an item key.
- Ordinary numbered definitions and results do not need repeated PDF-page links: the Paper page, current version, original result number and central Zotero access normally provide traceability. Add a precise PDF link only for an unnumbered passage, figure/table, ambiguous location or an explicit one-click reading need. When adding one, verify the actual attachment and distinguish printed page labels from one-based physical PDF pages. Record version/number correspondences centrally; never fabricate a locator. This optional-link rule applies to organizer-added navigation links, not original source citations, reference-list URLs, or Lecture source-page mappings.
- Generated research prose uses the short source alias and the necessary mathematical locator. Consolidate full paths, complete bibliographic records and version details in the owning source record; retain necessary provenance centrally or in a concise locator child only where useful, instead of appending a Source paragraph or PDF link to every conclusion. Source-transcription requirements still apply to original Paper text.
- A local research manuscript has its own version/material record on its Research page, distinct from the external papers it uses. Keep the file identity and source labels there; external literature cannot stand in for the provenance of a new draft result.
- If the graph lacks the Paper or source-result block, use a verified, concise external/Zotero citation as a temporary entry and record the missing import scope. Do not create an empty referenced Paper entity and present it as an imported note. Actual Paper creation follows either the explicitly selected completion level or an explicitly bounded excerpt request; an excerpt alone does not establish a completion level.
- Check native Logseq reference targets after rewriting a citation. For Zotero links, verify the correct work/attachment and page mapping; report an actual click-through test separately from a constructed and checked URI. This workflow provides explicit links and on-demand lookup, not automatic bidirectional synchronization.
