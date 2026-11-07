"""Local index-based mathematical document workflow. Python 3.12+."""
from __future__ import annotations

import argparse
import copy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
import mimetypes
from pathlib import Path
import re
import sys
import tempfile
import os
from urllib.parse import urlparse, unquote
import uuid
import zipfile

from jsonschema import Draft202012Validator

SKILL = Path(__file__).resolve().parents[1]
SCHEMA = SKILL / "references/indexed-document.schema.json"
TYPES = ("statement", "definition", "notation", "axiom", "assumption", "theorem", "proposition", "lemma", "corollary", "conjecture", "example", "remark", "exercise", "problem")
RELATIONS = ("depends_on", "implies", "equivalent_to", "special_case_of", "example_of", "counterexample_to", "related_to")
RESULTS = {"theorem", "proposition", "lemma", "corollary", "conjecture"}


class DocumentError(Exception):
    pass


def dumps(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def loads(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise DocumentError(f"重复 JSON 字段：{key}")
            result[key] = value
        return result
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(DocumentError(f"非法数值：{x}")))
    except (ValueError, UnicodeError) as error:
        raise DocumentError(f"JSON 无效：{error}") from error


def read(path):
    return loads(Path(path).read_text(encoding="utf-8"))


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".mathdoc-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(doc, ready=False):
    validator = Draft202012Validator(read(SCHEMA))
    errors = sorted(validator.iter_errors(doc), key=lambda e: str(list(e.absolute_path)))
    if errors:
        error = errors[0]
        raise DocumentError(f"格式错误 {list(error.absolute_path)}：{error.message}")
    items = {item["index"]: item for item in doc["items"]}
    if len(items) != len(doc["items"]) or set(items) != set(range(1, len(items) + 1)):
        raise DocumentError("index 必须唯一，并连续编号为 1..N")
    source = doc["source"]["document"]
    expected, seen, body_order, edge_count = set(), set(), [], 0
    for index, item in items.items():
        original = item["Original"]
        if original["indexing"]["location"]["document"] != source:
            raise DocumentError(f"条目 {index} 的来源与 source.document 不一致")
        if not original["content"]["body"].strip():
            raise DocumentError(f"条目 {index} 的正文为空")
        expected.add((index, "body"))
        if original["content"]["proof"]:
            expected.add((index, "proof"))
        unique = set()
        for relation in original["relations"]:
            target = relation["target"]
            if target not in items:
                raise DocumentError(f"条目 {index} 指向不存在的 index {target}")
            key = (relation["type"], target, relation["basis"])
            if key in unique:
                raise DocumentError(f"条目 {index} 含重复关系")
            unique.add(key)
            edge_count += 1
    for entry in doc["reading_order"]:
        key = (entry["index"], entry["part"])
        if key in seen or key not in expected:
            raise DocumentError(f"阅读顺序重复、指向空证明或缺失条目：{key}")
        seen.add(key)
        if entry["part"] == "body":
            body_order.append(entry["index"])
    if seen != expected:
        raise DocumentError(f"阅读顺序未覆盖全部正文与非空证明：{sorted(expected - seen)}")
    if body_order != list(range(1, len(items) + 1)):
        raise DocumentError("index 应按正文首次出现的原文顺序编号")
    if ready and (doc["review"]["status"] == "draft" or doc["unresolved"]):
        raise DocumentError("正式入库前需完成 Agent／人工核对，并处理 unresolved")
    if ready and not items:
        raise DocumentError("没有可入库的数学条目")
    return {"valid": True, "items": len(items), "relations": edge_count, "reading_parts": len(seen), "review_status": doc["review"]["status"], "unresolved": len(doc["unresolved"]), "mathematical_verification": "not_performed"}


def item(index, source, kind, body, identifier=""):
    return {"index": index, "Original": {"indexing": {"location": {"document": source}, "identifier": identifier}, "content": {"type": kind, "body": body, "proof": ""}, "relations": []}}


def blank(source):
    return {"format": "math-document-indexed", "format_version": "1.0", "source": source,
            "review": {"status": "draft", "actor": "structural-parser", "notes": ["结构草稿：需 Agent 对照原文核对类型、编号、证明归属及关系。"]},
            "items": [], "reading_order": [], "unresolved": [], "anchors": []}


def selected_pages(spec, total):
    if not spec:
        return list(range(1, total + 1))
    result = set()
    for part in spec.split(","):
        limits = part.strip().split("-")
        start, end = (int(limits[0]), int(limits[-1]))
        if len(limits) > 2 or start < 1 or end < start or end > total:
            raise DocumentError("页码范围超出 PDF 或格式无效")
        result.update(range(start, end + 1))
    return sorted(result)


def expand_tex(path, root=None, stack=(), visited=None):
    path = Path(path).resolve()
    root = path.parent if root is None else root
    if not path.is_relative_to(root):
        raise DocumentError("TeX 引用超出所选项目目录")
    if path in stack:
        raise DocumentError("TeX input/include 存在循环")
    visited = {} if visited is None else visited
    visited[path.relative_to(root).as_posix()] = sha(path)
    text = path.read_text(encoding="utf-8-sig")
    def include(match):
        line_prefix = text[text.rfind("\n", 0, match.start()) + 1:match.start()]
        if re.search(r"(?<!\\)%", line_prefix):
            return match.group(0)
        candidate = (path.parent / match.group(1)).with_suffix(".tex") if not Path(match.group(1)).suffix else path.parent / match.group(1)
        if not candidate.is_file():
            return match.group(0)
        return "\n" + expand_tex(candidate, root, (*stack, path), visited) + "\n"
    return re.sub(r"\\(?:input|include)\s*\{([^{}]+)\}", include, text)


def prepare(path, output, pages=None, render=False):
    path = Path(path).resolve()
    output = Path(output).resolve()
    if not path.is_file() or path.suffix.lower() not in (".pdf", ".tex"):
        raise DocumentError("输入必须是已存在的 .pdf 或 .tex 文件")
    metadata = {"document": "sources/files/" + path.name, "title": path.stem, "authors": [], "edition": "", "kind": "latex" if path.suffix.lower() == ".tex" else "text_pdf", "sha256": sha(path), "metadata_verified": False, "synthetic": False, "complete": True, "processed_pages": []}
    evidence = {"source": metadata, "local_path": str(path), "pages": [], "notes": []}
    if metadata["kind"] == "latex":
        inputs = {}
        text = expand_tex(path, visited=inputs)
        metadata["project_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        metadata["inputs"] = [{"path": relative, "sha256": fingerprint} for relative, fingerprint in sorted(inputs.items())]
        active_text = re.sub(r"(?<!\\)%[^\n]*", "", text)
        missing = re.findall(r"\\(?:input|include)\s*\{([^{}]+)\}", active_text)
        evidence["missing_includes"] = missing
        if missing:
            metadata["complete"] = False
        atomic(output / "source.tex", text.encode("utf-8"))
        evidence["notes"].append("TeX 仅作文本展开，不执行编译命令；需要人工核对宏、计数器及印刷编号。")
    else:
        from pypdf import PdfReader
        reader = PdfReader(path)
        choices = selected_pages(pages, len(reader.pages))
        metadata["processed_pages"] = choices
        metadata["complete"] = len(choices) == len(reader.pages)
        metadata["total_pages"] = len(reader.pages)
        pdfium = None
        if render:
            import pypdfium2
            pdfium = pypdfium2.PdfDocument(str(path))
        try:
            for number in choices:
                text = reader.pages[number - 1].extract_text() or ""
                record = {"pdf_page": number, "text": text, "needs_visual_reading": len(text.strip()) < 30}
                if pdfium is not None:
                    target = output / f"pages/{number:04}.png"
                    target.parent.mkdir(parents=True, exist_ok=True)
                    page = pdfium[number - 1]
                    bitmap = page.render(scale=1.6)
                    bitmap.to_pil().save(target)
                    bitmap.close()
                    page.close()
                    record["image"] = f"pages/{number:04}.png"
                evidence["pages"].append(record)
        finally:
            if pdfium is not None:
                pdfium.close()
        if evidence["pages"] and all(p["needs_visual_reading"] for p in evidence["pages"]):
            metadata["kind"] = "scan_pdf"
        atomic(output / "pages.txt", "\n\n".join(f"[PDF PAGE {p['pdf_page']}]\n{p['text']}" for p in evidence["pages"]).encode("utf-8"))
        evidence["notes"].append("提取文本仅作阅读辅助；公式、页码、跨页段落必须对照 PDF／页面图像核对。")
    atomic(output / "evidence.json", dumps(evidence))
    return evidence


def tex_draft(evidence, text):
    doc = blank(evidence["source"])
    for missing in evidence.get("missing_includes", []):
        doc["unresolved"].append({"kind": "include", "text": missing, "reason": "TeX 包含文件未提供"})
    body_match = re.search(r"\\begin\{document\}(.*)\\end\{document\}", text, re.S)
    if body_match:
        text = body_match.group(1)
    # Discard TeX comments only, retaining escaped percent signs.
    text = re.sub(r"(?<!\\)%[^\n]*", "", text)
    names = "|".join((*TYPES, "proof"))
    pattern = re.compile(r"\\begin\{(" + names + r")\*?\}(?:\[([^\]]*)\])?(.*?)\\end\{\1\*?\}", re.S)
    labels, last, cursor = {}, None, 0
    def append_body(kind, content, offset, heading=""):
        nonlocal last
        content = content.strip()
        if not content:
            return
        index = len(doc["items"]) + 1
        entry = item(index, doc["source"]["document"], kind, content)
        doc["items"].append(entry)
        doc["reading_order"].append({"index": index, "part": "body"})
        own_labels = re.findall(r"\\label\{([^{}]+)\}", content)
        for label in own_labels:
            labels[label] = index
        doc["anchors"].append({"index": index, "line": text.count("\n", 0, offset) + 1, "labels": own_labels, "environment_title": heading})
        if kind in RESULTS:
            last = index
    def prose(fragment, offset):
        for part in re.split(r"\n\s*\n", fragment):
            if re.fullmatch(r"(?:\\(?:newpage|clearpage|pagebreak)\s*)+", part.strip()):
                continue
            if part.strip():
                append_body("statement", part, offset)
    for match in pattern.finditer(text):
        prose(text[cursor:match.start()], cursor)
        kind, title, content = match.group(1), match.group(2) or "", match.group(3).strip()
        if kind == "proof":
            references = re.findall(r"\\(?:ref|eqref|autoref)\{([^{}]+)\}", title)
            target = labels.get(references[0]) if references else last
            if not content:
                doc["unresolved"].append({"kind": "proof", "text": "", "reason": "空证明环境，需核对是否缺失内容"})
            elif target and not doc["items"][target - 1]["Original"]["content"]["proof"]:
                doc["items"][target - 1]["Original"]["content"]["proof"] = content
                doc["reading_order"].append({"index": target, "part": "proof"})
                if not references:
                    doc["review"]["notes"].append(f"index {target} 的证明按最近结果附属，需核对归属。")
            else:
                doc["unresolved"].append({"kind": "proof", "text": content, "hint": title, "reason": "未确定证明归属，或已有其他证明"})
        else:
            append_body(kind, content, match.start(), title)
        cursor = match.end()
    prose(text[cursor:], cursor)
    for index, entry in enumerate(doc["items"], 1):
        refs = re.findall(r"\\(?:ref|eqref|autoref)\{([^{}]+)\}", entry["Original"]["content"]["body"] + entry["Original"]["content"]["proof"])
        for label in refs:
            doc["unresolved"].append({"kind": "reference", "index": index, "label": label, "target_hint": labels.get(label), "reason": "引用不自动判定为依赖；由 Agent 核对语义后建立关系"})
    return doc


def draft(evidence_path):
    evidence_path = Path(evidence_path)
    evidence = read(evidence_path)
    if evidence["source"]["kind"] == "latex":
        return tex_draft(evidence, (evidence_path.parent / "source.tex").read_text(encoding="utf-8"))
    doc = blank(evidence["source"])
    for page in evidence["pages"]:
        if page["needs_visual_reading"]:
            doc["unresolved"].append({"kind": "page", "pdf_page": page["pdf_page"], "reason": "需 Agent 视觉转录／OCR 核对"})
        for paragraph in re.split(r"\n\s*\n", page["text"]):
            if not paragraph.strip():
                continue
            entry = item(len(doc["items"]) + 1, doc["source"]["document"], "statement", paragraph.strip())
            doc["items"].append(entry)
            doc["reading_order"].append({"index": entry["index"], "part": "body"})
            doc["anchors"].append({"index": entry["index"], "pdf_page": page["pdf_page"]})
    return doc


def source_id(doc, provided=None):
    value = provided or "document-" + doc["source"].get("project_sha256", doc["source"]["sha256"])[:12]
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", value):
        raise DocumentError("文献 ID 需为小写字母、数字和连字符，最长 80 字符")
    return value


def submission_files(doc, provided=None):
    checks = validate(doc)
    name = source_id(doc, provided)
    prefix = f"logs/submissions/{name}/"
    return {prefix + "document.indexed.json": dumps(doc), prefix + "checks.json": dumps({"format": "mathdoc-submission-checks", "schema_version": "1.0", "source_sha256": doc["source"]["sha256"], "checks": checks, "formal_library_write": False})}


def export_submission(doc, target, provided=None):
    files = submission_files(doc, provided)
    target = Path(target)
    if target.suffix.lower() == ".zip":
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        atomic(target, stream.getvalue())
    else:
        if not (target / "mathkb.json").is_file():
            raise DocumentError("提交目录需是包含 mathkb.json 的仓库根目录，或使用 .zip 输出")
        for name, data in files.items():
            path = target / name
            if path.exists() and path.read_bytes() != data:
                raise DocumentError(f"待导入稿已存在且内容不同：{path}；请审阅差异后更新")
        for name, data in files.items():
            atomic(target / name, data)
    return {"files": list(files), "output": str(target), "items": len(doc["items"])}


def check_submissions(repo):
    repo = Path(repo)
    reports = []
    for path in sorted(repo.glob("logs/submissions/*/document.indexed.json")):
        reports.append({"path": path.relative_to(repo).as_posix(), "checks": validate(read(path))})
    return {"valid": True, "submissions": reports}


def plan_import(doc, repo, source_file, provided=None):
    validate(doc, ready=True)
    if not doc["source"]["metadata_verified"]:
        raise DocumentError("需核实来源元数据后再生成正式入库批次")
    if sha(source_file) != doc["source"]["sha256"]:
        raise DocumentError("来源文件 SHA-256 与分拆 JSON 不一致")
    if doc["source"]["kind"] == "latex" and doc["source"].get("project_sha256"):
        fingerprint = hashlib.sha256(expand_tex(source_file).encode("utf-8")).hexdigest()
        if fingerprint != doc["source"]["project_sha256"]:
            raise DocumentError("TeX 项目内容已有变化，包括 input/include 文件；需重新核对分拆稿")
    repo = Path(repo).resolve()
    spec = importlib.util.spec_from_file_location("mathkb_repository_adapter", repo / "infra/tools/mathkb.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    def checked(function, *args):
        try:
            return function(*args)
        except module.LibraryError as error:
            raise DocumentError(f"仓库校验未通过：{error}") from error
    library = checked(module.Library, repo)
    checked(library.validate)
    _, registered, _ = checked(library.load)
    if doc["source"]["document"] in registered:
        raise DocumentError("该来源已登记；首次导入适配器不自动重建或替换现有 UUID，需显式维护已有条目")
    mapping = {entry["index"]: str(uuid.uuid4()) for entry in doc["items"]}
    records = []
    for entry in doc["items"]:
        original = copy.deepcopy(entry["Original"])
        for relation in original["relations"]:
            relation["target"] = mapping[relation["target"]]
        records.append({"id": mapping[entry["index"]], "Original": original})
    source = doc["source"]
    registration = {key: source[key] for key in ("document", "title", "authors", "kind", "sha256")}
    version_label = "project-sha256:" + source["project_sha256"] if source.get("project_sha256") else "file-sha256:" + source["sha256"]
    registration.update(id=source_id(doc, provided), edition=source["edition"] or version_label, synthetic=source["synthetic"])
    entries = []
    for entry in doc["reading_order"]:
        target = {"item_id": mapping[entry["index"]], "part": entry["part"]}
        if "page" in entry:
            target["page"] = entry["page"]
        entries.append(target)
    batch = {"batch_id": str(uuid.uuid4()), "actor": "math-document-indexer", "expected_state_hash": library.state_hash(), "expected_item_hashes": {record["id"]: None for record in records}, "sources": [registration], "orders": [{"document": source["document"], "entries": entries}], "upserts": records}
    checked(library.schema_check, "batch", batch, "indexed document import")
    old_items, old_sources, old_orders = checked(library.load)
    old_items.update({record["id"]: record for record in records})
    old_sources[source["document"]] = registration
    old_orders[source["document"]] = batch["orders"][0]
    checked(library.check_state, old_items, old_sources, old_orders)
    return {"batch": batch, "index_uuid_map": mapping, "checks": {"valid": True, "repository_written": False}}


def serve(document=None, port=8765, source=None, workspace=None):
    from workbench import create_server
    server = create_server(document, port, source, workspace)
    print(json.dumps({"url": f"http://127.0.0.1:{server.server_port}", "workspace": str(server.workspace.root)}, ensure_ascii=True), flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("source", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--pages")
    p.add_argument("--render", action="store_true")
    p = sub.add_parser("draft")
    p.add_argument("evidence", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("validate")
    p.add_argument("document", type=Path)
    p.add_argument("--ready", action="store_true")
    p = sub.add_parser("submit")
    p.add_argument("document", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--source-id")
    p = sub.add_parser("check-submissions")
    p.add_argument("repository", type=Path)
    p = sub.add_parser("plan-import")
    p.add_argument("document", type=Path)
    p.add_argument("--repository", type=Path, required=True)
    p.add_argument("--source-file", type=Path, required=True)
    p.add_argument("--source-id")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("view")
    p.add_argument("document", type=Path, nargs="?")
    p.add_argument("--workspace", type=Path)
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--source", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            evidence = prepare(args.source, args.out, args.pages, args.render)
            result = {"evidence": str(args.out / "evidence.json"), "source": evidence["source"], "pages": len(evidence["pages"])}
        elif args.command == "draft":
            data = draft(args.evidence)
            validate(data)
            atomic(args.out, dumps(data))
            result = {"output": str(args.out), "checks": validate(data)}
        elif args.command == "validate":
            result = validate(read(args.document), args.ready)
        elif args.command == "submit":
            result = export_submission(read(args.document), args.output, args.source_id)
        elif args.command == "check-submissions":
            result = check_submissions(args.repository)
        elif args.command == "plan-import":
            if args.out.exists() or args.out.with_suffix(".index-map.json").exists():
                raise DocumentError("入库计划或 UUID 映射已存在；复用已保存计划，或选择新的输出路径后审阅")
            result = plan_import(read(args.document), args.repository, args.source_file, args.source_id)
            atomic(args.out, dumps(result["batch"]))
            atomic(args.out.with_suffix(".index-map.json"), dumps(result["index_uuid_map"]))
            result = {"batch": str(args.out), "mapping": str(args.out.with_suffix('.index-map.json')), "repository_written": False}
        else:
            if args.document:
                validate(read(args.document))
            serve(args.document, args.port, args.source, args.workspace)
            return 0
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (DocumentError, OSError, ValueError, ImportError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
