# -*- coding: utf-8 -*-
"""Пересобирает весь комплект игры «Экспансия»: калькулятор, слайды, раздаточные материалы, руководство."""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
for script in ['build_xlsx.py', 'build_pptx.py', 'pdf_handouts.py', 'pdf_guide.py']:
    print('==', script)
    subprocess.run([sys.executable, os.path.join(HERE, script)], check=True, cwd=HERE)
