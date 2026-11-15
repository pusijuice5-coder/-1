#!/usr/bin/env python3
"""Сборка SCORM-пакета курса «Продажи нового поколения».
   Запуск: python3 build_scorm.py            -> SCORM 1.2 (zip в корне репозитория)
           python3 build_scorm.py 2004       -> SCORM 2004 (3rd Edition)
   Видео (course/video/*.mp4) в git не хранятся: перед сборкой на чистой копии
   выполните  python3 video/build.py  (нужны node + playwright + ffmpeg)."""
import os, sys, zipfile
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'course')
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
TITLE = 'Продажи нового поколения: розница и корпоративный бизнес'
IDENT = 'IYB_SALES_COURSE_2026'
MASTERY = 80

def files():
    out = []
    for d, _, fs in os.walk(SRC):
        for f in sorted(fs):
            if f.startswith('.'): continue
            out.append(os.path.relpath(os.path.join(d, f), SRC).replace(os.sep, '/'))
    return sorted(out)

def manifest12(fl):
    res = '\n'.join('      <file href="%s"/>' % escape(f) for f in fl)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{IDENT}" version="1.0"
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
      <title>{escape(TITLE)}</title>
      <item identifier="ITEM-1" identifierref="RES-1" isvisible="true">
        <title>{escape(TITLE)}</title>
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

def manifest2004(fl):
    res = '\n'.join('      <file href="%s"/>' % escape(f) for f in fl)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="{IDENT}" version="1.0"
  xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3"
  xmlns:adlseq="http://www.adlnet.org/xsd/adlseq_v1p3"
  xmlns:adlnav="http://www.adlnet.org/xsd/adlnav_v1p3"
  xmlns:imsss="http://www.imsglobal.org/xsd/imsss"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>2004 3rd Edition</schemaversion>
  </metadata>
  <organizations default="ORG-1">
    <organization identifier="ORG-1">
      <title>{escape(TITLE)}</title>
      <item identifier="ITEM-1" identifierref="RES-1">
        <title>{escape(TITLE)}</title>
        <imsss:sequencing>
          <imsss:objectives>
            <imsss:primaryObjective objectiveID="PRIMARY" satisfiedByMeasure="true">
              <imsss:minNormalizedMeasure>{MASTERY / 100:.1f}</imsss:minNormalizedMeasure>
            </imsss:primaryObjective>
          </imsss:objectives>
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

def main():
    v2004 = len(sys.argv) > 1 and sys.argv[1] == '2004'
    fl = files()
    missing = [f for f in ['index.html'] + ['video/v%d.mp4' % i for i in range(1, 6)] + ['video/v%d.jpg' % i for i in range(1, 6)] if f not in fl]
    assert not missing, 'нет файлов: %s' % missing
    name = 'Prodazhi_kurs_SCORM%s.zip' % ('2004' if v2004 else '12')
    out = os.path.join(ROOT, name)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr('imsmanifest.xml', manifest2004(fl) if v2004 else manifest12(fl))
        for f in fl:
            stored = f.lower().endswith(('.mp4', '.webp', '.jpg', '.png', '.woff2'))
            z.write(os.path.join(SRC, f), f, zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED)
    print(name, '%.1f MB' % (os.path.getsize(out) / 1e6), len(fl), 'files')

if __name__ == '__main__':
    main()
