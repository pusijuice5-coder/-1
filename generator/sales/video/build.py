#!/usr/bin/env python3
"""Сборка видеороликов курса: тайминги сцен по паузам озвучки -> покадровый рендер -> MP4 + постер.
   Запуск: python3 build.py [v1 v2 ...]                         — ролики курса продаж
           python3 build.py --course ../../silkroad [v1 ...]    — ролики другого курса (папка с video/ и course/)
   В папке <курс>/video лежат scenes.js, vo/*.mp3 и необязательный video.json с настройками."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = sys.argv[1:]
VDIR, OUT, ENV = HERE, os.path.join(HERE, '..', 'course', 'video'), dict(os.environ)
IDS = ['v1', 'v2', 'v3', 'v4', 'v5']
SKIP = {'v4': [3]}          # паузы внутри сцены, которые не являются границей сцен
POSTER_SCENE = {'v1': 3, 'v2': 0, 'v3': 0, 'v4': 1, 'v5': 1}
if '--course' in ARGS:
    i = ARGS.index('--course'); croot = os.path.abspath(os.path.join(HERE, ARGS[i + 1])); del ARGS[i:i + 2]
    VDIR, OUT = os.path.join(croot, 'video'), os.path.join(croot, 'course', 'video')
    cfg = json.load(open(os.path.join(VDIR, 'video.json'))) if os.path.exists(os.path.join(VDIR, 'video.json')) else {}
    IDS, SKIP, POSTER_SCENE = cfg.get('ids', IDS), cfg.get('skip', {}), cfg.get('poster_scene', {})
    ENV['VIDEO_DIR'] = os.path.relpath(VDIR, HERE)
    if cfg.get('css'): ENV['VIDEO_CSS'] = ','.join(os.path.relpath(os.path.join(VDIR, c), HERE) for c in cfg['css'])

def duration(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).decode())

def silences(f, dur):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', f, '-af', 'silencedetect=noise=-38dB:d=1.25', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', err)]
    en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', err)]
    return [(a, b) for a, b in zip(st, en) if b < dur - 0.2]

def scene_counts():
    js = "global.window={};require(%s);require(%s);const o={};for(const k in window.VIDEOS)o[k]=window.VIDEOS[k].scenes.length;console.log(JSON.stringify(o))" % (json.dumps(os.path.join(HERE, 'lib.js')), json.dumps(os.path.join(VDIR, 'scenes.js')))
    return json.loads(subprocess.check_output(['node', '-e', js], cwd=HERE).decode())

def main():
    ids = ARGS or IDS
    counts, timings = scene_counts(), {}
    for v in IDS:
        mp3 = os.path.join(VDIR, 'vo', v + '.mp3'); dur = duration(mp3)
        sil = [s for i, s in enumerate(silences(mp3, dur)) if i not in SKIP.get(v, [])]
        assert len(sil) == counts[v] - 1, (v, len(sil), counts[v])
        total = round(dur + 0.6, 2)
        timings[v] = {'total': total, 'cuts': [0] + [round((a + b) / 2, 2) for a, b in sil] + [total]}
    with open(os.path.join(VDIR, 'timings.js'), 'w') as f:
        f.write('window.TIMINGS = ' + json.dumps(timings) + ';\n')
    if '--timings' in ids: return
    ids = [v for v in ids if not v.startswith('--')]
    os.makedirs(OUT, exist_ok=True)
    procs = []
    for v in ids:
        procs.append(subprocess.Popen(['node', 'render.cjs', v, os.path.join(OUT, v + '.mp4'), os.path.join(VDIR, 'vo', v + '.mp3')], cwd=HERE, env=ENV))
    for p in procs: p.wait()
    for v in ids:   # постеры
        c = timings[v]['cuts']; k = POSTER_SCENE.get(v, 0); t = round(c[k] + (c[k + 1] - c[k]) * 0.92, 2)
        subprocess.check_call(['node', 'render.cjs', v, '--shots', OUT, str(t)], cwd=HERE, env=ENV)
        src = os.path.join(OUT, '%s_%s.jpg' % (v, str(t).replace('.', '_')))
        os.replace(src, os.path.join(OUT, v + '.jpg'))
    print('done', ids)

if __name__ == '__main__':
    main()
