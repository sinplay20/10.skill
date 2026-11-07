"""Local document uploads and persistent workbench sessions."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import mimetypes
from pathlib import Path
import secrets
import threading
from urllib.parse import parse_qs, unquote, urlparse
import zipfile

import mathdoc as core


class Workspace:
    def __init__(self, root, document=None, source=None):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest = self.root / 'workspace.json'
        self.lock = threading.RLock()
        self.jobs = {}
        self.busy = False
        self.token = secrets.token_urlsafe(32)
        self.catalog = core.read(self.manifest) if self.manifest.is_file() else {'active':None, 'documents':[]}
        self.initial = (Path(document).resolve(), Path(source).resolve() if source else None) if document else None
        if self.initial:
            self.active = 'initial'
        else:
            self.active = self.catalog.get('active')

    def persist(self):
        self.catalog['active'] = self.active if self.active != 'initial' else None
        core.atomic(self.manifest, core.dumps(self.catalog))

    def contained(self, relative):
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise core.DocumentError('文献路径超出工作区')
        return path

    def paths(self, key=None):
        key = self.active if key is None else key
        if key == 'initial' and self.initial:
            return self.initial
        for record in self.catalog['documents']:
            if record['key'] == key:
                return self.contained(record['document']), self.contained(record['source']) if record.get('source') else None
        return None, None

    def etag(self, path, doc):
        return hashlib.sha256(str(path).encode() + b'\0' + core.dumps(doc)).hexdigest()

    def info(self):
        document, source = self.paths()
        return {'document_path':str(document) if document else None, 'source_path':str(source) if source else None,
                'source_sha256':core.sha(source) if source and source.is_file() else None,
                'source_available':bool(source and source.is_file()), 'skill_path':str(core.SKILL),
                'workspace_path':str(self.root), 'active':self.active, 'token':self.token}

    def library(self):
        result = []
        keys = (['initial'] if self.initial else []) + [r['key'] for r in self.catalog['documents']]
        for key in keys:
            document, _ = self.paths(key)
            try:
                doc = core.read(document)
                result.append({'key':key, 'title':doc['source']['title'], 'items':len(doc['items']),
                               'status':doc['review']['status'], 'active':key == self.active})
            except (OSError, core.DocumentError, KeyError):
                result.append({'key':key, 'title':'文档暂不可读', 'items':0, 'status':'unavailable', 'active':False})
        return result

    def activate(self, key):
        document, _ = self.paths(key)
        if document is None:
            raise core.DocumentError('找不到该文献')
        core.validate(core.read(document))
        self.active = key
        self.persist()

    def register(self, key, source=None):
        record = {'key':key, 'document':f'documents/{key}/document.indexed.json',
                  'source':source, 'created_at':datetime.now(timezone.utc).isoformat()}
        self.catalog['documents'].append(record)
        self.persist()

    def import_json(self, data):
        core.validate(data)
        key = secrets.token_hex(12)
        core.atomic(self.root / f'documents/{key}/document.indexed.json', core.dumps(data))
        self.register(key)
        return key

    def upload(self, name, data, pages='', render=False):
        extension = Path(name).suffix.lower()
        if extension not in {'.pdf', '.tex'}:
            raise core.DocumentError('请选择 PDF 或 UTF-8 编码的 TeX 文件')
        if not data or len(data) > 100 * 1024 * 1024:
            raise core.DocumentError('文献大小须在 0..100 MiB 以内')
        if extension == '.pdf' and b'%PDF-' not in data[:1024]:
            raise core.DocumentError('文件内容不是 PDF')
        if extension == '.tex':
            data.decode('utf-8-sig')
            if b'\0' in data:
                raise core.DocumentError('TeX 文件须为文本')
        with self.lock:
            if self.busy:
                raise core.DocumentError('上一份文献仍在处理中，请稍后再试')
            key = secrets.token_hex(12)
            folder = self.root / 'documents' / key
            source = folder / ('source' + extension)
            core.atomic(source, data)
            self.jobs[key] = {'key':key, 'status':'processing', 'message':'正在提取原文并生成结构初稿'}
            self.busy = True
        def process():
            try:
                evidence = core.prepare(source, folder / 'prepared', pages or None, render)
                evidence['source']['title'] = Path(name.replace('\\','/').split('/')[-1]).stem
                evidence['source']['document'] = f'sources/files/{key}/source{extension}'
                core.atomic(folder / 'prepared/evidence.json', core.dumps(evidence))
                draft = core.draft(folder / 'prepared/evidence.json')
                core.validate(draft)
                core.atomic(folder / 'document.indexed.json', core.dumps(draft))
                with self.lock:
                    self.register(key, f'documents/{key}/source{extension}')
                    self.jobs[key] = {'key':key, 'status':'completed', 'items':len(draft['items']),
                                      'unresolved':len(draft['unresolved']), 'message':'结构初稿已保存，待 Agent 对照原文核对'}
            except Exception as error:
                with self.lock:
                    self.jobs[key] = {'key':key, 'status':'failed', 'message':f'处理失败：{error}'}
            finally:
                with self.lock:
                    core.atomic(folder / 'job.json', core.dumps(self.jobs[key]))
                    self.busy = False
        threading.Thread(target=process, daemon=True).start()
        return {'key':key, 'status':'processing'}


def create_server(document=None, port=8765, source=None, workspace=None):
    root = workspace or (Path(document).resolve().parent / 'imports' if document else Path.cwd() / 'work/mathdoc')
    state = Workspace(root, document, source)
    assets = core.SKILL / 'assets'
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, data, mime='application/json; charset=utf-8', status=200, filename=None, etag=None):
            self.send_response(status)
            for key, value in [('Content-Type',mime),('Content-Length',str(len(data))),('Cache-Control','no-store'),('X-Content-Type-Options','nosniff')]:
                self.send_header(key,value)
            if etag:
                self.send_header('ETag',etag)
            if filename:
                self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
            self.end_headers()
            self.wfile.write(data)

        def allowed_host(self):
            return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}

        def do_GET(self):
            if not self.allowed_host():
                return self.send(b'Host rejected','text/plain',403)
            try:
                parsed = urlparse(self.path)
                route = unquote(parsed.path)
                with state.lock:
                    document, source = state.paths()
                    if route == '/api/info':
                        return self.send(core.dumps(state.info()))
                    if route == '/api/library':
                        return self.send(core.dumps(state.library()))
                    if route == '/api/job':
                        key = parse_qs(parsed.query).get('key',[''])[0]
                        return self.send(core.dumps(state.jobs.get(key,{'status':'failed','message':'任务不存在，请查看文献库中的已保存文档'})))
                    if route == '/api/document':
                        if document is None:
                            return self.send(b'null')
                        data = core.read(document)
                        core.validate(data)
                        return self.send(core.dumps(data),etag=state.etag(document,data))
                if route == '/source' and source and source.is_file():
                    return self.send(source.read_bytes(),'application/pdf' if source.suffix.lower()=='.pdf' else 'text/plain; charset=utf-8')
                target = (assets / ('index.html' if route=='/' else route.removeprefix('/assets/'))).resolve()
                if not target.is_relative_to(assets.resolve()) or not target.is_file() or (route!='/' and not route.startswith('/assets/')):
                    return self.send(b'Not found','text/plain',404)
                return self.send(target.read_bytes(),mimetypes.guess_type(target)[0] or 'application/octet-stream')
            except (core.DocumentError,OSError,ValueError) as error:
                self.send(core.dumps({'error':str(error)}),status=400)

        def do_POST(self):
            try:
                if not self.allowed_host() or self.headers.get('Origin',f"http://{self.headers.get('Host')}") != f"http://{self.headers.get('Host')}" or self.headers.get('X-Mathdoc-Token') != state.token:
                    # Drain bounded bodies so Windows can deliver the rejection before closing.
                    rejected_size = int(self.headers.get('Content-Length',0))
                    if 0 < rejected_size <= 100 * 1024 * 1024:
                        self.connection.settimeout(30)
                        self.rfile.read(rejected_size)
                    return self.send(core.dumps({'error':'请求来源无效，请刷新本地工作台'}),status=403)
                parsed = urlparse(self.path)
                size = int(self.headers.get('Content-Length',0))
                maximum = 100 if parsed.path == '/api/upload' else 30
                if not 0 < size <= maximum * 1024 * 1024:
                    raise core.DocumentError(f'文件大小须在 0..{maximum} MiB 以内')
                body = self.rfile.read(size)
                if len(body) != size:
                    raise core.DocumentError('文件上传不完整')
                if parsed.path == '/api/upload':
                    params = parse_qs(parsed.query)
                    result = state.upload(unquote(self.headers.get('X-File-Name','')),body,params.get('pages',[''])[0],params.get('render',['0'])[0]=='1')
                    return self.send(core.dumps(result),status=202)
                data = core.loads(body.decode('utf-8'))
                with state.lock:
                    if parsed.path == '/api/activate':
                        state.activate(data.get('key'))
                        return self.send(core.dumps(state.info()))
                    if parsed.path == '/api/import-json':
                        return self.send(core.dumps({'key':state.import_json(data)}))
                    core.validate(data)
                    document, _ = state.paths()
                    if parsed.path == '/api/save':
                        if document is None or self.headers.get('If-Match') != state.etag(document,core.read(document)):
                            return self.send(core.dumps({'error':'工作区文档已有更新或已切换，请刷新并核对差异后再保存。'}),status=409)
                        core.atomic(document,core.dumps(data))
                        return self.send(core.dumps({'saved':True}),etag=state.etag(document,data))
                    if parsed.path == '/api/submission':
                        archive = io.BytesIO()
                        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as handle:
                            for name, content in core.submission_files(data).items():
                                handle.writestr(name,content)
                        return self.send(archive.getvalue(),'application/zip',filename='mathdoc-submission.zip')
                self.send(b'Not found','text/plain',404)
            except (core.DocumentError,OSError,ValueError,AttributeError) as error:
                self.send(core.dumps({'error':str(error)}),status=400)
    server = ThreadingHTTPServer(('127.0.0.1',port),Handler)
    server.workspace = state
    return server
