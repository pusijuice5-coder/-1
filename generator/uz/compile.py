import json, re, os, glob
W = "/tmp/claude-0/w/uz"
S = json.load(open(W + "/strings.json"))
CYR = re.compile("[А-Яа-яЁё]")

def norm(t):
    t = t.replace("\\n", "\n")
    t = re.sub(r"([oOgG])'", lambda m: m.group(1) + "‘", t)   # o‘ g‘
    t = t.replace("'", "’")                                     # tutuq belgisi ’
    return t

problems = []
def load(fn, keys):
    out, seen = {}, set()
    for ln in open(fn, encoding="utf-8").read().split("\n"):
        if not ln.strip():
            continue
        i, t = ln.split("|", 1)
        i = int(i)
        if i in seen: problems.append("dup %s %d" % (fn, i))
        seen.add(i)
        src = keys[i]
        tr = norm(t)
        if src.count("**") != tr.count("**"):
            problems.append("bold markers %d: %r" % (i, tr[:60]))
        if CYR.search(tr) and src not in ("Выберите язык Tilni tanlang", "Русский язык"):
            problems.append("cyrillic left %d: %r" % (i, tr[:60]))
        out[src] = tr
    return out, seen

tr = {}
u, us = load(W + "/src/user.txt", S["user"])
tr.update(u)
gs = set()
for fn in sorted(glob.glob(W + "/src/gen_*.txt")):
    g, s = load(fn, S["gen"])
    tr.update(g); gs |= s
# single letters used for answer options / Scrum values
tr.update({"А": "A", "Б": "B", "В": "C", "Г": "D"})
missing_u = [i for i in range(len(S["user"])) if i not in us]
missing_g = [i for i in range(len(S["gen"])) if i not in gs]
print("user missing", missing_u, "gen missing", missing_g)
for p in problems: print("PROBLEM", p)
json.dump(tr, open(W + "/tr_all.json", "w"), ensure_ascii=False, indent=0)
print("entries", len(tr))
