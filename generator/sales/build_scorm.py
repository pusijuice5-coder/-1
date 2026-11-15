#!/usr/bin/env python3
"""Сборка SCORM-пакета курса.
   python3 build_scorm.py [2004|12]     -> zip в корне репозитория (по умолчанию SCORM 2004)
   Видео (course/video/*.mp4) в git не хранятся: перед сборкой на чистой копии выполните
   python3 video/build.py  (нужны node + playwright + ffmpeg).
   Презентация (PPTX) собирается отдельно: generator/pptx/build_pptx.js, и вкладывается в пакет в docs/."""
import os, sys, zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
COURSE = {
    'src': [os.path.join(HERE, 'course')],          # папки, из которых собирается курс (поздние перекрывают ранние)
    'title': 'Продажи нового поколения: розница и корпоративный бизнес',
    'ident': 'IYB_SALES_COURSE_2026',
    'zip': 'Prodazhi_kurs',
    'extra': {'docs/Prodazhi_kurs_prezentaciya.pptx': os.path.join(ROOT, 'Prodazhi_kurs_prezentaciya.pptx')},
    'videos': 5,
}
MASTERY = 80

def collect(course):
    files = {}
    for k, src in enumerate(course['src']):
        for d, _, fs in os.walk(src):
            for f in sorted(fs):
                if f.startswith('.'): continue
                full = os.path.join(d, f)
                rel = os.path.relpath(full, src).replace(os.sep, '/')
                # из базовой папки (общий плеер) можно исключить файлы другого курса
                if k == 0 and any(rel == e or rel.startswith(e) for e in course.get('exclude', [])): continue
                files[rel] = full
    for rel, full in course.get('extra', {}).items():
        assert os.path.exists(full), 'нет файла: %s' % full
        files[rel] = full
    return files

def manifest12(c, fl):
    res = '\n'.join('      <file href="%s"/>' % escape(f) for f in fl)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{c['ident']}" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd
                      http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd
                      http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="ORG-1">
    <organization identifier="ORG-1">
      <title>{escape(c['title'])}</title>
      <item identifier="ITEM-1" identifierref="RES-1" isvisible="true">
        <title>{escape(c['title'])}</title>
        <adlcp:masteryscore>{MASTERY}</adlcp:masteryscore>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES-1" type="webcontent" adlcp:scormtype="sco" href="index.html">
{res}
    </resource>
  </resources>
</manifest>
'''

def manifest2004(c, fl):
    res = '\n'.join('      <file href="%s"/>' % escape(f) for f in fl)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{c['ident']}" version="1.0"
  xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3"
  xmlns:adlseq="http://www.adlnet.org/xsd/adlseq_v1p3"
  xmlns:adlnav="http://www.adlnet.org/xsd/adlnav_v1p3"
  xmlns:imsss="http://www.imsglobal.org/xsd/imsss"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 imscp_v1p1.xsd
                      http://www.adlnet.org/xsd/adlcp_v1p3 adlcp_v1p3.xsd
                      http://www.adlnet.org/xsd/adlseq_v1p3 adlseq_v1p3.xsd
                      http://www.adlnet.org/xsd/adlnav_v1p3 adlnav_v1p3.xsd
                      http://www.imsglobal.org/xsd/imsss imsss_v1p0.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>2004 3rd Edition</schemaversion>
  </metadata>
  <organizations default="ORG-1">
    <organization identifier="ORG-1">
      <title>{escape(c['title'])}</title>
      <item identifier="ITEM-1" identifierref="RES-1">
        <title>{escape(c['title'])}</title>
        <imsss:sequencing>
          <imsss:objectives>
            <imsss:primaryObjective objectiveID="PRIMARY" satisfiedByMeasure="true">
              <imsss:minNormalizedMeasure>{MASTERY / 100:.1f}</imsss:minNormalizedMeasure>
            </imsss:primaryObjective>
          </imsss:objectives>
          <imsss:deliveryControls completionSetByContent="true" objectiveSetByContent="true"/>
        </imsss:sequencing>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES-1" type="webcontent" adlcp:scormType="sco" href="index.html">
{res}
    </resource>
  </resources>
</manifest>
'''

def build(course, ver):
    files = collect(course); fl = sorted(files)
    need = ['index.html'] + ['video/v%d.%s' % (i, e) for i in range(1, course['videos'] + 1) for e in ('mp4', 'jpg')]
    missing = [f for f in need if f not in files]
    assert not missing, 'нет файлов: %s' % missing
    name = '%s_SCORM%s.zip' % (course['zip'], ver)
    out = os.path.join(ROOT, name)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr('imsmanifest.xml', manifest2004(course, fl) if ver == '2004' else manifest12(course, fl))
        for f in fl:
            stored = f.lower().endswith(('.mp4', '.webp', '.jpg', '.png', '.woff2', '.pptx'))
            z.write(files[f], f, zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)
    print(name, '%.1f MB' % (os.path.getsize(out) / 1e6), len(fl), 'files')
    return out

if __name__ == '__main__':
    build(COURSE, sys.argv[1] if len(sys.argv) > 1 else '2004')
