# -*- coding: utf-8 -*-
"""Готовит основу для слайдов из шаблона пользователя (We build Products):
оставляет один мастер и два макета, убирает слайды-образцы, перекрашивает тему в палитру банка.
Запуск: python3 make_base.py /путь/к/We_build_Products.pptx  ->  assets/base.pptx
"""
import sys, os, re
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'assets', 'base.pptx')
KEEP = ('Default Layout', 'No title layout')
THEME = dict(dk1='101F16', lt1='FFFFFF', dk2='101F16', lt2='F1F4F1', accent1='02691A', accent2='4CEA4C',
             accent3='F2A900', accent4='7A8B80', accent5='D9534F', accent6='1E9E45', hlink='02691A', folHlink='5E6E64')
FONT = 'Inter'


def main(src):
    prs = Presentation(src)
    # 1. слайды-образцы
    lst = prs.slides._sldIdLst
    for sld in list(lst):
        prs.part.drop_rel(sld.rId)
        lst.remove(sld)
    # 2. второй мастер
    mlst = prs.part._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}sldMasterIdLst')
    ns_r = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
    for m in list(mlst)[1:]:
        prs.part.drop_rel(m.get(ns_r))
        mlst.remove(m)
    master = prs.slide_masters[0]
    # 3. лишние макеты
    for layout in list(master.slide_layouts):
        if layout.name not in KEEP:
            master.slide_layouts.remove(layout)
    # 4. мастер: убираем фирменную полоску шаблона, заголовок крупнее и жирный
    tree = master.shapes._spTree
    for sp in list(tree):
        nm = sp.xpath('.//p:cNvPr/@name')
        if nm and nm[0] in ('Straight Connector 10', 'Rectangle 6'):
            tree.remove(sp)
    for el in [master._element] + [l._element for l in master.slide_layouts]:   # анимация удалённых фигур
        for tm in el.xpath('./p:timing'):
            el.remove(tm)
    for rpr in master._element.xpath('.//p:titleStyle/a:lvl1pPr/a:defRPr'):
        rpr.set('sz', '2800')
        rpr.set('b', '1')
    for layout in master.slide_layouts:
        for sp in list(layout.shapes._spTree):
            nm = sp.xpath('.//p:cNvPr/@name')
            if nm and nm[0] in ('Straight Connector 10', 'Rectangle 6'):
                layout.shapes._spTree.remove(sp)
    # 5. тема: цвета и шрифт
    theme = master.part.part_related_by(RT.THEME)
    x = theme.blob.decode('utf8')
    for k, v in THEME.items():
        x = re.sub(r'(<a:%s>\s*<a:srgbClr val=")[0-9A-Fa-f]{6}(")' % k, r'\g<1>%s\g<2>' % v, x)
        x = re.sub(r'(<a:%s>\s*)<a:sysClr val="[^"]*" lastClr="[0-9A-Fa-f]{6}"/>' % k, r'\g<1><a:srgbClr val="%s"/>' % v, x)
    x = re.sub(r'(<a:majorFont>\s*<a:latin typeface=")[^"]*(")', r'\g<1>%s\g<2>' % FONT, x)
    x = re.sub(r'(<a:minorFont>\s*<a:latin typeface=")[^"]*(")', r'\g<1>%s\g<2>' % FONT, x)
    x = re.sub(r'<a:clrScheme name="[^"]*"', '<a:clrScheme name="Ipak Yuli"', x)
    theme._blob = x.encode('utf8')
    prs.core_properties.title = ''
    prs.core_properties.author = ''
    prs.core_properties.last_modified_by = ''
    prs.save(OUT)
    print('base saved', OUT, os.path.getsize(OUT) // 1024, 'KB')


if __name__ == '__main__':
    main(sys.argv[1])
