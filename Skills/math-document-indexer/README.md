# 数学文献分拆 Skill

版本：0.2.0。把数学论文／书籍的 PDF 或 LaTeX 整理为一份使用整数 `index` 的 JSON，在本地网页按原文顺序阅读并查看知识图谱，还可生成知识库待导入包。

## 安装与调用

本技能的完整目录是 `Skills/math-document-indexer/`。安装时保留 scripts、references、assets 和 requirements.txt，不要只复制 SKILL.md。可让支持技能安装的 Agent 执行：

```text
请安装 https://github.com/sinplay20/10.skill/tree/main/Skills/math-document-indexer 中的 Skill。
```

也可下载 `Skills/packages/math-document-indexer-0.2.0.zip`，将其中完整的 `math-document-indexer` 文件夹放入目标 Agent 的技能目录。Codex 的目录与发现规则见 [官方技能文档](https://learn.chatgpt.com/docs/build-skills)。本仓库保存技能源码，上传到 GitHub 不会自动在本机安装。

安装后发送：

```text
使用 $math-document-indexer 处理 <PDF 或主 TeX 文件的完整路径>。
先处理 PDF 物理页第 10—15 页，对照原文整理条目、证明和关系。
保留原文，使用 index；不确定项留在 unresolved。
生成并校验 JSON，打开阅读与知识图谱网页。结果放在独立工作目录。
```

后续可以要求 Agent 修订具体条目、更新关系，或导出仓库提交包。网页是阅读与审阅界面；点击按钮不会自行启动模型分拆 PDF。“复制 Agent 任务”用于将后续工作交回对话中的 Agent。

## 从网页上传文献

让 Agent 启动工作台：

```text
使用 $math-document-indexer 打开文献上传工作台，工作区设为 <本地工作目录>。
```

也可以在已安装依赖的环境运行：

```console
python <SKILL>/scripts/mathdoc.py view --workspace <WORK> --port 8765
```

无需预先生成 JSON。首页提供“上传数学文献”“导入条目 JSON”“本地文献库”三个入口；可点击或拖拽上传 PDF／UTF-8 TeX（最大 100 MiB），指定 PDF 物理页范围，并按需渲染页面图片。处理完成后会显示条目数与待处理项，点击“打开初稿”进入阅读与图谱。

原文件、提取材料和 JSON 保存在 `<WORK>/documents/<内部文献键>/`，文献目录保存在 `<WORK>/workspace.json`。重启时使用同一个 --workspace 即可继续；上传至本地工作台不等于提交 GitHub。文献内部条目仍使用整数 index。

阅读界面中的“复制 Agent 核对任务”会携带当前原文件、JSON 和技能路径。将任务粘贴给 Agent，核对类型、编号、公式、证明和关系。初稿保持 draft，语义核对完成后才更新审阅状态。扫描件的缺失内容不会自动补齐。

网页一次上传一份单文件 PDF／TeX。包含 input/include 的 TeX 多文件项目使用下方 CLI／Agent 本地路径流程；缺失包含文件会保留为 unresolved。网页导入 JSON 会创建独立文献记录，不会误关联此前打开的原文件。

交互参考：[CMath 数学地图工作台](https://cyw6130.github.io/CMath-math-map/) 的上传、导入 JSON 和文献库入口；本技能独立实现本地处理与既有数学条目格式。

## 依赖与手动运行

需要 Python 3.12+。在独立工作目录创建虚拟环境，然后用该环境的 Python 安装本技能 requirements.txt。示例中的 `<SKILL>` 是实际技能目录，`<WORK>` 是任务工作目录；路径含空格时加引号。

```console
python -m venv .venv
python -m pip install -r <SKILL>/requirements.txt
python <SKILL>/scripts/mathdoc.py prepare paper.pdf --out <WORK>/prepared --pages 10-15 --render
python <SKILL>/scripts/mathdoc.py draft <WORK>/prepared/evidence.json --out <WORK>/document.indexed.json
```

安装依赖前激活上述虚拟环境，或直接使用其中的 Python 可执行文件。`draft` 只生成结构草稿；随后由 Agent 对照原文整理类型、公式、编号、证明归属和关系。

```console
python <SKILL>/scripts/mathdoc.py validate <WORK>/document.indexed.json
python <SKILL>/scripts/mathdoc.py view <WORK>/document.indexed.json --source paper.pdf --port 8765
```

打开命令返回的本地 URL。服务绑定 127.0.0.1，终端中按 Ctrl+C 停止。TeX 同样使用 prepare／draft 命令；标准环境可辅助起稿，自定义宏、编号及复杂版面仍需 Agent 核对。

演示请先复制 `assets/example.indexed.json` 到独立工作目录，再用 view 打开它并用 `--source <SKILL>/assets/example.tex` 关联原文。示例是自行编写的虚构文献，含 12 个条目、10 条关系，展示第 2 页的定理与第 5 页的证明共用同一 index。

## JSON 与仓库交付

- `items` 使用 `index + Original`；14 种类型和 7 种关系见 [格式说明](references/format.md)。
- 证明附在条目中；reading_order 分别记录 body／proof 的原文位置。
- 关系依据区分 explicit（原文明确）与 inferred（分析推断）。
- [JSON Schema](references/indexed-document.schema.json) 检查格式，工具还检查索引、关系目标和阅读顺序覆盖。

```console
python <SKILL>/scripts/mathdoc.py submit <WORK>/document.indexed.json --output <WORK>/submission.zip
```

提交包含 `logs/submissions/<source-id>/document.indexed.json` 与 `checks.json`，仍使用 index，不包含原始文献。`--output <知识库根目录>` 可以写入本地待导入目录；该命令不执行 Git 提交或上传。

正式入库使用 `plan-import`：读取目标 math-knowledge-base 仓库的工具和规范，核对来源指纹，生成独立 index→UUID 映射及批次，再按目标仓库协议 apply。它不是任意仓库的通用导入器；已登记来源的修订需沿用已有 UUID。详见 [SKILL.md](SKILL.md)。

## 范围与验证

语义分拆和数学关系由 Agent 核对，不需要额外模型 API Key。PDF 文本抽取和 PNG 渲染已提供；没有内置自动数学 OCR，扫描页需要视觉阅读或另接 OCR。不确定内容保留在 unresolved；结构校验不等于数学正确性证明。

在本技能目录运行 `python -m unittest discover -s tests -v`。16 项独立测试无需外部知识库；设置 `MATHKB_TEST_REPOSITORY` 指向兼容知识库可额外运行 2 项 UUID 入库适配测试，测试仅使用临时副本。PDF 测试使用临时生成的页面。

本地网页和 KaTeX 0.16.22 公式资源随包提供，不依赖 CDN。第三方许可位于 [assets/vendor/katex/LICENSE](assets/vendor/katex/LICENSE)。
