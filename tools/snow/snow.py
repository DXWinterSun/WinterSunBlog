#!/usr/bin/env python3
"""Encrypted snow journal. JSON input on stdin; never pass private text as CLI args."""
import argparse
import copy
import datetime
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'private'))
import private as store

NAME = 'snow-journal'

def validate(data):
    for collection in ('logs', 'meals'):
        rows = data['collections'][collection]
        ids = [r['id'] for r in rows]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate record IDs')
        for r in rows:
            v = r['data']
            datetime.date.fromisoformat(v['date'])
            number = v['kg'] if collection == 'logs' else v['kcal']
            if not isinstance(number, (int, float)) or not math.isfinite(number) or number < 0:
                raise ValueError('Invalid numeric value')
            if 'kcalRange' in v:
                low, high = v['kcalRange']
                if not 0 <= low <= number <= high:
                    raise ValueError('Invalid estimate range')
    if not data['settings'].get('exists'):
        raise ValueError('Settings missing')

def apply(data, collection, row):
    data = copy.deepcopy(data)
    if collection == 'meals' and row['data'].get('planned'):
        raise ValueError('Planned food must not be counted')
    rows = data['collections'][collection]
    rows[:] = [r for r in rows if r['id'] != row['id']]
    # One weigh-in per day, consistent with the original journal.
    if collection == 'logs':
        rows[:] = [r for r in rows if r['data']['date'] != row['data']['date']]
    rows.append(row)
    rows.sort(key=lambda r: (r['data']['date'], r['id']))
    validate(data)
    return data

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['import', 'meal', 'weight', 'summary'])
    a = p.parse_args()
    box, index = store.load()  # Requires an EXISTING vault; never creates/resets it.
    doc = store.load_doc(box, NAME)
    if a.command == 'summary':
        if not doc:
            p.error('Journal has not been imported')
        data = doc['page']
    else:
        incoming = json.load(sys.stdin)
        if a.command == 'import':
            if doc:
                p.error('Journal already exists; bulk import refused')
            data = incoming
            validate(data)
            doc = {'name': NAME, 'title': '雪地打卡', 'created': store.stamp(),
                   'body': '结构化记录保存在 page 中。', 'log': []}
        else:
            if not doc:
                p.error('Journal has not been imported')
            data = apply(doc['page'], 'meals' if a.command == 'meal' else 'logs', incoming)
        doc['page'] = data
        store.save(box, index, doc, '私人档案：更新一份', argparse.Namespace(dry_run=False, trailer=[]))
        # Verify the persisted remote content without exposing plaintext.
        box2, _ = store.load()
        assert store.load_doc(box2, NAME)['page'] == data, 'Remote readback mismatch'
    print(json.dumps({'weights': len(data['collections']['logs']),
                      'meals': len(data['collections']['meals']),
                      'verified': True}, ensure_ascii=False))

if __name__ == '__main__':
    main()
