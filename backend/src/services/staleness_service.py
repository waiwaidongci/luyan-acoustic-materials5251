"""Source-data fingerprints: detect which frozen trade-offs a measurement revision makes stale.

A run freezes its own snapshot at creation time; the shared material library and criterion
definitions keep evolving. This module hashes the *current* source data in exactly the shape a
new run would freeze it, so a fingerprint mismatch means "the same preferences today would no
longer reproduce this result". Old runs, their results and approved trial notes are never
rewritten — staleness is a read-time annotation.
"""
import hashlib
import json

from sqlalchemy import select

from src.models import CandidateStudy, Criterion, MaterialSample

METRIC_FIELDS = ('absorption', 'impact', 'carbon', 'price', 'thickness')
SAMPLE_FIELDS = ('id', 'code') + METRIC_FIELDS
CRITERION_FIELDS = ('id', 'code', 'name', 'unit', 'direction', 'center_weight')


def _canonical(payload) -> str:
    return json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False, default=str)


def _coerce_measurements(payload) -> dict:
    """Force every metric value and criterion weight to float in a signature payload.

    Keeps hashing independent of JSON text storage, which may return 1.0 as integer 1.
    Identifiers and material id lists are left untouched.
    """
    out = dict(payload)
    out['samples'] = [
        {**s, **{f: float(s[f]) for f in METRIC_FIELDS if f in s}}
        for s in payload.get('samples', [])
    ]
    out['criteria'] = [
        {**c, **({'center_weight': float(c['center_weight'])} if 'center_weight' in c else {})}
        for c in payload.get('criteria', [])
    ]
    return out


def fingerprint_payload(payload) -> str:
    return hashlib.sha256(_canonical(_coerce_measurements(payload)).encode()).hexdigest()


def current_source(db, study: CandidateStudy) -> dict:
    """Build the source signature payload for a study as it would be frozen right now."""
    samples = db.scalars(
        select(MaterialSample)
        .where(MaterialSample.id.in_(study.material_ids))
        .order_by(MaterialSample.code)
    ).all()
    criteria = db.scalars(
        select(Criterion)
        .where(Criterion.study_id == study.id)
        .order_by(Criterion.code)
    ).all()
    return {
        'study_id': study.id,
        'material_ids': list(study.material_ids),
        'samples': [{k: getattr(s, k) for k in SAMPLE_FIELDS} for s in samples],
        'criteria': [{k: getattr(c, k) for k in CRITERION_FIELDS} for c in criteria],
    }


def current_source_fingerprint(db, study: CandidateStudy) -> str:
    return fingerprint_payload(current_source(db, study))


def _sample_index(payload: dict) -> dict:
    return {s['id']: s for s in payload.get('samples', [])}


def _criterion_index(payload: dict) -> dict:
    return {c['code']: c for c in payload.get('criteria', [])}


def diff_sources(frozen: dict, current: dict) -> dict:
    """Explain *why* a frozen run is stale: changed/added/removed samples and criteria."""
    old_samples, new_samples = _sample_index(frozen), _sample_index(current)
    old_criteria, new_criteria = _criterion_index(frozen), _criterion_index(current)

    changed_samples = []
    for sid, old in old_samples.items():
        new = new_samples.get(sid)
        if new is None:
            changed_samples.append({'sample_id': sid, 'code': old.get('code'), 'kind': 'removed', 'fields': []})
            continue
        fields = [f for f in METRIC_FIELDS if float(old.get(f)) != float(new.get(f))]
        if fields:
            changed_samples.append({
                'sample_id': sid, 'code': new.get('code'), 'kind': 'changed', 'fields': fields,
                'before': {f: old.get(f) for f in fields}, 'after': {f: new.get(f) for f in fields},
            })
    for sid, new in new_samples.items():
        if sid not in old_samples:
            changed_samples.append({'sample_id': sid, 'code': new.get('code'), 'kind': 'added', 'fields': []})

    changed_criteria = []
    for code, old in old_criteria.items():
        new = new_criteria.get(code)
        if new is None:
            changed_criteria.append({'code': code, 'name': old.get('name'), 'kind': 'removed', 'fields': []})
            continue
        fields = []
        for f in ('name', 'unit', 'direction', 'center_weight'):
            if f == 'center_weight':
                if float(old.get(f)) != float(new.get(f)):
                    fields.append(f)
            elif old.get(f) != new.get(f):
                fields.append(f)
        if fields:
            changed_criteria.append({
                'code': code, 'name': new.get('name'), 'kind': 'changed', 'fields': fields,
                'before': {f: old.get(f) for f in fields}, 'after': {f: new.get(f) for f in fields},
            })
    for code, new in new_criteria.items():
        if code not in old_criteria:
            changed_criteria.append({'code': code, 'name': new.get('name'), 'kind': 'added', 'fields': []})

    return {
        'sample_changes': changed_samples,
        'criterion_changes': changed_criteria,
        'affected_sample_ids': [c['sample_id'] for c in changed_samples if c['kind'] != 'added'],
    }


def _as_dict(value) -> dict:
    """JSON columns arrive as dict on MySQL drivers but as a JSON string on SQLite."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}
    return value or {}


def staleness_report(db, run) -> dict:
    """Read-time staleness annotation for one run."""
    frozen = _as_dict(run.source_signature)
    frozen_fp = run.source_fingerprint or ''
    study = db.get(CandidateStudy, run.study_id)
    current = current_source(db, study)
    current_fp = fingerprint_payload(current)
    is_stale = bool(frozen_fp) and frozen_fp != current_fp
    report = {
        'stale': is_stale,
        'source_fingerprint': frozen_fp,
        'current_fingerprint': current_fp,
        'recalc_of_id': run.recalc_of_id,
        'recalc_seq': run.recalc_seq,
        'recalc_status': run.recalc_status,
    }
    if is_stale:
        report.update(diff_sources(frozen, current))
    else:
        report.update({'sample_changes': [], 'criterion_changes': [], 'affected_sample_ids': []})
    return report
