# -*- coding: utf-8 -*-
"""Скриншоты калькулятора для руководства: демонстрационная партия -> LibreOffice -> PNG в assets/."""
import os, subprocess, sys, tempfile
from PIL import Image, ImageChops
import demo_xlsx

HERE = os.path.dirname(os.path.abspath(__file__))
SOFFICE = '/root/.claude/skills/synced/575c671b-b53f-49f5-b380-b6cee68d875c_98f61f68-2023-4d1e-aff1-998e15c53ae4/xlsx/scripts/office/soffice.py'


def trim(im, pad=14):
    bg = Image.new('RGB', im.size, (255, 255, 255))
    box = ImageChops.difference(im.convert('RGB'), bg).getbbox()
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.size[0], box[2] + pad), min(im.size[1], box[3] + pad))
    return im.crop(box)


def main():
    tmp = tempfile.mkdtemp()
    path = demo_xlsx.fill(os.path.join(tmp, 'demo.xlsx'), 4)
    subprocess.run([sys.executable, SOFFICE, '--headless', '--convert-to', 'pdf', path], cwd=tmp, capture_output=True)
    pdf = os.path.join(tmp, 'demo.pdf')
    pages = {'year': 5, 'board': 8, 'final': 10, 'review': 11}
    for name, pg in pages.items():
        subprocess.run(['pdftoppm', '-r', '200', '-png', '-f', str(pg), '-l', str(pg), pdf, os.path.join(tmp, name)], check=True)
        f = [x for x in os.listdir(tmp) if x.startswith(name + '-') and x.endswith('.png')][0]
        im = trim(Image.open(os.path.join(tmp, f)))
        if name == 'year':            # верх листа: ввод и итоги
            im = im.crop((0, 0, im.size[0], int(im.size[1] * 0.50)))
        if name == 'final':
            im = im.crop((0, 0, im.size[0], int(im.size[1] * 0.62)))
        if name == 'review':
            im = im.crop((0, 0, im.size[0], int(im.size[1] * 0.52)))
        im = trim(im)
        im.save(os.path.join(HERE, 'assets', 'shot_%s.png' % name), optimize=True)
        print(name, im.size)


if __name__ == '__main__':
    main()
