# -*- coding: utf-8 -*-
"""Заполняет копию калькулятора демонстрационной партией (для скриншотов и проверки)."""
import os, sys, shutil, json, subprocess
from openpyxl import load_workbook
import game as G
import demo_game as D

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '4_Kalkulyator_vedushchego.xlsx')
RECALC = '/root/.claude/skills/synced/575c671b-b53f-49f5-b380-b6cee68d875c_98f61f68-2023-4d1e-aff1-998e15c53ae4/xlsx/scripts/recalc.py'
OFF = ['C', 'D', 'E', 'F', 'G']; UP = ['H', 'I', 'J', 'K']


def fill(path, years=4, show_year=None):
    shutil.copy(SRC, path)
    wb = load_workbook(path)
    wb['Настройки']['C4'] = len(D.NAMES)
    for i, n in enumerate(D.NAMES):
        wb['Настройки'][f'B{7 + i}'] = n
    for y in range(1, years + 1):
        ws = wb['Год %d' % y]
        for i, d in enumerate(D.DECISIONS[y - 1]):
            r = 7 + i
            for k, reg in enumerate(G.REGIONS):
                v = d['offices'].get(reg, 0)
                ws[f'{OFF[k]}{r}'] = v if v else None
            for k, f in enumerate(G.FUNCS):
                ws[f'{UP[k]}{r}'] = 1 if f in d.get('up', []) else None
            ws[f'L{r}'] = d['policy']
            if y > 1:
                ws[f'M{r}'] = 1 if d.get('analytics') else None
            ws[f'N{r}'] = D.FORECASTS[y - 1][i]
    if show_year:
        wb['Табло']['K1'] = show_year
    wb.save(path)
    out = json.loads(subprocess.run([sys.executable, RECALC, path, '180'], capture_output=True, text=True).stdout)
    assert out.get('status') == 'success', out
    return path


if __name__ == '__main__':
    print(fill(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 4))
