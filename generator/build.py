import sys, os, shutil, subprocess, importlib
sys.path.insert(0, os.path.dirname(__file__))
import lib
W = "/tmp/claude-0/w"
B = W + "/build"
if os.path.exists(B): shutil.rmtree(B)
shutil.copytree(W + "/ku", B)
d = lib.Deck(B)
mods = sys.argv[1].split(",") if len(sys.argv) > 1 else ["m1"]
for m in mods:
    importlib.import_module(m).build(d)
d.save()
out = W + "/out.pptx"
if os.path.exists(out): os.remove(out)
subprocess.run("cd %s && zip -qXr %s ." % (B, out), shell=True, check=True)
print("slides:", len(d.slides), "->", out)
for w in lib.WARN: print("WARN", w)
