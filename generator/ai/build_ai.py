import sys, os, shutil, subprocess, importlib
sys.path.insert(0, os.path.dirname(__file__))
import lib, tpl_ai
W = "/tmp/claude-0/w2"
B = W + "/build_ai"
SK = "/root/.claude/skills/synced/575c671b-b53f-49f5-b380-b6cee68d875c_98f61f68-2023-4d1e-aff1-998e15c53ae4/pptx"
if os.path.exists(B): shutil.rmtree(B)
shutil.copytree(W + "/base", B)
d = tpl_ai.AIDeck(B)
mods = sys.argv[1].split(",")
for m in mods:
    importlib.import_module(m).build(d)
d.save()
subprocess.run([sys.executable, SK + "/scripts/clean.py", B], check=True, capture_output=True)
out = W + "/ai.pptx"
if os.path.exists(out): os.remove(out)
subprocess.run("cd %s && zip -qXrD %s ." % (B, out), shell=True, check=True)
print("slides:", len(d.slides), "->", out)
for w in lib.SHRUNK: print("SHRINK", w)
for w in lib.WARN: print("WARN", w)
