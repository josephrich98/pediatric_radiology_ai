#!/usr/bin/env python3
"""Archive and screen authorization documents for every row of an FDA AI list.

Run with PYTHONPATH=. python scripts/collect_fda_pediatric_inventory.py.
Requires pdftotext. The dated source CSV is immutable; reruns resume downloads.
Keyword matches are screening aids, never automatic pediatric authorization.
"""
from __future__ import annotations

import concurrent.futures
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/fda_pediatric_inventory/2026-09-16'
OUT = ROOT / 'data/processed/fda_pediatric_screening.json'
SIGNALS = re.compile(
    r'\b(?:p[ae]+diatric\w*|child\w*|adolescen\w*|infant\w*|neonat\w*|'
    r'newborn\w*|f[oe]+tal\w*|fetus\w*|foetus\w*|prenatal\w*|obstetric\w*)\b|'
    r'\b(?:age[ds]?|aged from)\s*[:≥>\-=]*\s*(?:[0-9]|1[0-7])\b|'
    r'\b(?:[0-9]|1[0-7])\s*(?:years?\s*(?:of age|old)|to\s*\d+\s*years?)', re.I)


def request(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (public regulatory research)'})
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()


def urls(sub):
    if sub.startswith('K'):
        return [f'https://www.accessdata.fda.gov/cdrh_docs/pdf{sub[1:3]}/{sub}.pdf']
    if sub.startswith('DEN'):
        return [f'https://www.accessdata.fda.gov/cdrh_docs/reviews/{sub}.pdf',
                f'https://www.accessdata.fda.gov/cdrh_docs/pdf{sub[3:5]}/{sub}.pdf']
    if sub.startswith('P'):
        base = sub[:7]
        suffix = sub[7:]
        return [f'https://www.accessdata.fda.gov/cdrh_docs/pdf{sub[1:3]}/{base}{suffix}B.pdf',
                f'https://www.accessdata.fda.gov/cdrh_docs/pdf{sub[1:3]}/{base}{suffix}b.pdf']
    return []


def collect_one(row):
    sub = row['Submission Number'].strip()
    pdf, txt = RAW / 'documents' / f'{sub}.pdf', RAW / 'text' / f'{sub}.txt'
    record = dict(row, document_url='', retrieval_status='', screening_hits=[])
    source = pdf.with_suffix('.url')
    if pdf.exists():
        record['document_url'] = source.read_text() if source.exists() else urls(sub)[0]
    else:
        errors = []
        for url in urls(sub):
            try:
                data = request(url)
                if not data.startswith(b'%PDF'):
                    raise ValueError('Response is not a PDF')
                pdf.write_bytes(data)
                source.write_text(url)
                record['document_url'] = url
                break
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                errors.append(str(exc))
        if not pdf.exists():
            record.update(retrieval_status='unavailable', error='; '.join(errors))
            return record
    if not txt.exists():
        result = subprocess.run(['pdftotext', '-layout', str(pdf), str(txt)], capture_output=True)
        if result.returncode:
            record.update(retrieval_status='extraction_failed', error=result.stderr.decode(errors='replace')[:200])
            return record
    text = txt.read_text(errors='replace')
    record.update(pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                  text_characters=len(text), document_pages=len(text.split('\f')) - 1,
                  retrieval_status='text_available' if len(text.strip()) >= 400 else 'needs_ocr')
    for page, body in enumerate(text.split('\f'), 1):
        for match in SIGNALS.finditer(body):
            start, end = max(0, match.start()-220), min(len(body), match.end()+380)
            excerpt = re.sub(r'\s+', ' ', body[start:end]).strip()
            if not any(h['page']==page and abs(h['offset']-match.start())<220 for h in record['screening_hits']):
                record['screening_hits'].append({'page': page, 'offset': match.start(), 'text': excerpt})
    return record


def main():
    for part in ['documents', 'text']:
        (RAW / part).mkdir(parents=True, exist_ok=True)
    with (RAW/'ai_devices.csv').open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        jobs = {pool.submit(collect_one, row): row for row in rows}
        for future in concurrent.futures.as_completed(jobs):
            try:
                records.append(future.result())
            except Exception as exc:
                records.append(dict(jobs[future], retrieval_status='error', error=str(exc), screening_hits=[]))
            if len(records)%100 == 0:
                print(f'{len(records)}/{len(rows)} documents screened', flush=True)
    records.sort(key=lambda row: row['Submission Number'])
    result = {'retrieved_on':'2026-09-16', 'source':'https://www.fda.gov/media/178541/download?attachment',
              'source_sha256':hashlib.sha256((RAW/'ai_devices.csv').read_bytes()).hexdigest(),
              'source_rows':len(rows), 'records':records}
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    from collections import Counter
    print(Counter(r['retrieval_status'] for r in records))
    print('Documents with screening hits:',sum(bool(r['screening_hits']) for r in records))


if __name__ == '__main__':
    main()
