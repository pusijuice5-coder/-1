#!/usr/bin/env python3
"""Убирает дубликаты картинок в .pptx (pptxgenjs вкладывает одну и ту же картинку заново на каждом слайде).
   python3 dedupe_media.py deck.pptx"""
import hashlib, os, re, sys, zipfile

def main(path):
    zin = zipfile.ZipFile(path)
    seen, remap = {}, {}
    for n in zin.namelist():
        if n.startswith('ppt/media/'):
            h = hashlib.sha1(zin.read(n)).hexdigest()
            if h in seen: remap[os.path.basename(n)] = os.path.basename(seen[h])
            else: seen[h] = n
    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
        for item in zin.infolist():
            name = item.filename
            if name.startswith('ppt/media/') and os.path.basename(name) in remap: continue
            data = zin.read(name)
            if name.startswith('ppt/slideLayouts/') and name.endswith('.xml'):
                data = re.sub(r'descr="[^"]*logo\.png"', 'descr="Логотип Ipak Yuli Bank"', data.decode('utf-8')).encode('utf-8')
            if name.endswith('.rels'):
                txt = data.decode('utf-8')
                txt = re.sub(r'media/([^"/]+)"', lambda m: 'media/%s"' % remap.get(m.group(1), m.group(1)), txt)
                data = txt.encode('utf-8')
            zout.writestr(item, data)
    os.replace(tmp, path)
    print('media: %d -> %d, %.1f MB' % (len(seen) + len(remap), len(seen), os.path.getsize(path) / 1e6))

if __name__ == '__main__':
    main(sys.argv[1])
