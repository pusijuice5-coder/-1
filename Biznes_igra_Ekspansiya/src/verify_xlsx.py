# -*- coding: utf-8 -*-
"""Сверка калькулятора с эталонной моделью: случайные решения -> LibreOffice -> сравнение."""
import os, sys, random, subprocess, json, shutil
from openpyxl import load_workbook
import game as G

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '4_Kalkulyator_vedushchego.xlsx')
RECALC = '/root/.claude/skills/synced/575c671b-b53f-49f5-b380-b6cee68d875c_98f61f68-2023-4d1e-aff1-998e15c53ae4/xlsx/scripts/recalc.py'
TMP = sys.argv[1] if len(sys.argv) > 1 else '/tmp'
OFF = ['C', 'D', 'E', 'F', 'G']; UP = ['H', 'I', 'J', 'K']


def random_game(n, rng):
    state = G.new_state(n)
    all_dec = []
    for y in G.YEARS:
        dec = []
        for b in state:
            d = dict(offices={}, up=[], policy=rng.choice(G.POLICIES + ['']), analytics=False)
            budget = max(b['budget'], 0)
            for _ in range(rng.choice([0, 1, 2, 3, 4])):
                r = rng.choice(G.REGIONS)
                if budget >= G.P['open_cost']:
                    d['offices'][r] = d['offices'].get(r, 0) + 1; budget -= G.P['open_cost']
            if rng.random() < 0.25:       # закрыть офис там, где не открываем
                cand = [r for r in G.REGIONS if b['offices'][r] > 0 and d['offices'].get(r, 0) == 0]
                if cand:
                    r = rng.choice(cand); d['offices'][r] = -rng.randint(1, b['offices'][r])
            lvl = dict(b['level'])
            for f in G.FUNCS:
                if rng.random() < 0.4 and lvl[f] < 4 and budget >= G.P['level_cost'][lvl[f] + 1]:
                    d['up'].append(f); budget -= G.P['level_cost'][lvl[f] + 1]; lvl[f] += 1
            if y > 1 and rng.random() < 0.4 and budget >= G.P['analytics']:
                d['analytics'] = True
            dec.append(d)
        G.play_year(state, dec, y)
        all_dec.append(dec)
    return all_dec


def run(n, seed):
    rng = random.Random(seed)
    dec = random_game(n, rng)
    ref = G.play([[dict(d, policy=d['policy'] or 'С') for d in yr] for yr in dec])
    path = os.path.join(TMP, 'verify_%d_%d.xlsx' % (n, seed))
    shutil.copy(SRC, path)
    wb = load_workbook(path)
    wb['Настройки']['C4'] = n
    for y in G.YEARS:
        ws = wb['Год %d' % y]
        for i, d in enumerate(dec[y - 1]):
            r = 7 + i
            for k, reg in enumerate(G.REGIONS):
                v = d['offices'].get(reg, 0)
                ws[f'{OFF[k]}{r}'] = v if v else None
            for k, f in enumerate(G.FUNCS):
                ws[f'{UP[k]}{r}'] = 1 if f in d['up'] else None
            ws[f'L{r}'] = d['policy'] or None
            if y > 1:
                ws[f'M{r}'] = 1 if d['analytics'] else None
            ws[f'N{r}'] = round(ref[y - 1][i]['profit']) + 5
    wb.save(path)
    out = json.loads(subprocess.run([sys.executable, RECALC, path, '180'], capture_output=True, text=True).stdout)
    assert out.get('status') == 'success', out
    wb = load_workbook(path, data_only=True)
    worst = 0.0
    for y in G.YEARS:
        ws = wb['Год %d' % y]
        for i in range(n):
            r = 15 + 2 + i          # строки итогов: 17..22
            got = dict(income=ws[f'C{r}'].value, upkeep=ws[f'D{r}'].value, losses=ws[f'E{r}'].value, events=ws[f'F{r}'].value,
                       profit=ws[f'G{r}'].value, invest=ws[f'H{r}'].value, budget=ws[f'I{r}'].value, value=ws[f'J{r}'].value)
            e = ref[y - 1][i]
            exp = dict(income=e['income'], upkeep=e['upkeep'], losses=e['base_loss'] + e['shock'], events=e['events'], profit=e['profit'],
                       invest=e['invest'], budget=e['budget_end'], value=e['value'])
            for k in exp:
                diff = abs((got[k] or 0) - exp[k])
                worst = max(worst, diff)
                assert diff < 1e-6, ('MISMATCH', n, seed, y, i, k, got[k], exp[k])
            assert ws[f'Q{7 + i}'].value == 'ОК', (n, seed, y, i, ws[f'Q{7 + i}'].value)
            dev = ws[f'L{r}'].value
            assert abs(dev - (e['profit'] - (round(e['profit']) + 5))) < 1e-6, ('forecast dev', dev)
    # места на листе «Финал»
    order = sorted(range(n), key=lambda i: (-ref[3][i]['value'], i))
    wsf = wb['Финал']
    for k, i in enumerate(order):
        assert wsf[f'B{5 + k}'].value == 'Банк %d' % (i + 1), (wsf[f'B{5 + k}'].value, i)
        assert abs(wsf[f'C{5 + k}'].value - ref[3][i]['value']) < 1e-6
    tb = wb['Табло']
    assert tb['Z1'].value == 4, tb['Z1'].value
    return worst


if __name__ == '__main__':
    for n, seed in [(3, 1), (4, 2), (5, 3), (6, 4), (4, 5), (6, 6)]:
        w = run(n, seed)
        print('банков %d, набор %d: совпало, макс. расхождение %.2e' % (n, seed, w))
