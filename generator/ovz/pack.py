import sys, os, zipfile
src, dst = sys.argv[1], sys.argv[2]
files = []
for dp, dn, fn in os.walk(src):
    for f in fn:
        full = os.path.join(dp, f); rel = os.path.relpath(full, src).replace(os.sep, '/')
        files.append((rel, full))
files.sort(key=lambda t: (t[0] != '[Content_Types].xml', not t[0].startswith('_rels/'), t[0]))
if os.path.exists(dst): os.remove(dst)
with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
    for rel, full in files:
        ct = zipfile.ZIP_STORED if rel.lower().endswith(('.jpg', '.jpeg', '.png')) else zipfile.ZIP_DEFLATED
        z.write(full, rel, compress_type=ct)
print(dst, os.path.getsize(dst)//1024, 'KB')
