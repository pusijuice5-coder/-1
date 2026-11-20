# -*- coding: utf-8 -*-
"""Restyle the OVZ course deck in place: design only, text untouched.

usage: python3 build.py <unpacked_src_dir> <assets_dir> <out_dir>
"""
import os, re, sys, shutil, copy, math
from lxml import etree
from PIL import Image

SRC, ASSETS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'a14': 'http://schemas.microsoft.com/office/drawing/2010/main',
    'pr': 'http://schemas.openxmlformats.org/package/2006/relationships',
    'ct': 'http://schemas.openxmlformats.org/package/2006/content-types',
}
A = '{%s}' % NS['a']; P = '{%s}' % NS['p']; R = '{%s}' % NS['r']
EMU = 914400
REL_IMG = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'

# ---------------- palette ----------------
DG = '02691A'      # brand dark green
LG = '4CEA4C'      # brand lime
INK = '10261A'     # text on light
PALE = 'E4F5E3'    # pale mint surface
OVERLAY = '05351A' # dim overlay
GRAYLINE = 'C9D3CB'

DARK_SLIDES = {1, 2, 53, 102}
SECTION_SLIDES = {3, 4, 8, 9, 10, 34, 36, 37, 39, 42, 46, 50, 54, 58, 59, 60, 83, 85, 86, 88, 91, 95, 99}

# ---------------- helpers ----------------
def q(tag):
    pre, t = tag.split(':')
    return '{%s}%s' % (NS[pre], t)

def lum(hexc):
    r, g, b = (int(hexc[i:i+2], 16)/255 for i in (0, 2, 4))
    return 0.2126*r + 0.7152*g + 0.0722*b

SCHEME_HEX = {'bg1': 'FFFFFF', 'lt1': 'FFFFFF', 'tx1': '000000', 'dk1': '000000',
              'bg2': 'E7E6E6', 'lt2': 'E7E6E6', 'tx2': '44546A', 'dk2': '44546A',
              'accent1': DG, 'accent2': LG, 'accent6': DG}

FILL_TAGS = [q('a:noFill'), q('a:solidFill'), q('a:gradFill'), q('a:blipFill'), q('a:pattFill'), q('a:grpFill')]

def color_el_info(c):
    """returns (hex, alpha) for a color element (srgbClr/schemeClr/sysClr/prstClr)"""
    tag = etree.QName(c).localname
    if tag == 'srgbClr':
        hx = c.get('val').upper()
    elif tag == 'schemeClr':
        hx = SCHEME_HEX.get(c.get('val'), '808080')
    elif tag == 'sysClr':
        hx = (c.get('lastClr') or '000000').upper()
    else:
        hx = '000000'
    a = c.find('a:alpha', NS)
    alpha = int(a.get('val'))/100000 if a is not None else 1.0
    # crude lumMod/lumOff handling
    lm = c.find('a:lumMod', NS); lo = c.find('a:lumOff', NS)
    if lm is not None or lo is not None:
        r, g, b = (int(hx[i:i+2], 16) for i in (0, 2, 4))
        m = int(lm.get('val'))/100000 if lm is not None else 1
        o = int(lo.get('val'))/100000 if lo is not None else 0
        r, g, b = (min(255, int(v*m + 255*o)) for v in (r, g, b))
        hx = '%02X%02X%02X' % (r, g, b)
    return hx, alpha

def get_fill(spPr):
    """('solid', hex, alpha) | ('none',) | ('grp',) | ('blip',) | ('grad',) | None"""
    if spPr is None:
        return None
    for ch in spPr:
        if ch.tag == q('a:solidFill'):
            hx, al = color_el_info(ch[0]) if len(ch) else ('000000', 1)
            return ('solid', hx, al)
        if ch.tag == q('a:noFill'):
            return ('none',)
        if ch.tag == q('a:grpFill'):
            return ('grp',)
        if ch.tag == q('a:blipFill'):
            return ('blip',)
        if ch.tag == q('a:gradFill'):
            return ('grad',)
    return None

def orig_fill_color_tag(spPr):
    """raw color descriptor of original solid fill e.g. '7800FF' or 'tx1'"""
    if spPr is None: return None
    sf = spPr.find('a:solidFill', NS)
    if sf is None or not len(sf): return None
    c = sf[0]
    return (c.get('val') or '').upper() if etree.QName(c).localname == 'srgbClr' else c.get('val')

def remove_fills(spPr):
    for ch in list(spPr):
        if ch.tag in FILL_TAGS:
            spPr.remove(ch)

def fill_insert_index(spPr):
    idx = 0
    for i, ch in enumerate(spPr):
        if ch.tag in (q('a:xfrm'), q('a:custGeom'), q('a:prstGeom')):
            idx = i + 1
    return idx

def set_solid(spPr, hexc, alpha=None):
    remove_fills(spPr)
    sf = etree.Element(q('a:solidFill'))
    c = etree.SubElement(sf, q('a:srgbClr'), val=hexc)
    if alpha is not None:
        etree.SubElement(c, q('a:alpha'), val=str(int(alpha*100000)))
    spPr.insert(fill_insert_index(spPr), sf)

def set_nofill(spPr):
    remove_fills(spPr)
    spPr.insert(fill_insert_index(spPr), etree.Element(q('a:noFill')))

def get_line(spPr):
    if spPr is None: return None
    ln = spPr.find('a:ln', NS)
    if ln is None: return None
    sf = ln.find('a:solidFill', NS)
    if sf is not None and len(sf):
        return color_el_info(sf[0])[0]
    if ln.find('a:noFill', NS) is not None:
        return 'none'
    return None

def set_line(spPr, hexc, width=None):
    ln = spPr.find('a:ln', NS)
    if ln is None:
        ln = etree.Element(q('a:ln'))
        # insert after fill
        idx = fill_insert_index(spPr)
        for i, ch in enumerate(spPr):
            if ch.tag in FILL_TAGS: idx = i + 1
        spPr.insert(idx, ln)
    if width is not None:
        ln.set('w', str(int(width)))
    for ch in list(ln):
        if ch.tag in (q('a:noFill'), q('a:solidFill'), q('a:gradFill'), q('a:pattFill')):
            ln.remove(ch)
    sf = etree.Element(q('a:solidFill'))
    etree.SubElement(sf, q('a:srgbClr'), val=hexc)
    ln.insert(0, sf)

def set_shadow(spPr, blur=320000, dist=60000, alpha=20):
    for ch in list(spPr):
        if ch.tag in (q('a:effectLst'), q('a:effectDag')):
            spPr.remove(ch)
    eff = etree.fromstring(
        '<a:effectLst xmlns:a="%s"><a:outerShdw blurRad="%d" dist="%d" dir="5400000" algn="t" rotWithShape="0">'
        '<a:srgbClr val="0B2A17"><a:alpha val="%d"/></a:srgbClr></a:outerShdw></a:effectLst>' % (NS['a'], blur, dist, alpha*1000))
    idx = fill_insert_index(spPr)
    for i, ch in enumerate(spPr):
        if ch.tag in FILL_TAGS or ch.tag == q('a:ln'): idx = i + 1
    spPr.insert(idx, eff)

def geom(spPr):
    if spPr is None: return ''
    g = spPr.find('a:prstGeom', NS)
    if g is not None: return g.get('prst')
    if spPr.find('a:custGeom', NS) is not None: return 'cust'
    return ''

def set_roundrect(spPr, adj=50000):
    g = spPr.find('a:prstGeom', NS)
    if g is None or g.get('prst') != 'rect': return
    g.set('prst', 'roundRect')
    av = g.find('a:avLst', NS)
    if av is None:
        av = etree.SubElement(g, q('a:avLst'))
    for ch in list(av): av.remove(ch)
    etree.SubElement(av, q('a:gd'), name='adj', fmla='val %d' % adj)

# ---------------- geometry (absolute bboxes) ----------------
def xfrm_of(el):
    tag = etree.QName(el).localname
    if tag == 'grpSp':
        return el.find('p:grpSpPr/a:xfrm', NS)
    if tag == 'graphicFrame':
        return el.find('p:xfrm', NS)
    return el.find('p:spPr/a:xfrm', NS)

def walk(container, tf=(0, 0, 1, 1), out=None, parents=()):
    """flatten shapes in z-order with absolute bbox (inches). tf maps child->abs: X = ax + x*sx"""
    if out is None: out = []
    ax, ay, sx, sy = tf
    for el in container:
        tag = etree.QName(el).localname
        if tag not in ('sp', 'pic', 'grpSp', 'cxnSp', 'graphicFrame'):
            continue
        xf = xfrm_of(el)
        bbox = None
        if xf is not None and xf.find('a:off', NS) is not None:
            o = xf.find('a:off', NS); e = xf.find('a:ext', NS)
            x, y = int(o.get('x')), int(o.get('y')); w, h = int(e.get('cx')), int(e.get('cy'))
            bbox = ((ax + x*sx)/EMU, (ay + y*sy)/EMU, w*sx/EMU, h*sy/EMU)
        out.append({'el': el, 'tag': tag, 'bbox': bbox, 'parents': parents})
        if tag == 'grpSp' and xf is not None and xf.find('a:chOff', NS) is not None:
            o = xf.find('a:off', NS); e = xf.find('a:ext', NS)
            co = xf.find('a:chOff', NS); ce = xf.find('a:chExt', NS)
            cw, ch_ = int(ce.get('cx')) or 1, int(ce.get('cy')) or 1
            ksx = int(e.get('cx'))/cw; ksy = int(e.get('cy'))/ch_
            nax = ax + (int(o.get('x')) - int(co.get('x'))*ksx)*sx
            nay = ay + (int(o.get('y')) - int(co.get('y'))*ksy)*sy
            walk(el, (nax, nay, sx*ksx, sy*ksy), out, parents + (el,))
    return out

def name_of(el):
    nv = el.find('.//p:cNvPr', NS)
    return nv.get('name', '') if nv is not None else ''

def is_hidden(el):
    nv = el.find('.//p:cNvPr', NS)
    return nv is not None and nv.get('hidden') == '1'

def spPr_of(el):
    tag = etree.QName(el).localname
    if tag == 'grpSp':
        return el.find('p:grpSpPr', NS)
    return el.find('p:spPr', NS)

# ---------------- package helpers ----------------
class Rels:
    def __init__(self, path):
        self.path = path
        self.tree = etree.parse(path)
        self.root = self.tree.getroot()
    def get(self, rid):
        for r in self.root:
            if r.get('Id') == rid: return r
    def target(self, rid):
        r = self.get(rid)
        return r.get('Target') if r is not None else None
    def add_image(self, media_name):
        for r in self.root:
            if r.get('Type') == REL_IMG and r.get('Target') == '../media/' + media_name:
                return r.get('Id')
        ids = {r.get('Id') for r in self.root}
        n = 1
        while 'rId%d' % n in ids: n += 1
        rid = 'rId%d' % n
        etree.SubElement(self.root, '{%s}Relationship' % NS['pr'], Id=rid, Type=REL_IMG, Target='../media/' + media_name)
        return rid
    def save(self):
        self.tree.write(self.path, xml_declaration=True, encoding='UTF-8', standalone=True)

# ---------------- media analysis ----------------
SAT = {}
def media_sat(name):
    if name in SAT: return SAT[name]
    p = os.path.join(SRC, 'ppt', 'media', name)
    try:
        im = Image.open(p).convert('RGB'); im.thumbnail((128, 128))
        s = sum(im.convert('HSV').getchannel('S').tobytes())/(im.width*im.height)/255
    except Exception:
        s = 1.0
    SAT[name] = s
    return s

BIG_MAP = {'image25.jpeg': 'step1', 'image29.JPG': 'step2', 'image20.jpg': 'step3', 'image33.bmp': 'step4',
           'image35.jpg': 'step5', 'image36.jpg': 'step6', 'image40.png': 'storage', 'image44.jpeg': 'funds',
           'image37.png': 'transfer', 'image39.jpg': 'close', 'image45.jpeg': 'currency'}
OPS_MAP = {'image43.jpeg': 'funds', 'image44.jpeg': 'funds', 'image37.png': 'transfer', 'image39.jpg': 'close',
           'image38.jpg': 'currency', 'image45.jpeg': 'currency', 'image40.png': 'storage'}
CHAR_MAP = {'image4.png': 'ovz_char_present.png', 'image5.png': 'ovz_char_hands.png', 'image47.png': 'ovz_char_point.png'}
ISPRING_MEDIA = {'image11.png', 'image12.png', 'image30.png', 'image41.png', 'image42.png', 'image46.png',
                 'image49.png', 'image51.png', 'image53.png', 'image54.png'}

def img_size(name):
    return Image.open(os.path.join(ASSETS, name)).size

# ---------------- picture replacement ----------------
def replace_blip(pic, rid):
    bf = pic.find('p:blipFill', NS)
    old = bf.find('a:blip', NS)
    new = etree.Element(q('a:blip'))
    new.set(R + 'embed', rid)
    bf.replace(old, new)
    src = bf.find('a:srcRect', NS)
    if src is not None: bf.remove(src)
    if bf.find('a:stretch', NS) is None and bf.find('a:tile', NS) is None:
        st = etree.SubElement(bf, q('a:stretch')); etree.SubElement(st, q('a:fillRect'))
    spPr = pic.find('p:spPr', NS)
    if spPr is not None:
        for ch in list(spPr):
            if ch.tag == q('a:blipFill'):
                spPr.remove(ch)

def set_xfrm_abs(el, x, y, w, h):
    xf = xfrm_of(el)
    xf.find('a:off', NS).set('x', str(int(x*EMU))); xf.find('a:off', NS).set('y', str(int(y*EMU)))
    xf.find('a:ext', NS).set('cx', str(int(w*EMU))); xf.find('a:ext', NS).set('cy', str(int(h*EMU)))

def new_pic(tree, rid, name, x, y, w, h, descr=''):
    ids = [int(e.get('id')) for e in tree.iter(q('p:cNvPr')) if (e.get('id') or '').isdigit()]
    nid = max(ids + [1]) + 1
    xml = ('<p:pic xmlns:p="%s" xmlns:a="%s" xmlns:r="%s"><p:nvPicPr><p:cNvPr id="%d" name="%s" descr="%s"/>'
           '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
           '<p:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
           '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
           '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>') % (
        NS['p'], NS['a'], NS['r'], nid, name, descr, rid, int(x*EMU), int(y*EMU), int(w*EMU), int(h*EMU))
    return etree.fromstring(xml)

# ---------------- text helpers ----------------
def run_props(r):
    rPr = r.find('a:rPr', NS)
    if rPr is None:
        rPr = etree.Element(q('a:rPr'))
        r.insert(0, rPr)
    return rPr

def run_color_raw(rPr):
    sf = rPr.find('a:solidFill', NS)
    if sf is not None and len(sf):
        c = sf[0]
        return (c.get('val') or '').upper() if etree.QName(c).localname == 'srgbClr' else c.get('val')
    return None

def set_run_color(rPr, hexc):
    for ch in list(rPr):
        if ch.tag in FILL_TAGS:
            rPr.remove(ch)
    sf = etree.Element(q('a:solidFill'))
    etree.SubElement(sf, q('a:srgbClr'), val=hexc)
    idx = 0
    for i, ch in enumerate(rPr):
        if ch.tag == q('a:ln'): idx = i + 1
    rPr.insert(idx, sf)

def eff_size(txBody, r):
    rPr = r.find('a:rPr', NS)
    if rPr is not None and rPr.get('sz'):
        return int(rPr.get('sz'))
    # paragraph level / list style
    lst = txBody.find('a:lstStyle', NS)
    if lst is not None:
        d = lst.find('a:lvl1pPr/a:defRPr', NS)
        if d is not None and d.get('sz'):
            return int(d.get('sz'))
    return 1800

def is_bold(txBody, r):
    rPr = r.find('a:rPr', NS)
    if rPr is not None and rPr.get('b') is not None:
        return rPr.get('b') == '1'
    lst = txBody.find('a:lstStyle', NS)
    if lst is not None:
        d = lst.find('a:lvl1pPr/a:defRPr', NS)
        if d is not None and d.get('b') is not None:
            return d.get('b') == '1'
    return False

def text_of(el):
    return ''.join(t.text or '' for t in el.iter(q('a:t')))

# ---------------- main per-slide transform ----------------
LOG = []
POS_FIX = {
    60: [('Group 3', 0, -0.95, 0.55), ('TextBox 31', 0, -0.95, 0)],
    99: [('Group 3', 0, -0.62, 0.32), ('TextBox 31', 0, -0.62, 0)],
    90: [('Group 3', 4.26, -2.83, 0), ('TextBox 21', 4.26, -2.83, 0)],
    67: [('Group 3', 0, -0.45, 0), ('TextBox 11', 0, -0.45, 0)],
    81: [('Group 3', 0, -0.55, 0.15), ('TextBox 14', 0, -0.55, 0)],
    83: [('Group 3', 0, -0.75, 0.50), ('TextBox 31', 0, -0.75, 0)],
}

def classify_surface(info):
    """after recolor: return 'dark'/'light'/None for shape as a surface"""
    el = info['el']
    if is_hidden(el): return None
    tag = info['tag']
    if tag == 'pic':
        bf = el.find('p:blipFill/a:blip', NS)
        return 'light' if bf is not None else None
    if tag in ('cxnSp', 'graphicFrame'):
        return None
    spPr = spPr_of(el)
    f = get_fill(spPr)
    if f is None:
        return None
    if f[0] == 'grp':
        # resolve from parents
        for par in reversed(info['parents']):
            pf = get_fill(par.find('p:grpSpPr', NS))
            if pf and pf[0] == 'solid':
                f = pf; break
            if pf and pf[0] != 'grp':
                return None
        else:
            return None
        if f[0] != 'solid': return None
    if f[0] == 'solid':
        hx, al = f[1], f[2]
        if al < 0.5: return None
        return 'dark' if lum(hx) < 0.45 else 'light'
    if f[0] == 'blip':
        return 'light'
    return None

def contains(b, x, y):
    return b is not None and b[0] <= x <= b[0] + b[2] and b[1] <= y <= b[1] + b[3]

def process_slide(n, theme_dark):
    sp = os.path.join(OUT, 'ppt', 'slides', 'slide%d.xml' % n)
    tree = etree.parse(sp)
    root = tree.getroot()
    rels = Rels(os.path.join(OUT, 'ppt', 'slides', '_rels', 'slide%d.xml.rels' % n))
    spTree = root.find('p:cSld/p:spTree', NS)
    names = [e.get('name', '') for e in spTree.iter(q('p:cNvPr'))]
    if any('ISPRING_' in nm for nm in names):
        LOG.append('slide %d: iSpring object, untouched' % n)
        return
    dark = n in DARK_SLIDES
    shapes = walk(spTree)

    # ---------- slide type hints ----------
    has_big_pic = any(s['tag'] == 'pic' and s['bbox'] and s['bbox'][2] > 6 for s in shapes)
    overview_steps = sum(1 for s in shapes if s['tag'] == 'pic' and s['bbox'] and 1.7 < s['bbox'][2] < 2.2) >= 6
    texts_all = text_of(spTree)

    # ---------- background ----------
    bgname = 'ovz_bg_dark.jpg' if dark else ('ovz_bg_light_b.jpg' if (overview_steps or n in SECTION_SLIDES) else 'ovz_bg_light_a.jpg')
    rid_bg = rels.add_image(bgname)
    cSld = root.find('p:cSld', NS)
    old_bg = cSld.find('p:bg', NS)
    new_bg = etree.fromstring('<p:bg xmlns:p="%s" xmlns:a="%s" xmlns:r="%s"><p:bgPr><a:blipFill dpi="0" rotWithShape="1">'
                              '<a:blip r:embed="%s"/><a:srcRect/><a:stretch><a:fillRect/></a:stretch></a:blipFill>'
                              '<a:effectLst/></p:bgPr></p:bg>' % (NS['p'], NS['a'], NS['r'], rid_bg))
    if old_bg is not None:
        cSld.replace(old_bg, new_bg)
    else:
        cSld.insert(0, new_bg)

    # ---------- shape recolor ----------
    first_overlay = None
    for s in shapes:
        el, tag, b = s['el'], s['tag'], s['bbox']
        spPr = spPr_of(el)
        nm = name_of(el)
        if spPr is None or b is None:
            continue
        x, y, w, h = b
        g = geom(spPr)
        if tag in ('sp', 'grpSp'):
            raw = orig_fill_color_tag(spPr)
            f = get_fill(spPr)
            if f and f[0] == 'solid':
                hx, al = f[1], f[2]
                if raw in ('7800FF', '071647', '5D1EB2', '1B2232', '243762'):
                    if al < 0.05:
                        pass  # transparent ring: only line recolor below
                    elif w >= 12.9 and h >= 7.0:
                        set_nofill(spPr)
                    elif n in DARK_SLIDES and w >= 4 and (g == 'cust' or x > 8):
                        set_nofill(spPr)
                    elif w >= 11.5 and h <= 3.0 and y <= 0.25:
                        set_nofill(spPr)          # header bar -> airy title
                    elif w >= 11.5 and y < -1.0:
                        set_nofill(spPr)          # parked header shape
                    elif g == 'triangle' and y < 3.5 and w < 1:
                        set_nofill(spPr)          # speech pointer of header bubble
                    elif g == 'ellipse' and w >= 8:
                        if n in (8, 58):
                            set_solid(spPr, DG)
                        elif has_big_pic:
                            set_solid(spPr, LG)   # lime ring around illustration disc
                        else:
                            set_solid(spPr, PALE)
                    elif 1.9 <= w <= 2.6 and 0.5 <= h <= 0.85 and g in ('rect', 'roundRect'):
                        set_solid(spPr, LG if dark else DG)
                        set_roundrect(spPr)
                    else:
                        set_solid(spPr, DG)
                elif raw == '5773B8':
                    set_solid(spPr, LG, 0.5)
                elif raw in ('tx1',) and al < 0.9 and w >= 12.9 and h >= 7.0:
                    set_solid(spPr, OVERLAY, 0.55)
                    if first_overlay is None and not s['parents']:
                        first_overlay = el
                elif raw == 'FFFFFF' and g == 'cust':
                    set_shadow(spPr)
                elif raw == 'bg1' and tag == 'grpSp':
                    set_solid(spPr, LG)   # number discs on contents slides
                elif raw == '4472C4' and al < 0.05:
                    ln = spPr.find('a:ln', NS)
                    if ln is None:
                        set_line(spPr, 'FFFFFF')
                        ln = spPr.find('a:ln', NS)
                    for ch in list(ln): ln.remove(ch)
                    etree.SubElement(ln, q('a:noFill'))
                    continue
            # lines
            lc = get_line(spPr)
            if lc and lc != 'none':
                lraw = spPr.find('a:ln/a:solidFill', NS)[0]
                lval = lraw.get('val')
                if lval in ('bg1', 'lt1') or (lval or '').upper() == 'FFFFFF':
                    fnow = get_fill(spPr)
                    if g == 'ellipse' and (fnow is None or (fnow[0] == 'solid' and fnow[2] < 0.05) or fnow[0] == 'none'):
                        set_line(spPr, LG)
                    elif dark:
                        pass
                    elif g != 'ellipse':
                        set_line(spPr, DG)
                elif (lval or '').upper() in ('7800FF', '071647', '243762'):
                    set_line(spPr, DG)
        elif tag == 'cxnSp':
            lc = get_line(spPr)
            if lc and lc.upper() in ('7800FF', '071647'):
                set_line(spPr, DG)

    # ---------- pictures ----------
    contents_group = None
    for s in shapes:
        el, tag, b = s['el'], s['tag'], s['bbox']
        if tag != 'pic' or b is None:
            continue
        blip = el.find('p:blipFill/a:blip', NS)
        if blip is None:
            continue
        target = rels.target(blip.get(R + 'embed')) or ''
        media = target.split('/')[-1]
        if media in ISPRING_MEDIA or media == 'image2.png':
            continue
        x, y, w, h = b
        spPr = el.find('p:spPr', NS)
        raw_blip = etree.tostring(blip)
        if media == 'image1.png':           # logo
            lname = 'ovz_logo_ondark.png' if dark else 'ovz_logo_color.png'
            rid = rels.add_image(lname)
            replace_blip(el, rid)
            iw, ih = img_size(lname)
            nw = 2.25; nh = nw*ih/iw
            if s['parents']:
                continue
            set_xfrm_abs(el, 13.333 - 0.5 - nw, 0.42, nw, nh)
            continue
        if media in CHAR_MAP:
            cname = CHAR_MAP[media]
            rid = rels.add_image(cname)
            replace_blip(el, rid)
            iw, ih = img_size(cname)
            nh = h; nw = nh*iw/ih
            cx = x + w/2
            set_xfrm_abs(el, cx - nw/2, y + h - nh, nw, nh)
            continue
        if media in ('image6.png', 'image8.png', 'image10.png', 'image48.png'):
            if s['parents']:
                contents_group = s['parents'][0]
            else:
                el.getparent().remove(el)
            continue
        if media == 'image3.png':
            if os.path.exists(os.path.join(ASSETS, 'ovz_nav_screen.png')):
                rid = rels.add_image('ovz_nav_screen.png')
                replace_blip(el, rid)
            continue
        # discs
        bw = (b'grayscl' in raw_blip or b'duotone' in raw_blip or b'saturation sat="0"' in raw_blip
              or media_sat(media) < 0.06)
        if w > 6:
            subj = BIG_MAP.get(media)
            if not subj:
                LOG.append('slide %d: unmapped big pic %s' % (n, media)); continue
            rid = rels.add_image('ovz_big_%s.jpg' % subj)
            replace_blip(el, rid)
            if spPr.find('a:ln', NS) is not None:
                ln = spPr.find('a:ln', NS)
                for ch in list(ln): ln.remove(ch)
                etree.SubElement(ln, q('a:noFill'))
            continue
        if 1.5 < w < 3.2:
            if 1.7 < w < 2.2:   # steps overview grid
                col = min(2, max(0, int(round((x - 1.8)/3.85))))
                row = 0 if y < 3.2 else 1
                subj = 'step%d' % (row*3 + col + 1)
            else:
                subj = OPS_MAP.get(media)
                if not subj:
                    LOG.append('slide %d: unmapped small pic %s' % (n, media)); continue
            dname = 'ovz_disc_%s%s.jpg' % (subj, '_bw' if bw else '')
            rid = rels.add_image(dname)
            replace_blip(el, rid)
            set_line(spPr, GRAYLINE if bw else LG, 19050)
            continue
        LOG.append('slide %d: untouched pic %s (%.1fx%.1f)' % (n, media, w, h))

    # contents illustration: swap the whole plant+monitor group
    if contents_group is not None:
        rid = rels.add_image('ovz_contents.png')
        iw, ih = img_size('ovz_contents.png')
        nw = 6.0; nh = nw*ih/iw
        pic = new_pic(tree, rid, 'OVZ Иллюстрация содержания', 0.35, 2.95, nw, nh, 'Иллюстрация: экран курса с двумя главами')
        contents_group.getparent().replace(contents_group, pic)

    # ---------- layout fixes (cards that were partly off-slide in the source) ----------
    for (nm_, dx, dy, dh) in POS_FIX.get(n, []):
        for el in list(spTree):
            if etree.QName(el).localname in ('sp', 'grpSp') and name_of(el) == nm_:
                xf = xfrm_of(el)
                o = xf.find('a:off', NS); e = xf.find('a:ext', NS)
                o.set('x', str(int(int(o.get('x')) + dx*EMU))); o.set('y', str(int(int(o.get('y')) + dy*EMU)))
                if dh: e.set('cy', str(int(int(e.get('cy')) + dh*EMU)))
                LOG.append('slide %d: moved %s by (%.2f, %.2f)' % (n, nm_, dx, dy))
                break

    # ---------- additions ----------
    def insert_decor(pic_el):
        if first_overlay is not None:
            first_overlay.addprevious(pic_el)
        else:
            spTree.append(pic_el)

    if n == 3:
        rid = rels.add_image('ovz_globe.png'); iw, ih = img_size('ovz_globe.png')
        nh = 2.15; nw = nh*iw/ih
        insert_decor(new_pic(tree, rid, 'OVZ Глобус', 6.667 - nw/2, 5.05, nw, nh, 'Иллюстрация: глобус'))
    if n in (53, 102):
        rid = rels.add_image('ovz_char_celeb.png'); iw, ih = img_size('ovz_char_celeb.png')
        nh = 5.45; nw = nh*iw/ih
        insert_decor(new_pic(tree, rid, 'OVZ Персонаж празднует', 11.72 - nw/2, 7.5 - nh - 0.08, nw, nh, 'Иллюстрация: сотрудник банка радуется'))
    if n in (12, 13, 62, 63):
        rid = rels.add_image('ovz_residents.png'); iw, ih = img_size('ovz_residents.png')
        nh = 2.15; nw = nh*iw/ih
        insert_decor(new_pic(tree, rid, 'OVZ Резиденты', 9.35, 5.2, nw, nh, 'Иллюстрация: паспорт, глобус и метка на карте'))
    if n in (48, 49, 97, 98):
        rid = rels.add_image('ovz_sanctions.png'); iw, ih = img_size('ovz_sanctions.png')
        nh = 2.0; nw = nh*iw/ih
        insert_decor(new_pic(tree, rid, 'OVZ Санкционный контроль', 13.333 - 0.25 - nw, 5.28, nw, nh, 'Иллюстрация: щит и контроль операций'))

    # ---------- text colours ----------
    shapes = walk(spTree)
    for i, s in enumerate(shapes):
        el = s['el']
        if s['tag'] not in ('sp',):
            continue
        tb = el.find('p:txBody', NS)
        if tb is None or not text_of(tb).strip():
            continue
        b = s['bbox']
        surf = classify_surface(s)
        if surf is None and b is not None:
            cx, cy = b[0] + b[2]/2, b[1] + min(b[3]/2, 0.45)
            for j in range(i - 1, -1, -1):
                o = shapes[j]
                if o['el'] in s['parents']:
                    continue
                if contains(o['bbox'], cx, cy):
                    sf = classify_surface(o)
                    if sf:
                        surf = sf; break
        if surf is None:
            surf = 'dark' if dark else 'light'
        runs = [r for r in tb.iter(q('a:r'), q('a:fld'))]
        sizes = [eff_size(tb, r) for r in runs if (r.findtext('a:t', namespaces=NS) or '').strip()]
        heading = bool(sizes) and (min(sizes) >= 2600 or (min(sizes) >= 2400 and all(is_bold(tb, r) for r in runs if (r.findtext('a:t', namespaces=NS) or '').strip())))
        for r in runs:
            rPr = run_props(r)
            if rPr.find('a:hlinkClick', NS) is not None:
                continue
            raw = run_color_raw(rPr)
            t = (r.findtext('a:t', namespaces=NS) or '').strip()
            if raw in ('7800FF', '5D1EB2'):
                set_run_color(rPr, LG if surf == 'dark' else DG)
            elif surf == 'dark':
                set_run_color(rPr, 'FFFFFF')
            else:
                if heading or t in ('Важно!', 'Muhim!', 'Важно', 'Muhim'):
                    set_run_color(rPr, DG)
                else:
                    set_run_color(rPr, INK)

    # ---------- "important" icons on cards ----------
    shapes = walk(spTree)
    for i, s in enumerate(shapes):
        el = s['el']
        if s['tag'] != 'sp' or s['parents']:
            continue
        tb = el.find('p:txBody', NS)
        if tb is None: continue
        first = ''
        for p_ in tb.findall('a:p', NS):
            first = text_of(p_).strip()
            if first: break
        if not (first.startswith('Важно') or first.startswith('Muhim')):
            continue
        b = s['bbox']
        cx, cy = b[0] + 0.3, b[1] + 0.3
        card = None
        for j in range(i - 1, -1, -1):
            o = shapes[j]
            if o['tag'] == 'sp' and contains(o['bbox'], cx, cy):
                f = get_fill(spPr_of(o['el']))
                if f and f[0] == 'solid' and f[1] == 'FFFFFF':
                    card = o; break
        cb = card['bbox'] if card else b
        rid = rels.add_image('ovz_icon_important.png'); iw, ih = img_size('ovz_icon_important.png')
        sz = 0.56
        others = [o['bbox'] for o in shapes if o['tag'] == 'sp' and o['el'] is not el and o['bbox'] is not None
                  and o['el'].find('p:txBody', NS) is not None and text_of(o['el']).strip()
                  and not is_hidden(o['el'])]
        def inter(ix, iy, ob):
            return ix < ob[0] + ob[2] and ix + sz > ob[0] and iy < ob[1] + ob[3] and iy + sz > ob[1]
        own = (b[0], b[1] + 0.30, b[2], max(0.01, b[3] - 0.30))   # own text below the 'Важно!' line
        def score(ix, iy):
            sc = 0
            for ob in others:
                if ob[2] > 12 and ob[3] > 7: continue
                if inter(ix, iy, ob): sc += 3
            if inter(ix, iy, own): sc += 2
            if ix < 0.03 or iy < 0.03 or ix + sz > 13.30 or iy + sz > 7.47: sc += 5
            return sc
        cands = [(cb[0] + cb[2] - sz*0.45, cb[1] - sz*0.85),
                 (cb[0] - sz*0.55, cb[1] - sz*0.85),
                 (cb[0] - sz*0.90, cb[1] + 0.02),
                 (cb[0] + cb[2] - sz*0.10, cb[1] + 0.02),
                 (cb[0] + cb[2] - sz - 0.08, cb[1] + 0.08)]
        ix, iy = min(cands, key=lambda c: (score(*c), cands.index(c)))
        ix = min(max(ix, 0.04), 13.333 - sz - 0.04); iy = min(max(iy, 0.04), 7.5 - sz - 0.04)
        el.addnext(new_pic(tree, rid, 'OVZ Значок Важно', ix, iy, sz, sz*ih/iw, 'Значок: важно'))

    tree.write(sp, xml_declaration=True, encoding='UTF-8', standalone=True)
    rels.save()

# ---------------- theme ----------------
def patch_theme():
    tp = os.path.join(OUT, 'ppt', 'theme', 'theme1.xml')
    s = open(tp, encoding='utf8').read()
    def rep(tag, val):
        nonlocal s
        s = re.sub(r'(<a:%s>)<a:srgbClr val="[0-9A-Fa-f]{6}"/>' % tag, r'\1<a:srgbClr val="%s"/>' % val, s, count=1)
    rep('accent1', DG); rep('accent2', LG); rep('accent6', '2E8B3E')
    rep('hlink', DG); rep('folHlink', '0B5A20')
    open(tp, 'w', encoding='utf8').write(s)

# ---------------- content types & media ----------------
def ensure_media_and_types():
    md = os.path.join(OUT, 'ppt', 'media')
    for f in os.listdir(ASSETS):
        if f.startswith('ovz_'):
            shutil.copy(os.path.join(ASSETS, f), os.path.join(md, f))
    ct = os.path.join(OUT, '[Content_Types].xml')
    s = open(ct, encoding='utf8').read()
    for ext, mime in (('png', 'image/png'), ('jpg', 'image/jpeg'), ('jpeg', 'image/jpeg')):
        if 'Extension="%s"' % ext not in s:
            s = s.replace('<Default ', '<Default Extension="%s" ContentType="%s"/><Default ' % (ext, mime), 1)
    open(ct, 'w', encoding='utf8').write(s)

def cleanup_media():
    """drop image rels no longer referenced in their part, then delete unreferenced media"""
    used = set()
    for dp, dn, fn in os.walk(os.path.join(OUT, 'ppt')):
        if not dp.endswith('_rels'):
            continue
        for f in fn:
            rp = os.path.join(dp, f)
            part = os.path.join(os.path.dirname(dp), f[:-5])
            rels = Rels(rp)
            content = open(part, 'rb').read() if os.path.exists(part) else b''
            changed = False
            for r in list(rels.root):
                tgt = r.get('Target') or ''
                if r.get('TargetMode') == 'External':
                    continue
                if r.get('Type') == REL_IMG or tgt.endswith(('.wdp', '.svg')):
                    if ('"%s"' % r.get('Id')).encode() not in content:
                        rels.root.remove(r); changed = True
                        continue
                if '/media/' in tgt:
                    used.add(tgt.split('/')[-1])
            if changed:
                rels.save()
    md = os.path.join(OUT, 'ppt', 'media')
    removed = []
    for f in os.listdir(md):
        if f not in used:
            os.remove(os.path.join(md, f)); removed.append(f)
    LOG.append('removed media: ' + ', '.join(sorted(removed)))

if __name__ == '__main__':
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    ensure_media_and_types()
    patch_theme()
    for n in range(1, 103):
        process_slide(n, None)
    cleanup_media()
    print('\n'.join(LOG))
