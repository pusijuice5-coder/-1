#!/bin/bash
# render.sh file first last outdir
cd /tmp/claude-0/w2
SK=/root/.claude/skills/synced/575c671b-b53f-49f5-b380-b6cee68d875c_98f61f68-2023-4d1e-aff1-998e15c53ae4/pptx
f=$1; base=$(basename $f .pptx)
rm -f /tmp/claude-0/w2/$base.pdf
timeout 590 python3 $SK/scripts/office/soffice.py --headless --convert-to pdf --outdir /tmp/claude-0/w2 /tmp/claude-0/w2/$f >/dev/null 2>&1
mkdir -p $4
pdftoppm -jpeg -r 80 -f $2 -l $3 /tmp/claude-0/w2/$base.pdf $4/s 2>/dev/null
ls $4 | wc -l
