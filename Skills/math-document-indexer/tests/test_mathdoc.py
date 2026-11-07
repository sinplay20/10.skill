import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT
sys.path.insert(0, str(SKILL / 'scripts'))
import mathdoc


class DocumentTests(unittest.TestCase):
    def setUp(self):
        (ROOT / 'work').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'work')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.doc = mathdoc.read(SKILL / 'assets/example.indexed.json')

    def test_index_model_delayed_proof_and_evidence(self):
        self.assertEqual(mathdoc.validate(self.doc)['items'], 12)
        positions = [(row['part'], row['page']) for row in self.doc['reading_order'] if row['index'] == 4]
        self.assertEqual(positions, [('body', '2'), ('proof', '5')])
        self.assertEqual({relation['basis'] for relation in self.doc['items'][3]['Original']['relations']}, {'explicit', 'inferred'})
        self.assertFalse(any('id' in item for item in self.doc['items']))

    def test_dangling_relations_missing_proof_and_duplicate_indices_fail(self):
        changes = []
        bad = copy.deepcopy(self.doc); bad['items'][3]['Original']['relations'][0]['target'] = 999; changes.append(bad)
        bad = copy.deepcopy(self.doc); bad['reading_order'].pop(); changes.append(bad)
        bad = copy.deepcopy(self.doc); bad['items'][1]['index'] = 1; changes.append(bad)
        bad = copy.deepcopy(self.doc); bad['items'][0]['Original']['content']['type'] = 'proof'; changes.append(bad)
        for bad in changes:
            with self.assertRaises(mathdoc.DocumentError): mathdoc.validate(bad)

    def test_original_unicode_latex_and_newlines_roundtrip(self):
        original = '中文 α\\beta\r\n\r\nA\u2028B\n'
        self.doc['items'][0]['Original']['content']['body'] = original
        restored = mathdoc.loads(mathdoc.dumps(self.doc).decode())
        mathdoc.validate(restored)
        self.assertEqual(restored['items'][0]['Original']['content']['body'], original)

    def test_duplicate_keys_and_nonfinite_numbers_fail(self):
        for value in ('{"index":1,"index":2}', '{"x":NaN}'):
            with self.assertRaises(mathdoc.DocumentError): mathdoc.loads(value)

    def test_tex_draft_binds_a_delayed_proof_and_leaves_relations_to_agent(self):
        evidence = mathdoc.prepare(SKILL / 'assets/example.tex', self.root / 'prepared')
        doc = mathdoc.draft(self.root / 'prepared/evidence.json')
        mathdoc.validate(doc)
        theorem = next(item for item in doc['items'] if item['Original']['content']['type'] == 'theorem')
        self.assertIn('m+n', theorem['Original']['content']['proof'])
        self.assertEqual(doc['reading_order'][-1], {'index':theorem['index'], 'part':'proof'})
        self.assertEqual(doc['review']['status'], 'draft')
        self.assertTrue(all(not item['Original']['relations'] for item in doc['items']))
        self.assertTrue(evidence['source']['project_sha256'])

    def test_empty_proof_and_missing_includes_remain_unresolved(self):
        source = self.root / 'main.tex'
        source.write_text(r'\begin{document}\begin{theorem}A.\end{theorem}\begin{proof}\end{proof}\input{missing}\end{document}', encoding='utf-8')
        mathdoc.prepare(source, self.root / 'prepared')
        doc = mathdoc.draft(self.root / 'prepared/evidence.json')
        mathdoc.validate(doc)
        self.assertEqual({row['kind'] for row in doc['unresolved']}, {'proof', 'include'})
        with self.assertRaises(mathdoc.DocumentError): mathdoc.validate(doc, ready=True)

    def test_multifile_tex_fingerprint_detects_an_input_change(self):
        main = self.root / 'main.tex'; child = self.root / 'part.tex'
        main.write_text(r'\begin{document}\input{part}\end{document}', encoding='utf-8')
        child.write_text('An original mathematical paragraph.', encoding='utf-8')
        mathdoc.prepare(main, self.root / 'prepared')
        doc = mathdoc.draft(self.root / 'prepared/evidence.json')
        doc['review']['status'] = 'agent_checked'; doc['source']['metadata_verified'] = True
        child.write_text('A changed original paragraph.', encoding='utf-8')
        with self.assertRaisesRegex(mathdoc.DocumentError, '项目内容'):
            mathdoc.plan_import(doc, self.root / 'not-a-repo', main)

    def test_tex_includes_cannot_escape_project_or_form_a_cycle(self):
        main = self.root / 'main.tex'
        main.write_text(r'\input{main}', encoding='utf-8')
        with self.assertRaises(mathdoc.DocumentError): mathdoc.expand_tex(main)
        project = self.root / 'project'; project.mkdir()
        (self.root / 'outside.tex').write_text('Outside.', encoding='utf-8')
        (project / 'main.tex').write_text(r'\input{../outside}', encoding='utf-8')
        with self.assertRaises(mathdoc.DocumentError): mathdoc.expand_tex(project / 'main.tex')

    def test_submission_contains_index_json_and_actual_checks_only(self):
        target = self.root / 'submission.zip'
        mathdoc.export_submission(self.doc, target)
        with zipfile.ZipFile(target) as archive:
            names = archive.namelist()
            self.assertEqual(len(names), 2)
            self.assertTrue(all(name.startswith('logs/submissions/') for name in names))
            doc = json.loads(archive.read(next(name for name in names if name.endswith('document.indexed.json'))))
            self.assertEqual(doc, self.doc)
            self.assertFalse(any(name.endswith(('.pdf', '.tex')) for name in names))

    def test_repository_staging_is_idempotent_and_rejects_silent_overwrites(self):
        mathdoc.atomic(self.root / 'mathkb.json', b'{}')
        mathdoc.export_submission(self.doc, self.root, 'demo-source')
        mathdoc.export_submission(self.doc, self.root, 'demo-source')
        self.assertEqual(len(mathdoc.check_submissions(self.root)['submissions']), 1)
        changed = copy.deepcopy(self.doc); changed['review']['notes'].append('New review note.')
        with self.assertRaises(mathdoc.DocumentError): mathdoc.export_submission(changed, self.root, 'demo-source')

    def test_source_hash_mismatch_and_unreviewed_content_cannot_import(self):
        source = self.root / 'wrong.tex'; source.write_text('Wrong source.', encoding='utf-8')
        with self.assertRaisesRegex(mathdoc.DocumentError, 'SHA-256'):
            mathdoc.plan_import(self.doc, self.root, source)
        self.doc['review']['status'] = 'draft'
        with self.assertRaises(mathdoc.DocumentError): mathdoc.validate(self.doc, ready=True)

    def test_pdf_page_ranges_text_and_scan_visual_evidence(self):
        from pypdf import PdfWriter
        from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject
        writer = PdfWriter()
        page = writer.add_blank_page(350,450)
        font = DictionaryObject({NameObject('/Type'):NameObject('/Font'), NameObject('/Subtype'):NameObject('/Type1'), NameObject('/BaseFont'):NameObject('/Helvetica')})
        page[NameObject('/Resources')] = DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
        stream = DecodedStreamObject(); stream.set_data(b'BT /F1 12 Tf 20 350 Td (Definition 1. An integer n is even when n = 2k.) Tj ET')
        page[NameObject('/Contents')] = writer._add_object(stream)
        writer.add_blank_page(350,450)
        source = self.root / 'fixture.pdf'
        with source.open('wb') as handle: writer.write(handle)
        evidence = mathdoc.prepare(source, self.root / 'text', '1', render=True)
        self.assertFalse(evidence['source']['complete'])
        self.assertIn('Definition 1', evidence['pages'][0]['text'])
        self.assertTrue((self.root / 'text/pages/0001.png').is_file())
        scanned = mathdoc.prepare(source, self.root / 'scan', '2', render=True)
        self.assertTrue(scanned['pages'][0]['needs_visual_reading'])
        doc = mathdoc.draft(self.root / 'scan/evidence.json')
        mathdoc.validate(doc)
        self.assertTrue(doc['unresolved'])
        with self.assertRaises(mathdoc.DocumentError): mathdoc.prepare(source, self.root / 'invalid', '3')


class RepositoryAdapterTests(unittest.TestCase):
    def setUp(self):
        repository = Path(os.environ.get('MATHKB_TEST_REPOSITORY', ROOT.parent / 'math-knowledge-base'))
        if not (repository / 'infra/tools/mathkb.py').is_file(): self.skipTest('Set MATHKB_TEST_REPOSITORY to test the repository adapter')
        (ROOT / 'work').mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT / 'work'); self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        for relative in ('infra/tools/mathkb.py', 'infra/VERSION'):
            path = self.repo / relative; path.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(repository / relative, path)
        shutil.copytree(repository / 'infra/spec/schemas', self.repo / 'infra/spec/schemas')
        mathdoc.atomic(self.repo / 'mathkb.json', mathdoc.dumps({'format':'math-knowledge-base','schema_version':'1.0','layout_version':4,'shard_prefix_length':2,'allow_synthetic_sources':True}))
        mathdoc.atomic(self.repo / 'sources/index.json', mathdoc.dumps({'sources':[]}))
        self.doc = mathdoc.read(SKILL / 'assets/example.indexed.json')

    def test_index_document_converts_and_applies_through_existing_repository_tool(self):
        result = mathdoc.plan_import(self.doc, self.repo, SKILL / 'assets/example.tex')
        mapping = result['index_uuid_map']
        self.assertEqual(len(set(mapping.values())), 12)
        for item in result['batch']['upserts']:
            self.assertNotIn('index',item)
            self.assertEqual(len(item['id']),36)
        spec=importlib.util.spec_from_file_location('repository_under_test',self.repo/'infra/tools/mathkb.py')
        module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        library=module.Library(self.repo)
        library.apply(result['batch'])
        self.assertEqual(library.validate()['items'],12)
        self.assertEqual(library.apply(result['batch'])['status'],'already_applied')
        positions=[(row['part'],row['page']) for row in library.read_source(self.doc['source']['document']) if row['item_id']==mapping[4]]
        self.assertEqual(positions,[('body','2'),('proof','5')])
        with self.assertRaises(mathdoc.DocumentError): mathdoc.plan_import(self.doc,self.repo,SKILL/'assets/example.tex')

    def test_synthetic_demonstration_cannot_enter_production(self):
        config=mathdoc.read(self.repo/'mathkb.json');config['allow_synthetic_sources']=False
        mathdoc.atomic(self.repo/'mathkb.json',mathdoc.dumps(config))
        with self.assertRaises(mathdoc.DocumentError): mathdoc.plan_import(self.doc,self.repo,SKILL/'assets/example.tex')
        self.assertEqual(mathdoc.read(self.repo/'sources/index.json'),{'sources':[]})


if __name__=='__main__': unittest.main()
