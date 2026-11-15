#!/usr/bin/env python3
"""Сборка видеороликов курса: тайминги сцен по паузам озвучки -> покадровый рендер -> MP4 + постер.
   Запуск: python3 build.py [v1 v2 ...]"""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'course', 'video')
IDS = ['v1', 'v2', 'v3', 'v4', 'v5']
SKIP = {'v4': [3]}          # паузы внутри сцены, которые не являются границей сцен
POSTER_SCENE = {'v1': 3, 'v2': 0, 'v3': 0, 'v4': 1, 'v5': 1}

def duration(f):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).decode())

def silences(f, dur):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', f, '-af', 'silencedetect=noise=-38dB:d=1.25', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', err)]
    en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', err)]
    return [(a, b) for a, b in zip(st, en) if b < dur - 0.2]

def scene_counts():
    js = "global.window={};require('./scenes.js');const o={};for(const k in window.VIDEOS)o[k]=window.VIDEOS[k].scenes.length;console.log(JSON.stringify(o))"
    return json.loads(subprocess.check_output(['node', '-e', js], cwd=HERE).decode())

def main():
    ids = sys.argv[1:] or IDS
    counts, timings = scene_counts(), {}
    for v in IDS:
        mp3 = os.path.join(HERE, 'vo', v + '.mp3'); dur = duration(mp3)
        sil = [s for i, s in enumerate(silences(mp3, dur)) if i not in SKIP.get(v, [])]
        assert len(sil) == counts[v] - 1, (v, len(sil), counts[v])
        total = round(dur + 0.6, 2)
        timings[v] = {'total': total, 'cuts': [0] + [round((a + b) / 2, 2) for a, b in sil] + [total]}
    with open(os.path.join(HERE, 'timings.js'), 'w') as f:
        f.write('window.TIMINGS = ' + json.dumps(timings) + ';\n')
    if '--timings' in ids: return
    os.makedirs(OUT, exist_ok=True)
    procs = []
    for v in ids:
        procs.append(subprocess.Popen(['node', 'render.cjs', v, os.path.join(OUT, v + '.mp4'), os.path.join(HERE, 'vo', v + '.mp3')], cwd=HERE))
    for p in procs: p.wait()
    for v in ids:   # постеры
        c = timings[v]['cuts']; k = POSTER_SCENE[v]; t = round(c[k] + (c[k + 1] - c[k]) * 0.92, 2)
        subprocess.check_call(['node', 'render.cjs', v, '--shots', OUT, str(t)], cwd=HERE)
        src = os.path.join(OUT, '%s_%s.jpg' % (v, str(t).replace('.', '_')))
        os.replace(src, os.path.join(OUT, v + '.jpg'))
    print('done', ids)

if __name__ == '__main__':
    main()
