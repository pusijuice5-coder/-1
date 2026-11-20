import sys, zipfile, re, hashlib
from lxml import etree
A='http://schemas.openxmlformats.org/drawingml/2006/main'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
old, new = zipfile.ZipFile(sys.argv[1]), zipfile.ZipFile(sys.argv[2])
problems = []

def shape_texts(xml):
    root = etree.fromstring(xml)
    out = []
    for txb in root.iter('{%s}txBody' % P, '{%s}txBody' % A):
        paras = []
        for p in txb.findall('{%s}p' % A):
            s = ''
            for ch in p:
                tag = etree.QName(ch).localname
                if tag in ('r', 'fld'):
                    t = ch.find('{%s}t' % A); s += (t.text or '') if t is not None else ''
                elif tag == 'br':
                    s += '\n'
            paras.append(s)
        sp = txb.getparent()
        nv = sp.find('.//{%s}cNvPr' % P)
        out.append(((nv.get('id') if nv is not None else '?'), ' '.join(paras)))
    return out

def links(xml):
    root = etree.fromstring(xml)
    res = []
    for h in root.iter('{%s}hlinkClick' % A):
        res.append((h.get('action'), h.get('{%s}id' % R)))
    return res

names_old = set(old.namelist()); names_new = set(new.namelist())
slides = sorted([n for n in names_old if re.match(r'ppt/slides/slide\d+\.xml$', n)], key=lambda s: int(re.findall(r'\d+', s)[0]))
total_chars = 0
for s in slides:
    a = [x for x in shape_texts(old.read(s)) if x[1].strip()]; b = [x for x in shape_texts(new.read(s)) if x[1].strip()]
    ta = sorted(a); tb = sorted(b)
    total_chars += sum(len(t) for _, t in a)
    if ta != tb:
        problems.append(f'TEXT DIFF {s}: old={len(a)} new={len(b)}')
        for x in set(ta) ^ set(tb): problems.append(f'   {x!r:.200}')
    la, lb = links(old.read(s)), links(new.read(s))
    if sorted(map(str, la)) != sorted(map(str, lb)):
        problems.append(f'LINK DIFF {s}: {la} vs {lb}')
    # hyperlink rel targets
    ra = old.read(s.replace('slides/', 'slides/_rels/') + '.rels').decode()
    rb = new.read(s.replace('slides/', 'slides/_rels/') + '.rels').decode()
    def nonimg(r):
        return sorted(re.findall(r'Id="(rId\d+)" Type="([^"]+/(?:slide|hyperlink|notesSlide|tags|slideLayout))" Target="([^"]+)"', r)) + \
               sorted(re.findall(r'Id="(rId\d+)" Type="([^"]+/(?:slide|hyperlink|notesSlide|tags|slideLayout))" Target="([^"]+)" TargetMode', r))
    if nonimg(ra) != nonimg(rb):
        problems.append(f'REL DIFF {s}')
# untouched parts must be byte-identical
for n in sorted(names_old):
    if n.startswith(('ppt/notesSlides/', 'ppt/tags/', 'ppt/notesMasters/', 'ppt/slideLayouts/slideLayout', 'ppt/slideMasters/slideMaster', 'docProps/custom', 'ppt/presProps', 'ppt/commentAuthors')) and n.endswith('.xml'):
        if n not in names_new: problems.append(f'MISSING {n}'); continue
        if old.read(n) != new.read(n): problems.append(f'CHANGED {n}')
po = old.read('ppt/presentation.xml'); pn = new.read('ppt/presentation.xml')
if po != pn: problems.append('presentation.xml changed')
# iSpring slides byte-identical
for s in slides:
    if b'ISPRING_' in old.read(s) and old.read(s) != new.read(s):
        problems.append(f'ISPRING slide changed {s}')
print(f'slides: {len(slides)}  text shapes compared, total characters: {total_chars}')
print('PROBLEMS:' if problems else 'OK: all slide texts, notes, tags, slide IDs, hyperlinks and iSpring slides identical')
print('\n'.join(problems[:60]))
