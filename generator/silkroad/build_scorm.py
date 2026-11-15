#!/usr/bin/env python3
"""Сборка SCORM-пакета курса «Шёлковый путь» (общий плеер берётся из ../sales/course).
   python3 build_scorm.py [2004|12]          -> zip в корне репозитория
   python3 build_scorm.py assemble <папка>   -> собрать курс в папку (для локальной проверки)"""
import os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'sales'))
import build_scorm as base

COURSE = {
    'src': [os.path.join(HERE, '..', 'sales', 'course'), os.path.join(HERE, 'course')],
    'exclude': ['js/content.js', 'js/content2.js', 'js/config.js', 'index.html', 'video/', 'docs/'],
    'title': 'Шёлковый путь: знакомство с Ipak Yuli Bank',
    'ident': 'IYB_SILK_ROAD_COURSE_2026',
    'zip': 'Shelkovyj_put_kurs',
    'extra': {'docs/Shelkovyj_put_prezentaciya.pptx': os.path.join(base.ROOT, 'Shelkovyj_put_prezentaciya.pptx')},
    'videos': 4,
}

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'assemble':
        c = dict(COURSE); c['extra'] = {k: v for k, v in COURSE['extra'].items() if os.path.exists(v)}
        out = sys.argv[2]; shutil.rmtree(out, ignore_errors=True)
        for rel, full in base.collect(c).items():
            dst = os.path.join(out, rel); os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copyfile(full, dst)
        print('assembled', out)
    else:
        base.build(COURSE, sys.argv[1] if len(sys.argv) > 1 else '2004')
