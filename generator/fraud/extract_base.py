# -*- coding: utf-8 -*-
"""One-off: copy the parts of the user's template (We_build_Products.pptx) that the course reuses
into base/ - slide master 1, its "Default Layout", the theme and presentation settings."""
import os, sys, zipfile
src = sys.argv[1]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "base")
parts = ["ppt/slideMasters/slideMaster1.xml", "ppt/slideLayouts/slideLayout2.xml", "ppt/theme/theme1.xml",
         "ppt/presProps.xml", "ppt/viewProps.xml", "ppt/tableStyles.xml", "ppt/presentation.xml"]
z = zipfile.ZipFile(src)
for p in parts:
    data = z.read(p)
    if p == "ppt/presentation.xml":       # keep only what is reused (default text style); drop the 301 slide ids
        import re
        t = data.decode("utf-8")
        t = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", "<p:sldIdLst></p:sldIdLst>", t, flags=re.S)
        data = t.encode("utf-8")
    os.makedirs(os.path.join(out, os.path.dirname(p)), exist_ok=True)
    open(os.path.join(out, p), "wb").write(data)
    print(p, len(data))
