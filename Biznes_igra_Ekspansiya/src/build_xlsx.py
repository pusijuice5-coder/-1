# -*- coding: utf-8 -*-
"""Калькулятор ведущего для игры «Экспансия» (Excel без макросов).
Запуск: python3 build_xlsx.py  ->  ../4_Kalkulyator_vedushchego.xlsx
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, Protection
from openpyxl.utils import get_column_letter as L
from openpyxl.cell.cell import MergedCell
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.text import RichText
from openpyxl.drawing.text import Paragraph, ParagraphProperties, CharacterProperties, Font as DFont
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.chart.axis import ChartLines
import game as G

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '4_Kalkulyator_vedushchego.xlsx')

DARK, LIME, INK, MUTED = '02691A', '4CEA4C', '14241A', '5E6E64'
TINT, GRID, INPUT, WARN = 'EEF6F0', 'C9D5CD', 'FFF4C2', 'FDE3E1'
YEAR_COLORS = ['C9D5CD', 'B4F2B4', '4CEA4C', '1E9E45', '02691A']
FONT = 'Arial'
NB = 6            # максимум банков
NR = 5            # регионов
REG = [G.REGION_NAME[r] for r in G.REGIONS]
FUN = ['Риски', 'Цифра', 'Команда', 'Сервис']
YS = ['Год 1', 'Год 2', 'Год 3', 'Год 4']
SET, SCN, CALC = 'Настройки', 'Сценарий', 'Расчёт'

f_base = Font(name=FONT, size=10, color=INK)
f_bold = Font(name=FONT, size=10, bold=True, color=INK)
f_head = Font(name=FONT, size=10, bold=True, color='FFFFFF')
f_title = Font(name=FONT, size=16, bold=True, color=DARK)
f_sub = Font(name=FONT, size=10, color=MUTED)
f_in = Font(name=FONT, size=11, bold=True, color='0000FF')
f_note = Font(name=FONT, size=9, italic=True, color=MUTED)
fill_head = PatternFill('solid', fgColor=DARK)
fill_tint = PatternFill('solid', fgColor=TINT)
fill_in = PatternFill('solid', fgColor=INPUT)
fill_off = PatternFill('solid', fgColor='E6E9E7')
thin = Side(style='thin', color=GRID)
box = Border(left=thin, right=thin, top=thin, bottom=thin)
center = Alignment(horizontal='center', vertical='center', wrap_text=True)
left = Alignment(horizontal='left', vertical='center', wrap_text=True)
right = Alignment(horizontal='right', vertical='center')
NUM = '#,##0.0;[Red]-#,##0.0;0.0'
INT = '0'

wb = Workbook()


def sheet(name, tab=None):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    if tab:
        ws.sheet_properties.tabColor = tab
    return ws


def put(ws, ref, value, font=f_base, fill=None, align=None, fmt=None, border=None, unlock=False):
    c = ws[ref]
    if isinstance(c, MergedCell):      # ячейка внутри объединения: только рамка
        if border:
            c.border = border
        return c
    c.value = value
    c.font = font
    if fill:
        c.fill = fill
    if align:
        c.alignment = align
    if fmt:
        c.number_format = fmt
    if border:
        c.border = border
    if unlock:
        c.protection = Protection(locked=False)
    return c


def header_row(ws, row, c1, labels, height=30):
    for k, lab in enumerate(labels):
        put(ws, f'{L(c1 + k)}{row}', lab, f_head, fill_head, center, border=box)
    ws.row_dimensions[row].height = height


def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w


def protect(ws):
    ws.protection.sheet = True
    ws.protection.formatCells = False
    ws.protection.formatColumns = False
    ws.protection.formatRows = False


def q(name):
    return "'%s'" % name


# ---------------------------------------------------------------- Настройки
ws = wb.active
ws.title = 'Инструкция'
ws_i = ws
ws_s = sheet(SET, DARK)
ws_y = [sheet(y, LIME) for y in YS]
ws_b = sheet('Табло', DARK)
ws_f = sheet('Финал', DARK)
ws_d = sheet('Разбор', 'F2A900')
ws_c = sheet(SCN, 'D9534F')
ws_k = sheet(CALC, '7A8B80')

ws = ws_s
put(ws, 'A1', 'Настройки игры', f_title)
put(ws, 'A2', 'Заполните жёлтые ячейки до начала игры. Остальное считается само.', f_sub)
put(ws, 'A4', 'Число банков в игре', f_bold)
put(ws, 'C4', 4, f_in, fill_in, center, INT, box, unlock=True)
put(ws, 'D4', 'от 3 до 6', f_note)
dv = DataValidation(type='whole', operator='between', formula1='3', formula2='6', showErrorMessage=True,
                    errorTitle='Число банков', error='В игре участвуют от 3 до 6 банков.')
ws.add_data_validation(dv)
dv.add('C4')
header_row(ws, 6, 1, ['№', 'Название банка', 'Участвует'], 22)
for i in range(NB):
    r = 7 + i
    put(ws, f'A{r}', i + 1, f_base, None, center, INT, box)
    put(ws, f'B{r}', 'Банк %d' % (i + 1), f_in, fill_in, left, None, box, unlock=True)
    put(ws, f'C{r}', f'=IF(A{r}<=$C$4,"да","нет")', f_base, None, center, None, box)
put(ws, 'A14', 'Названия команды придумывают сами в начале игры. Впишите их здесь — они появятся на всех листах.', f_note)

put(ws, 'E6', 'Параметры модели', f_head, fill_head, left, border=box)
put(ws, 'F6', 'Значение', f_head, fill_head, center, border=box)
put(ws, 'G6', 'Единица', f_head, fill_head, center, border=box)
PARAMS = [
    ('Бюджет развития на старте', G.P['start_budget'], 'млрд сум'),
    ('Офисов в Столице на старте', G.P['start_offices'], 'шт.'),
    ('Открыть офис', G.P['open_cost'], 'млрд сум'),
    ('Содержание офиса в год', G.P['upkeep'], 'млрд сум'),
    ('Предел дохода одного офиса в год', G.P['capacity'], 'млрд сум'),
    ('Обычные кредитные потери на офис в год', G.P['base_loss'], 'млрд сум'),
    ('Повышение функции до 2-го уровня', G.P['level_cost'][2], 'млрд сум'),
    ('Повышение функции до 3-го уровня', G.P['level_cost'][3], 'млрд сум'),
    ('Повышение функции до 4-го уровня', G.P['level_cost'][4], 'млрд сум'),
    ('Аналитический обзор на год', G.P['analytics'], 'млрд сум'),
    ('Риск-менеджмент: снижение потерь за уровень', G.P['risk_cut'], 'доля'),
    ('Цифровые каналы: экономия на офисе за уровень', G.P['digital_save'], 'млрд сум'),
    ('Сервис: прибавка к доле рынка за уровень', G.P['service_gain'], 'доля'),
    ('Норма управляемости: база', G.P['span_base'], 'офисов'),
    ('Норма управляемости: прибавка за уровень команды', G.P['span_step'], 'офисов'),
    ('Стоимость банка: множитель прибыли года', G.P['final_mult'], 'раз'),
]
PROW = {}
for k, (name, val, unit) in enumerate(PARAMS):
    r = 7 + k
    put(ws, f'E{r}', name, f_base, None, left, None, box)
    put(ws, f'F{r}', val, f_base, fill_tint, center, '0.00' if isinstance(val, float) else INT, box)
    put(ws, f'G{r}', unit, f_sub, None, center, None, box)
    PROW[k] = r
(P_BUD, P_OFF0, P_OPEN, P_UPK, P_CAP, P_BASE, P_L2, P_L3, P_L4, P_AN, P_RISK, P_DIG, P_SERV, P_SPB, P_SPS, P_MULT) = [
    f"{SET}!$F${PROW[k]}" for k in range(len(PARAMS))]
r0 = 7 + len(PARAMS) + 2
header_row(ws, r0, 5, ['Кредитная политика', 'Доход', 'Потери'], 22)
POLROW = {}
for k, p in enumerate(G.POLICIES):
    r = r0 + 1 + k
    put(ws, f'E{r}', '%s — %s' % (p, G.POLICY_NAME[p].lower()), f_base, None, left, None, box)
    put(ws, f'F{r}', G.P['policy'][p][0], f_base, fill_tint, center, '0.00', box)
    put(ws, f'G{r}', G.P['policy'][p][1], f_base, fill_tint, center, '0.00', box)
    POLROW[p] = r
put(ws, f'E{r0 + 5}', 'Параметры менять не нужно. Они вынесены сюда, чтобы было видно, на чём построен расчёт, и чтобы игру можно было настроить под свою группу. Если меняете — проверьте числа в раздаточных материалах.', f_note, None, Alignment(wrap_text=True, vertical='top'))
ws.merge_cells(f'E{r0 + 5}:G{r0 + 8}')
widths(ws, {'A': 6, 'B': 30, 'C': 12, 'D': 12, 'E': 52, 'F': 12, 'G': 12})
N_BANKS = f'{SET}!$C$4'

# ---------------------------------------------------------------- Сценарий
ws = ws_c
put(ws, 'A1', 'Сценарий игры', f_title)
put(ws, 'A2', 'Только для ведущего. Не показывайте этот лист участникам: здесь видно, что произойдёт в каждом году.', Font(name=FONT, size=10, bold=True, color='D9534F'))


def scen_table(top, title, data, fmt=INT):
    put(ws, f'A{top}', title, f_bold)
    header_row(ws, top + 1, 1, ['Регион'] + YS, 20)
    for k, reg in enumerate(G.REGIONS):
        r = top + 2 + k
        put(ws, f'A{r}', G.REGION_FULL[reg], f_base, None, left, None, box)
        for t in range(4):
            put(ws, f'{L(2 + t)}{r}', data(reg, t), f_base, fill_tint, center, fmt, box)
    return top + 2


R_POOL = scen_table(4, 'Объём рынка региона в расчёте на один банк, млрд сум (фактический объём = значение × число банков)', lambda reg, t: G.POOL[reg][t])
R_FLO = scen_table(12, 'Публичный прогноз объёма рынка: нижняя граница (на один банк)', lambda reg, t: G.FORECAST[reg][t][0])
R_FHI = scen_table(20, 'Публичный прогноз объёма рынка: верхняя граница (на один банк)', lambda reg, t: G.FORECAST[reg][t][1])
R_SHK = scen_table(28, 'Спад в регионе: дополнительные кредитные потери на один офис, млрд сум', lambda reg, t: G.SHOCK[reg][t])
put(ws, 'A36', 'События для банков, у которых функция осталась на 1-м уровне', f_bold)
header_row(ws, 37, 1, ['Событие', 'Год', 'Функция', 'Размер', 'Как считается'], 20)
EV = [('Проверка регулятора', G.EVENTS['inspection']['year'], 'Риск-менеджмент', G.EVENTS['inspection']['fine'], 'штраф, млрд сум'),
      ('Кибератака', G.EVENTS['cyber']['year'], 'Цифровые каналы', G.EVENTS['cyber']['loss'], 'ущерб, млрд сум'),
      ('Отток сотрудников', G.EVENTS['talent']['year'], 'Команда', G.EVENTS['talent']['cut'], 'доля дохода года')]
for k, e in enumerate(EV):
    r = 38 + k
    put(ws, f'A{r}', e[0], f_base, None, left, None, box)
    put(ws, f'B{r}', e[1], f_base, fill_tint, center, INT, box)
    put(ws, f'C{r}', e[2], f_base, None, left, None, box)
    put(ws, f'D{r}', e[3], f_base, fill_tint, center, '0.00' if isinstance(e[3], float) else INT, box)
    put(ws, f'E{r}', e[4], f_sub, None, left, None, box)
EV_INS, EV_CYB, EV_TAL = 38, 39, 40
STORY = [
    ('Год 1', 'Спокойный год. Событий нет. Регулятор объявляет о проверке в следующем году.'),
    ('Год 2', 'Проверка регулятора: банки с риск-менеджментом 1-го уровня платят штраф. Закон о льготах для СЭЗ принят — рынок зоны растёт быстрее прогноза.'),
    ('Год 3', 'Спад на Севере: рынок сжимается на треть, офисы в регионе несут дополнительные потери. Кибератака на банковский сектор: страдают банки с цифровыми каналами 1-го уровня.'),
    ('Год 4', 'Засуха в Долине: рынок падает, офисы в регионе несут дополнительные потери. Отток сотрудников: банки с командой 1-го уровня теряют десятую часть дохода. Юг и СЭЗ продолжают расти.'),
    ('Ложные тревоги', 'Налог на сверхприбыль банков (слух перед годом 2), падение турпотока на Юге (слух перед годом 3), отмена льгот СЭЗ (слух перед годом 4) — не сбываются.'),
]
put(ws, 'A43', 'Что происходит по годам', f_bold)
for k, (y, txt) in enumerate(STORY):
    r = 44 + k
    put(ws, f'A{r}', y, f_bold, None, Alignment(vertical='top'))
    put(ws, f'B{r}', txt, f_base, None, Alignment(wrap_text=True, vertical='top'))
    ws.merge_cells(f'B{r}:E{r}')
    ws.row_dimensions[r].height = 32
widths(ws, {'A': 32, 'B': 12, 'C': 22, 'D': 12, 'E': 34})


def scen(top, reg_idx, t):
    """ссылка на ячейку таблицы сценария: строка региона, столбец года t (0..3)"""
    return f"{SCN}!${L(2 + t)}${top + reg_idx}"


# ---------------------------------------------------------------- Расчёт
ws = ws_k
put(ws, 'A1', 'Расчёт. Этот лист служебный: ничего вводить и менять здесь не нужно.', f_bold)
COLS = {}
names = (['Год', '№', 'Активен'] + ['Зрелые: ' + x for x in REG] + ['Новые: ' + x for x in REG] + ['Ур. ' + x for x in FUN] +
         ['Офисов', 'Норма', 'Коэф. сети'] + ['Мощность: ' + x for x in REG] + ['Вес: ' + x for x in REG] + ['Доход: ' + x for x in REG] +
         ['Доход', 'Сеть', 'Коэф. риска', 'Обычные потери', 'Потери от спада', 'Штраф', 'Кибератака', 'Отток', 'События', 'Прибыль',
          'Инвестиции', 'Бюджет нач.', 'Бюджет кон.', 'Стоимость', 'Полит.: доход', 'Полит.: потери', 'Недозагрузка', 'Место',
          'Закрыли лишнее', 'Сверх макс.', 'Инвест. в офисы', 'Инвест. в функции'] + ['Итог офисов: ' + x for x in REG])
for k, nm in enumerate(names):
    COLS[nm] = L(k + 1)
cA, cN, cAct = 'A', 'B', 'C'
cMat = [COLS['Зрелые: ' + x] for x in REG]
cNew = [COLS['Новые: ' + x] for x in REG]
cLvl = [COLS['Ур. ' + x] for x in FUN]
cTot, cSpan, cSpk = COLS['Офисов'], COLS['Норма'], COLS['Коэф. сети']
cEff = [COLS['Мощность: ' + x] for x in REG]
cW = [COLS['Вес: ' + x] for x in REG]
cInc = [COLS['Доход: ' + x] for x in REG]
cIncT, cUpk, cRk, cBase, cShk = COLS['Доход'], COLS['Сеть'], COLS['Коэф. риска'], COLS['Обычные потери'], COLS['Потери от спада']
cIns, cCyb, cTal, cEv, cProf = COLS['Штраф'], COLS['Кибератака'], COLS['Отток'], COLS['События'], COLS['Прибыль']
cInv, cB0, cB1, cVal = COLS['Инвестиции'], COLS['Бюджет нач.'], COLS['Бюджет кон.'], COLS['Стоимость']
cPi, cPl, cUnder, cRank = COLS['Полит.: доход'], COLS['Полит.: потери'], COLS['Недозагрузка'], COLS['Место']
cBadClose, cBadLvl, cInvOff, cInvFun = COLS['Закрыли лишнее'], COLS['Сверх макс.'], COLS['Инвест. в офисы'], COLS['Инвест. в функции']
cEnd = [COLS['Итог офисов: ' + x] for x in REG]
LASTCOL = len(names)
BLOCK = 10


def top(t):          # строка заголовка блока года t (0..3)
    return 3 + t * BLOCK


def brow(t, i):      # строка банка i (0..5) в блоке года t
    return top(t) + 2 + i


def trow(t):         # строка итогов блока
    return top(t) + 2 + NB


IN_ROW0 = 7          # первая строка ввода на листах «Год N»
cIn_off = ['C', 'D', 'E', 'F', 'G']
cIn_up = ['H', 'I', 'J', 'K']
cIn_pol, cIn_an, cIn_fc = 'L', 'M', 'N'

for t in range(4):
    ys = q(YS[t])
    put(ws, f'A{top(t)}', YS[t], f_bold)
    put(ws, f'B{top(t)}', 'сыгран:', f_sub)
    put(ws, f'C{top(t)}', f'=IF(COUNTA({ys}!$C${IN_ROW0}:$N${IN_ROW0 + NB - 1})>0,1,0)', f_bold, fill_tint, center, INT)
    for k, nm in enumerate(names):
        put(ws, f'{L(k + 1)}{top(t) + 1}', nm, f_head, fill_head, center, border=box)
    ws.row_dimensions[top(t) + 1].height = 28
    b, e, tr = brow(t, 0), brow(t, NB - 1), trow(t)
    for i in range(NB):
        r = brow(t, i)
        rp = brow(t - 1, i)
        ri = IN_ROW0 + i
        F = {}
        F[cA] = t + 1
        F[cN] = i + 1
        F[cAct] = f'=IF({cN}{r}<={N_BANKS},1,0)'
        for k in range(NR):
            inp = f'N({ys}!{cIn_off[k]}{ri})'
            prev = (P_OFF0 if k == 0 else '0') if t == 0 else f'{cEnd[k]}{rp}'
            F[cMat[k]] = f'=MAX(0,{prev}-MAX(0,-{inp}))*{cAct}{r}'
            F[cNew[k]] = f'=MAX(0,{inp})*{cAct}{r}'
            F[cEff[k]] = f'=({cMat[k]}{r}+0.5*{cNew[k]}{r})*{cSpk}{r}'
            F[cW[k]] = f'={cEff[k]}{r}*(1+{P_SERV}*({cLvl[3]}{r}-1))'
            F[cInc[k]] = (f'=IF({cW[k]}${tr}=0,0,MIN({cEff[k]}{r}*{P_CAP},{scen(R_POOL, k, t)}*{N_BANKS}*{cW[k]}{r}/{cW[k]}${tr}))*{cPi}{r}')
            F[cEnd[k]] = f'={cMat[k]}{r}+{cNew[k]}{r}'
        for j in range(4):
            prev = '1' if t == 0 else f'{cLvl[j]}{rp}'
            F[cLvl[j]] = f'=MIN(4,{prev}+IF(N({ys}!{cIn_up[j]}{ri})>0,1,0))'
        F[cTot] = f'=SUM({cMat[0]}{r}:{cNew[-1]}{r})'
        F[cSpan] = f'={P_SPB}+{P_SPS}*{cLvl[2]}{r}'
        F[cSpk] = f'=IF({cTot}{r}=0,1,({cTot}{r}-0.5*MAX(0,{cTot}{r}-{cSpan}{r}))/{cTot}{r})'
        F[cIncT] = f'=SUM({cInc[0]}{r}:{cInc[-1]}{r})'
        F[cUpk] = f'={cTot}{r}*MAX(0,{P_UPK}-{P_DIG}*({cLvl[1]}{r}-1))'
        F[cRk] = f'=MAX(0,1-{P_RISK}*({cLvl[0]}{r}-1))'
        F[cBase] = f'={cTot}{r}*{P_BASE}*{cPl}{r}*{cRk}{r}'
        F[cShk] = '=(' + '+'.join(f'{cEnd[k]}{r}*{scen(R_SHK, k, t)}' for k in range(NR)) + f')*{cPl}{r}*{cRk}{r}'
        F[cIns] = f'=IF(AND({t + 1}={SCN}!$B${EV_INS},{cLvl[0]}{r}<2),{SCN}!$D${EV_INS},0)*{cAct}{r}'
        F[cCyb] = f'=IF(AND({t + 1}={SCN}!$B${EV_CYB},{cLvl[1]}{r}<2),{SCN}!$D${EV_CYB},0)*{cAct}{r}'
        F[cTal] = f'=IF(AND({t + 1}={SCN}!$B${EV_TAL},{cLvl[2]}{r}<2),{SCN}!$D${EV_TAL}*{cIncT}{r},0)'
        F[cEv] = f'={cIns}{r}+{cCyb}{r}+{cTal}{r}'
        F[cProf] = f'={cIncT}{r}-{cUpk}{r}-{cBase}{r}-{cShk}{r}-{cEv}{r}'
        F[cInvOff] = f'={P_OPEN}*SUM({cNew[0]}{r}:{cNew[-1]}{r})'
        lvl_parts = []
        for j in range(4):
            prev = '1' if t == 0 else f'{cLvl[j]}{rp}'
            lvl_parts.append(f'IF({cLvl[j]}{r}>{prev},CHOOSE({cLvl[j]}{r}-1,{P_L2},{P_L3},{P_L4}),0)')
        F[cInvFun] = '=(' + '+'.join(lvl_parts) + f')*{cAct}{r}'
        an = f'IF(N({ys}!{cIn_an}{ri})>0,{P_AN},0)' if t > 0 else '0'
        F[cInv] = f'={cInvOff}{r}+{cInvFun}{r}+{an}*{cAct}{r}'
        F[cB0] = f'={P_BUD}*{cAct}{r}' if t == 0 else f'={cB1}{rp}'
        F[cB1] = f'={cB0}{r}-{cInv}{r}+{cProf}{r}'
        F[cVal] = f'={cB1}{r}+{P_MULT}*{cProf}{r}'
        pol = f'{ys}!{cIn_pol}{ri}'
        F[cPi] = (f'=IF(OR({pol}="О",{pol}="O"),{SET}!$F${POLROW["О"]},IF(OR({pol}="А",{pol}="A"),{SET}!$F${POLROW["А"]},{SET}!$F${POLROW["С"]}))')
        F[cPl] = (f'=IF(OR({pol}="О",{pol}="O"),{SET}!$G${POLROW["О"]},IF(OR({pol}="А",{pol}="A"),{SET}!$G${POLROW["А"]},{SET}!$G${POLROW["С"]}))')
        F[cUnder] = f'=SUM({cEff[0]}{r}:{cEff[-1]}{r})*{P_CAP}*{cPi}{r}-{cIncT}{r}'
        F[cRank] = (f'=IF({cAct}{r}=1,1+SUMPRODUCT(({cAct}${b}:{cAct}${e}=1)*(({cVal}${b}:{cVal}${e}>{cVal}{r})+'
                    f'({cVal}${b}:{cVal}${e}={cVal}{r})*({cN}${b}:{cN}${e}<{cN}{r}))),"")')
        bad = []
        for k in range(NR):
            prev = (P_OFF0 if k == 0 else '0') if t == 0 else f'{cEnd[k]}{rp}'
            bad.append(f'(-N({ys}!{cIn_off[k]}{ri})>{prev})')
        F[cBadClose] = '=IF(OR(' + ','.join(bad) + '),1,0)'
        bad = []
        for j in range(4):
            prev = '1' if t == 0 else f'{cLvl[j]}{rp}'
            bad.append(f'AND(N({ys}!{cIn_up[j]}{ri})>0,{prev}>=4)')
        F[cBadLvl] = '=IF(OR(' + ','.join(bad) + '),1,0)'
        for col, val in F.items():
            put(ws, f'{col}{r}', val, f_base, None, center, None, box)
    put(ws, f'A{tr}', 'Итого', f_bold)
    for col in cMat + cNew + cEff + cW + cInc + cEnd + [cTot, cIncT]:
        put(ws, f'{col}{tr}', f'=SUM({col}{b}:{col}{e})', f_bold, fill_tint, center, None, box)
for k in range(LASTCOL):
    ws.column_dimensions[L(k + 1)].width = 11
ws.freeze_panes = 'D3'


def calc(col, t, i):
    return f"{CALC}!${col}${brow(t, i)}"


# ---------------------------------------------------------------- Год N
for t in range(4):
    ws = ws_y[t]
    put(ws, 'A1', '%s: решения и итоги' % YS[t], f_title)
    put(ws, 'A2', 'Перенесите решения из бланков команд в жёлтые ячейки. Пустая ячейка означает «без изменений». Итоги года появятся ниже и на листе «Табло».', f_sub)
    put(ws, 'A4', 'Решения команд', Font(name=FONT, size=12, bold=True, color=DARK))
    groups = [('C5:G5', 'Офисы: открыть (+) или закрыть (−)'), ('H5:K5', 'Повысить функцию на уровень: поставьте 1')]
    for rng, lab in groups:
        ws.merge_cells(rng)
        put(ws, rng.split(':')[0], lab, f_head, fill_head, center, border=box)
    for col, lab in [('A', ''), ('B', ''), ('L', 'Кредитная политика'), ('M', 'Аналитика'), ('N', 'Прогноз команды'),
                     ('O', 'Стоимость решений'), ('P', 'Бюджет на начало года'), ('Q', 'Проверка')]:
        put(ws, f'{col}5', lab, f_head, fill_head, center, border=box)
    ws.row_dimensions[5].height = 34
    labels = ['№', 'Банк'] + REG + FUN + ['О / С / А', '1 — купили', 'прибыль года', 'млрд сум', 'млрд сум', '']
    header_row(ws, 6, 1, labels, 30)
    dv_off = DataValidation(type='whole', operator='between', formula1='-9', formula2='9', allow_blank=True, showErrorMessage=True,
                            errorTitle='Офисы', error='Введите целое число: +2 — открыть два офиса, -1 — закрыть один.')
    dv_one = DataValidation(type='whole', operator='between', formula1='0', formula2='1', allow_blank=True, showErrorMessage=True,
                            errorTitle='Отметка', error='Поставьте 1 или оставьте ячейку пустой.')
    dv_pol = DataValidation(type='list', formula1='"О,С,А"', allow_blank=True, showErrorMessage=True,
                            errorTitle='Кредитная политика', error='Выберите из списка: О — осторожная, С — сбалансированная, А — агрессивная.')
    dv_num = DataValidation(type='decimal', operator='between', formula1='-9999', formula2='9999', allow_blank=True)
    for d in (dv_off, dv_one, dv_pol, dv_num):
        ws.add_data_validation(d)
    for i in range(NB):
        r = IN_ROW0 + i
        put(ws, f'A{r}', i + 1, f_base, None, center, INT, box)
        put(ws, f'B{r}', f'=IF(A{r}<={N_BANKS},{SET}!B{7 + i},"—")', f_bold, None, left, None, box)
        for col in cIn_off:
            put(ws, f'{col}{r}', None, f_in, fill_in, center, '+0;-0;0', box, unlock=True)
            dv_off.add(f'{col}{r}')
        for col in cIn_up:
            put(ws, f'{col}{r}', None, f_in, fill_in, center, INT, box, unlock=True)
            dv_one.add(f'{col}{r}')
        put(ws, f'{cIn_pol}{r}', None, f_in, fill_in, center, None, box, unlock=True)
        dv_pol.add(f'{cIn_pol}{r}')
        if t == 0:
            put(ws, f'{cIn_an}{r}', 'со 2-го года', f_note, fill_off, center, None, box)
        else:
            put(ws, f'{cIn_an}{r}', None, f_in, fill_in, center, INT, box, unlock=True)
            dv_one.add(f'{cIn_an}{r}')
        put(ws, f'{cIn_fc}{r}', None, f_in, fill_in, center, '0.0', box, unlock=True)
        dv_num.add(f'{cIn_fc}{r}')
        put(ws, f'O{r}', f'=IF(A{r}<={N_BANKS},{calc(cInv, t, i)},"")', f_base, fill_tint, center, NUM, box)
        put(ws, f'P{r}', f'=IF(A{r}<={N_BANKS},{calc(cB0, t, i)},"")', f_base, fill_tint, center, NUM, box)
        put(ws, f'Q{r}', (f'=IF(A{r}>{N_BANKS},"",IF({calc(cBadClose, t, i)}=1,"Закрывают больше офисов, чем есть",'
                          f'IF({calc(cBadLvl, t, i)}=1,"Уровень уже максимальный",IF(O{r}>MAX(P{r},0)+0.001,"Не хватает бюджета","ОК"))))'),
            f_bold, None, center, None, box)
        ws.row_dimensions[r].height = 22
    ws.conditional_formatting.add(f'Q{IN_ROW0}:Q{IN_ROW0 + NB - 1}', CellIsRule(operator='equal', formula=['"ОК"'], font=Font(name=FONT, bold=True, color=DARK), fill=PatternFill('solid', bgColor='DFF5E3')))
    ws.conditional_formatting.add(f'Q{IN_ROW0}:Q{IN_ROW0 + NB - 1}', FormulaRule(formula=[f'AND(Q{IN_ROW0}<>"",Q{IN_ROW0}<>"ОК")'], font=Font(name=FONT, bold=True, color='B42318'), fill=PatternFill('solid', bgColor=WARN)))
    put(ws, f'A{IN_ROW0 + NB}', 'Если в графе «Проверка» не «ОК», вернитесь к команде и исправьте решение вместе с ней.', f_note)

    # итоги
    r0 = IN_ROW0 + NB + 2
    put(ws, f'A{r0}', 'Итоги года, млрд сум', Font(name=FONT, size=12, bold=True, color=DARK))
    ws.merge_cells(f'L{r0 + 1}:M{r0 + 1}')
    header_row(ws, r0 + 1, 1, ['Место', 'Банк', 'Доход', 'Расходы на сеть', 'Кредитные потери', 'События', 'Прибыль', 'Инвестиции',
                               'Бюджет на конец года', 'Стоимость банка', 'Прогноз команды', 'Отклонение прогноза'], 46)
    RES0 = r0 + 2
    for i in range(NB):
        r = RES0 + i
        act = f'A{IN_ROW0 + i}<={N_BANKS}'
        put(ws, f'A{r}', f'=IF({act},{calc(cRank, t, i)},"")', f_bold, None, center, INT, box)
        put(ws, f'B{r}', f'=B{IN_ROW0 + i}', f_bold, None, left, None, box)
        vals = [calc(cIncT, t, i), calc(cUpk, t, i), f'{calc(cBase, t, i)}+{calc(cShk, t, i)}', calc(cEv, t, i), calc(cProf, t, i),
                calc(cInv, t, i), calc(cB1, t, i), calc(cVal, t, i)]
        for k, v in enumerate(vals):
            put(ws, f'{L(3 + k)}{r}', f'=IF({act},{v},"")', f_bold if k in (4, 7) else f_base, fill_tint if k in (4, 7) else None, center, NUM, box)
        put(ws, f'K{r}', f'=IF(AND({act},{cIn_fc}{IN_ROW0 + i}<>""),{cIn_fc}{IN_ROW0 + i},"")', f_base, None, center, NUM, box)
        ws.merge_cells(f'L{r}:M{r}')
        put(ws, f'L{r}', f'=IF(K{r}="","",G{r}-K{r})', f_base, None, center, '+#,##0.0;-#,##0.0;0.0', box)
        put(ws, f'M{r}', None, f_base, None, None, None, box)
    ws.conditional_formatting.add(f'A{RES0}:A{RES0 + NB - 1}', CellIsRule(operator='equal', formula=['1'], font=Font(name=FONT, bold=True, color='FFFFFF'), fill=PatternFill('solid', bgColor=DARK)))

    # рынок
    r0 = RES0 + NB + 1
    put(ws, f'A{r0}', 'Рынок в этом году', Font(name=FONT, size=12, bold=True, color=DARK))
    ws.merge_cells(f'A{r0 + 1}:B{r0 + 1}')
    header_row(ws, r0 + 1, 1, ['Регион', '', 'Объём рынка', 'Рынок загружает, офисов', 'Офисов всех банков', 'Теснота'] +
               ['' for _ in range(NB)], 46)
    for i in range(NB):
        put(ws, f'{L(7 + i)}{r0 + 1}', f'=IF({i + 1}<={N_BANKS},{SET}!B{7 + i},"")', f_head, fill_head, center, border=box)
    MKT0 = r0 + 2
    for k, reg in enumerate(G.REGIONS):
        r = MKT0 + k
        ws.merge_cells(f'A{r}:B{r}')
        put(ws, f'A{r}', G.REGION_FULL[reg], f_bold, None, left, None, box)
        put(ws, f'B{r}', None, f_base, None, None, None, box)
        put(ws, f'C{r}', f'={scen(R_POOL, k, t)}*{N_BANKS}', f_base, None, center, '0', box)
        put(ws, f'D{r}', f'=C{r}/{P_CAP}', f_base, None, center, '0.0', box)
        put(ws, f'E{r}', f'={CALC}!${cEnd[k]}${trow(t)}', f_bold, None, center, INT, box)
        put(ws, f'F{r}', f'=IF(E{r}>D{r}+0.001,"тесно","есть место")', f_base, None, center, None, box)
        for i in range(NB):
            put(ws, f'{L(7 + i)}{r}', f'=IF({i + 1}<={N_BANKS},{CALC}!${cEnd[k]}${brow(t, i)},"")', f_base, fill_tint, center, INT, box)
    ws.conditional_formatting.add(f'F{MKT0}:F{MKT0 + NR - 1}', CellIsRule(operator='equal', formula=['"тесно"'], font=Font(name=FONT, bold=True, color='B42318')))
    put(ws, f'A{MKT0 + NR}', 'Офисы — на конец года. Офис, открытый в этом году, считается, но работал вполсилы.', f_note)

    # уровни
    r0 = MKT0 + NR + 2
    put(ws, f'A{r0}', 'Функции и сеть на конец года', Font(name=FONT, size=12, bold=True, color=DARK))
    header_row(ws, r0 + 1, 1, ['№', 'Банк'] + ['Риск-менеджмент', 'Цифровые каналы', 'Команда', 'Сервис'] + ['Офисов всего', 'Норма управляемости', 'Политика года'], 46)
    LVL0 = r0 + 2
    for i in range(NB):
        r = LVL0 + i
        act = f'A{IN_ROW0 + i}<={N_BANKS}'
        put(ws, f'A{r}', i + 1, f_base, None, center, INT, box)
        put(ws, f'B{r}', f'=B{IN_ROW0 + i}', f_bold, None, left, None, box)
        for j in range(4):
            put(ws, f'{L(3 + j)}{r}', f'=IF({act},{calc(cLvl[j], t, i)},"")', f_base, None, center, INT, box)
        put(ws, f'G{r}', f'=IF({act},{calc(cTot, t, i)},"")', f_bold, None, center, INT, box)
        put(ws, f'H{r}', f'=IF({act},{calc(cSpan, t, i)},"")', f_base, None, center, INT, box)
        pol = f'{cIn_pol}{IN_ROW0 + i}'
        put(ws, f'I{r}', f'=IF({act},IF(OR({pol}="О",{pol}="O"),"осторожная",IF(OR({pol}="А",{pol}="A"),"агрессивная","сбалансированная")),"")', f_base, None, center, None, box)
    ws.conditional_formatting.add(f'G{LVL0}:G{LVL0 + NB - 1}', FormulaRule(formula=[f'AND(G{LVL0}<>"",G{LVL0}>H{LVL0})'], font=Font(name=FONT, bold=True, color='B42318'), fill=PatternFill('solid', bgColor=WARN)))
    put(ws, f'A{LVL0 + NB}', 'Красным отмечены банки, у которых офисов больше нормы управляемости: вся их сеть работает с потерями.', f_note)

    # прогноз
    if t < 3:
        r0 = LVL0 + NB + 2
        put(ws, f'A{r0}', 'Публичный прогноз объёма рынка на следующий год, млрд сум', Font(name=FONT, size=12, bold=True, color=DARK))
        ws.merge_cells(f'A{r0 + 1}:B{r0 + 1}')
        header_row(ws, r0 + 1, 1, ['Регион', '', 'от', 'до', 'В этом году'], 22)
        for k, reg in enumerate(G.REGIONS):
            r = r0 + 2 + k
            ws.merge_cells(f'A{r}:B{r}')
            put(ws, f'A{r}', G.REGION_FULL[reg], f_bold, None, left, None, box)
            put(ws, f'B{r}', None, f_base, None, None, None, box)
            put(ws, f'C{r}', f'={scen(R_FLO, k, t + 1)}*{N_BANKS}', f_base, None, center, '0', box)
            put(ws, f'D{r}', f'={scen(R_FHI, k, t + 1)}*{N_BANKS}', f_base, None, center, '0', box)
            put(ws, f'E{r}', f'=C{MKT0 + k}', f_sub, None, center, '0', box)
    widths(ws, {'A': 7, 'B': 24, 'C': 13, 'D': 14, 'E': 13, 'F': 13, 'G': 13, 'H': 15, 'I': 19, 'J': 13, 'K': 13, 'L': 13, 'M': 13, 'N': 13, 'O': 13, 'P': 13, 'Q': 34})
    ws.freeze_panes = f'C{IN_ROW0}'
    protect(ws)

# ---------------------------------------------------------------- Табло
ws = ws_b
put(ws, 'A1', 'Табло', f_title)
put(ws, 'A2', 'Этот лист показывают участникам. Он сам переключается на последний сыгранный год.', f_sub)
put(ws, 'J1', 'Показать год', f_sub, None, right)
put(ws, 'K1', None, f_in, fill_in, center, INT, box, unlock=True)
dvy = DataValidation(type='whole', operator='between', formula1='1', formula2='4', allow_blank=True)
ws.add_data_validation(dvy)
dvy.add('K1')
put(ws, 'J2', 'пусто — последний сыгранный', f_note, None, right)
played = [f"{CALC}!$C${top(t)}" for t in range(4)]
auto = f'MAX(1,{played[0]}*1,{played[1]}*2,{played[2]}*3,{played[3]}*4)'
put(ws, 'Z1', f'=IF(K1="",{auto},K1)', f_base)   # служебная ячейка: показываемый год
YEAR = '$Z$1'
put(ws, 'A4', f'="Итоги года "&{YEAR}&", млрд сум"', Font(name=FONT, size=14, bold=True, color=DARK))


def pick(col, i, row_fn=brow):
    """значение из блока выбранного года"""
    col_rng = f"{CALC}!${col}$1:${col}${trow(3)}"
    return f'INDEX({col_rng},{row_fn(0, i)}+({YEAR}-1)*{BLOCK})'


header_row(ws, 5, 1, ['Место', 'Банк', 'Доход', 'Расходы на сеть', 'Кредитные потери', 'События', 'Прибыль', 'Инвестиции', 'Бюджет на конец года', 'Стоимость банка'], 40)
B0 = 6
bigf = Font(name=FONT, size=12, color=INK)
bigb = Font(name=FONT, size=12, bold=True, color=INK)
for i in range(NB):
    r = B0 + i
    act = f'{i + 1}<={N_BANKS}'
    put(ws, f'A{r}', f'=IF({act},{pick(cRank, i)},"")', bigb, None, center, INT, box)
    put(ws, f'B{r}', f'=IF({act},{SET}!B{7 + i},"")', bigb, None, left, None, box)
    vals = [pick(cIncT, i), pick(cUpk, i), f'{pick(cBase, i)}+{pick(cShk, i)}', pick(cEv, i), pick(cProf, i), pick(cInv, i), pick(cB1, i), pick(cVal, i)]
    for k, v in enumerate(vals):
        put(ws, f'{L(3 + k)}{r}', f'=IF({act},{v},"")', bigb if k in (4, 7) else bigf, fill_tint if k in (4, 7) else None, center, NUM, box)
    ws.row_dimensions[r].height = 24
ws.conditional_formatting.add(f'A{B0}:A{B0 + NB - 1}', CellIsRule(operator='equal', formula=['1'], font=Font(name=FONT, size=12, bold=True, color='FFFFFF'), fill=PatternFill('solid', bgColor=DARK)))
put(ws, f'A{B0 + NB}', 'Стоимость банка = бюджет на конец года + две прибыли этого года.', f_note)

M0 = B0 + NB + 2
put(ws, f'A{M0}', 'Рынок: где работают банки', Font(name=FONT, size=14, bold=True, color=DARK))
ws.merge_cells(f'A{M0 + 1}:B{M0 + 1}')
header_row(ws, M0 + 1, 1, ['Регион', '', 'Объём рынка', 'Рынок загружает, офисов', 'Офисов всех банков', 'Теснота'] + ['' for _ in range(NB)], 50)
for i in range(NB):
    put(ws, f'{L(7 + i)}{M0 + 1}', f'=IF({i + 1}<={N_BANKS},{SET}!B{7 + i},"")', f_head, fill_head, center, border=box)
for k, reg in enumerate(G.REGIONS):
    r = M0 + 2 + k
    ws.merge_cells(f'A{r}:B{r}')
    put(ws, f'A{r}', G.REGION_FULL[reg], bigb, None, left, None, box)
    put(ws, f'B{r}', None, f_base, None, None, None, box)
    pool_row = f"{SCN}!$B${R_POOL + k}:$E${R_POOL + k}"
    put(ws, f'C{r}', f'=INDEX({pool_row},1,{YEAR})*{N_BANKS}', bigf, None, center, '0', box)
    put(ws, f'D{r}', f'=C{r}/{P_CAP}', bigf, None, center, '0.0', box)
    tot_rng = f"{CALC}!${cEnd[k]}$1:${cEnd[k]}${trow(3)}"
    put(ws, f'E{r}', f'=INDEX({tot_rng},{trow(0)}+({YEAR}-1)*{BLOCK})', bigb, None, center, INT, box)
    put(ws, f'F{r}', f'=IF(E{r}>D{r}+0.001,"тесно","есть место")', bigf, None, center, None, box)
    for i in range(NB):
        put(ws, f'{L(7 + i)}{r}', f'=IF({i + 1}<={N_BANKS},{pick(cEnd[k], i)},"")', bigf, fill_tint, center, INT, box)
    ws.row_dimensions[r].height = 24
ws.conditional_formatting.add(f'F{M0 + 2}:F{M0 + 1 + NR}', CellIsRule(operator='equal', formula=['"тесно"'], font=Font(name=FONT, size=12, bold=True, color='B42318')))

V0 = M0 + NR + 4
put(ws, f'A{V0}', 'Функции банков', Font(name=FONT, size=14, bold=True, color=DARK))
header_row(ws, V0 + 1, 1, ['№', 'Банк', 'Риск-менеджмент', 'Цифровые каналы', 'Команда', 'Сервис', 'Офисов всего', 'Норма управляемости'], 50)
for i in range(NB):
    r = V0 + 2 + i
    act = f'{i + 1}<={N_BANKS}'
    put(ws, f'A{r}', i + 1, bigf, None, center, INT, box)
    put(ws, f'B{r}', f'=IF({act},{SET}!B{7 + i},"")', bigb, None, left, None, box)
    for j in range(4):
        put(ws, f'{L(3 + j)}{r}', f'=IF({act},{pick(cLvl[j], i)},"")', bigf, None, center, INT, box)
    put(ws, f'G{r}', f'=IF({act},{pick(cTot, i)},"")', bigb, None, center, INT, box)
    put(ws, f'H{r}', f'=IF({act},{pick(cSpan, i)},"")', bigf, None, center, INT, box)
    ws.row_dimensions[r].height = 24
ws.conditional_formatting.add(f'G{V0 + 2}:G{V0 + 1 + NB}', FormulaRule(formula=[f'AND(G{V0 + 2}<>"",G{V0 + 2}>H{V0 + 2})'], font=Font(name=FONT, size=12, bold=True, color='B42318'), fill=PatternFill('solid', bgColor=WARN)))

P0 = V0 + NB + 4
put(ws, f'A{P0}', f'=IF({YEAR}<4,"Публичный прогноз объёма рынка на год "&({YEAR}+1),"Игра окончена: итог — на листе «Финал»")', Font(name=FONT, size=14, bold=True, color=DARK))
ws.merge_cells(f'A{P0 + 1}:B{P0 + 1}')
header_row(ws, P0 + 1, 1, ['Регион', '', 'от', 'до', 'В этом году'], 26)
for k, reg in enumerate(G.REGIONS):
    r = P0 + 2 + k
    ws.merge_cells(f'A{r}:B{r}')
    put(ws, f'A{r}', G.REGION_FULL[reg], bigb, None, left, None, box)
    put(ws, f'B{r}', None, f_base, None, None, None, box)
    lo = f"{SCN}!$B${R_FLO + k}:$E${R_FLO + k}"
    hi = f"{SCN}!$B${R_FHI + k}:$E${R_FHI + k}"
    put(ws, f'C{r}', f'=IF({YEAR}<4,INDEX({lo},1,{YEAR}+1)*{N_BANKS},"")', bigf, None, center, '0', box)
    put(ws, f'D{r}', f'=IF({YEAR}<4,INDEX({hi},1,{YEAR}+1)*{N_BANKS},"")', bigf, None, center, '0', box)
    put(ws, f'E{r}', f'=C{M0 + 2 + k}', Font(name=FONT, size=12, color=MUTED), None, center, '0', box)
    ws.row_dimensions[r].height = 24

# данные для графиков (справа, за пределами экрана)
put(ws, 'AB3', 'Данные графиков', f_note)
put(ws, 'AB4', 'Банк', f_note)
for i in range(NB):
    put(ws, f'AB{5 + i}', f'=IF({i + 1}<={N_BANKS},{SET}!B{7 + i},"")', f_base)
    put(ws, f'AC{5 + i}', f'=IF({i + 1}<={N_BANKS},{pick(cVal, i)},0)', f_base, None, None, '0.0')
put(ws, 'AC4', 'Стоимость банка', f_note)
put(ws, 'AE4', 'Банк', f_note)
for i in range(NB):
    put(ws, f'AE{5 + i}', f'=IF({i + 1}<={N_BANKS},{SET}!B{7 + i},"")', f_base)
    put(ws, f'AF{5 + i}', f'=IF({i + 1}<={N_BANKS},{P_BUD},0)', f_base, None, None, '0.0')
    for t in range(4):
        put(ws, f'{L(33 + t)}{5 + i}', f'=IF({i + 1}<={N_BANKS},{played[t]}*{calc(cVal, t, i)},0)', f_base, None, None, '0.0')
put(ws, 'AF4', 'Старт', f_note)
for t in range(4):
    put(ws, f'{L(33 + t)}4', YS[t], f_note)


def style_chart(ch, title):
    ch.title = title
    ch.visible_cells_only = False      # данные лежат в скрытых столбцах
    ch.style = 2
    ch.legend.position = 'b'
    ch.y_axis.majorGridlines = ChartLines(spPr=GraphicalProperties(ln=LineProperties(solidFill='E3E8E5', w=6350)))
    ch.y_axis.delete = False
    ch.x_axis.delete = False
    ch.y_axis.number_format = '0'
    cp = CharacterProperties(sz=1000, solidFill=INK, latin=DFont(typeface=FONT))
    ch.x_axis.txPr = RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])
    ch.y_axis.txPr = RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])
    ch.legend.txPr = RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])


bar = BarChart()
bar.type = 'col'
bar.add_data(Reference(ws, min_col=29, min_row=4, max_row=4 + NB), titles_from_data=True)
bar.set_categories(Reference(ws, min_col=28, min_row=5, max_row=4 + NB))
style_chart(bar, 'Стоимость банка, млрд сум')
bar.legend = None
bar.series[0].graphicalProperties.solidFill = DARK
bar.series[0].graphicalProperties.line.solidFill = DARK
bar.dataLabels = DataLabelList()
bar.dataLabels.showVal = True
bar.dataLabels.showSerName = False
bar.dataLabels.showCatName = False
bar.dataLabels.showLegendKey = False
bar.dataLabels.numFmt = '0;-0;'
bar.gapWidth = 60
bar.height, bar.width = 8.2, 13.5
ws.add_chart(bar, 'L4')

hist = BarChart()
hist.type = 'col'
hist.add_data(Reference(ws, min_col=32, max_col=36, min_row=4, max_row=4 + NB), titles_from_data=True)
hist.set_categories(Reference(ws, min_col=31, min_row=5, max_row=4 + NB))
style_chart(hist, 'Стоимость банка по годам, млрд сум')
for k, s_ in enumerate(hist.series):
    s_.graphicalProperties.solidFill = YEAR_COLORS[k]
    s_.graphicalProperties.line.solidFill = YEAR_COLORS[k]
hist.gapWidth = 70
hist.overlap = -10
hist.height, hist.width = 8.2, 13.5
ws.add_chart(hist, 'L21')
widths(ws, {'A': 8, 'B': 30, 'C': 14, 'D': 15, 'E': 14, 'F': 14, 'G': 14, 'H': 17, 'I': 14, 'J': 14, 'K': 6, 'Z': 4})
ws.column_dimensions['Z'].hidden = True
for col in range(27, 38):
    ws.column_dimensions[L(col)].hidden = True
protect(ws)

# ---------------------------------------------------------------- Финал
ws = ws_f
put(ws, 'A1', 'Итог игры', f_title)
put(ws, 'A2', 'Заполняется после четвёртого года. Банки расставлены по стоимости.', f_sub)
header_row(ws, 4, 1, ['Место', 'Банк', 'Стоимость банка', 'Бюджет на конец игры', 'Прибыль 4-го года', 'Прибыль за 4 года', 'Инвестиции за 4 года', 'Офисов', 'Рост стоимости, раз'], 34)
rk_rng = f"{CALC}!${cRank}${brow(3, 0)}:${cRank}${brow(3, NB - 1)}"
for k in range(NB):
    r = 5 + k
    idx = f'MATCH({k + 1},{rk_rng},0)'

    def fin(col, t=3, idx=idx):
        return f"INDEX({CALC}!${col}${brow(t, 0)}:${col}${brow(t, NB - 1)},{idx})"
    ok = f'AND({k + 1}<={N_BANKS},{played[3]}=1)'
    put(ws, f'A{r}', f'=IF({ok},{k + 1},"")', Font(name=FONT, size=13, bold=True, color=INK), None, center, INT, box)
    put(ws, f'B{r}', f'=IF({ok},INDEX({SET}!$B$7:$B$12,{idx}),"")', Font(name=FONT, size=13, bold=True, color=INK), None, left, None, box)
    put(ws, f'C{r}', f'=IF({ok},{fin(cVal)},"")', Font(name=FONT, size=13, bold=True, color=DARK), fill_tint, center, NUM, box)
    put(ws, f'D{r}', f'=IF({ok},{fin(cB1)},"")', bigf, None, center, NUM, box)
    put(ws, f'E{r}', f'=IF({ok},{fin(cProf)},"")', bigf, None, center, NUM, box)
    put(ws, f'F{r}', '=IF(%s,%s,"")' % (ok, '+'.join(fin(cProf, t) for t in range(4))), bigf, None, center, NUM, box)
    put(ws, f'G{r}', '=IF(%s,%s,"")' % (ok, '+'.join(fin(cInv, t) for t in range(4))), bigf, None, center, NUM, box)
    put(ws, f'H{r}', f'=IF({ok},{fin(cTot)},"")', bigf, None, center, INT, box)
    put(ws, f'I{r}', f'=IF({ok},C{r}/{P_BUD},"")', bigf, None, center, '0.0', box)
    ws.row_dimensions[r].height = 26
ws.conditional_formatting.add('A5:A10', CellIsRule(operator='equal', formula=['1'], font=Font(name=FONT, size=13, bold=True, color='FFFFFF'), fill=PatternFill('solid', bgColor=DARK)))
put(ws, 'A12', 'Стоимость банка = бюджет на конец 4-го года + две прибыли 4-го года. На старте у каждого банка было 100 млрд сум.', f_note)

put(ws, 'A14', 'Точность прогнозов', Font(name=FONT, size=12, bold=True, color=DARK))
put(ws, 'A15', 'Считается, если команда записывала прогноз своей прибыли в бланк решений. Чем меньше среднее отклонение, тем точнее команда предвидела последствия решений.', f_note)
header_row(ws, 16, 1, ['№', 'Банк', 'Прогнозов сделано', 'Среднее отклонение, млрд сум'], 34)
for i in range(NB):
    r = 17 + i
    act = f'{i + 1}<={N_BANKS}'
    fcs = [f"{q(YS[t])}!${cIn_fc}${IN_ROW0 + i}" for t in range(4)]
    cnt = '+'.join(f'IF(AND({played[t]}=1,{fcs[t]}<>""),1,0)' for t in range(4))
    dev = '+'.join(f'IF(AND({played[t]}=1,{fcs[t]}<>""),ABS({calc(cProf, t, i)}-N({fcs[t]})),0)' for t in range(4))
    put(ws, f'A{r}', i + 1, f_base, None, center, INT, box)
    put(ws, f'B{r}', f'=IF({act},{SET}!B{7 + i},"")', f_bold, None, left, None, box)
    put(ws, f'C{r}', f'=IF({act},{cnt},"")', f_base, None, center, INT, box)
    put(ws, f'D{r}', f'=IF({act},IF(C{r}=0,"—",({dev})/C{r}),"")', f_base, fill_tint, center, '0.0', box)
widths(ws, {'A': 8, 'B': 26, 'C': 17, 'D': 17, 'E': 17, 'F': 17, 'G': 17, 'H': 11, 'I': 14})
protect(ws)

# ---------------------------------------------------------------- Разбор
ws = ws_d
put(ws, 'A1', 'Разбор: откуда взялся результат', f_title)
put(ws, 'A2', 'Лист для ведущего. Цифры — за все сыгранные годы, млрд сум. По ним удобно задавать вопросы в дебрифе.', f_sub)
heads = ['№', 'Банк', 'Доход', 'Расходы на сеть', 'Обычные кредитные потери', 'Потери от спада на Севере', 'Потери от засухи в Долине',
         'Штраф регулятора', 'Ущерб от кибератаки', 'Потери от оттока сотрудников', 'Недозагрузка офисов', 'Вложено в офисы', 'Вложено в функции', 'Прибыль']
header_row(ws, 4, 1, heads, 48)


def total(col, i, years=range(4)):
    return '+'.join(f'{played[t]}*{calc(col, t, i)}' for t in years)


for i in range(NB):
    r = 5 + i
    act = f'{i + 1}<={N_BANKS}'
    put(ws, f'A{r}', i + 1, f_base, None, center, INT, box)
    put(ws, f'B{r}', f'=IF({act},{SET}!B{7 + i},"")', f_bold, None, left, None, box)
    north = '+'.join(f'{played[t]}*{calc(cEnd[1], t, i)}*{scen(R_SHK, 1, t)}*{calc(cPl, t, i)}*{calc(cRk, t, i)}' for t in range(4))
    valley = '+'.join(f'{played[t]}*{calc(cEnd[2], t, i)}*{scen(R_SHK, 2, t)}*{calc(cPl, t, i)}*{calc(cRk, t, i)}' for t in range(4))
    vals = [total(cIncT, i), total(cUpk, i), total(cBase, i), north, valley, total(cIns, i), total(cCyb, i), total(cTal, i),
            total(cUnder, i), total(cInvOff, i), total(cInvFun, i), total(cProf, i)]
    for k, v in enumerate(vals):
        put(ws, f'{L(3 + k)}{r}', f'=IF({act},{v},"")', f_bold if k == 11 else f_base, fill_tint if k == 11 else None, center, NUM, box)
    ws.row_dimensions[r].height = 22
put(ws, 'A12', 'Как читать таблицу', f_bold)
NOTES = [
    'Недозагрузка офисов — доход, который сеть могла бы принести при полной загрузке, но не принесла: рынок региона оказался тесным или офисов больше нормы управляемости. Большая цифра означает лишние офисы.',
    'Потери от спада и засухи зависят от трёх решений: сколько офисов в регионе, какая кредитная политика и какой уровень риск-менеджмента.',
    'Штраф, кибератака и отток сотрудников бьют только по банкам, которые оставили функцию на 1-м уровне.',
    'Сравните «Вложено в офисы» и «Вложено в функции» у лидера и у отстающего — обычно разница видна сразу.',
]
for k, txt in enumerate(NOTES):
    put(ws, f'A{13 + k}', txt, f_base, None, Alignment(wrap_text=True, vertical='top'))
    ws.merge_cells(f'A{13 + k}:N{13 + k}')
    ws.row_dimensions[13 + k].height = 30
widths(ws, {'A': 6, 'B': 24, 'C': 12, 'D': 12, 'E': 14, 'F': 14, 'G': 14, 'H': 12, 'I': 12, 'J': 14, 'K': 14, 'L': 12, 'M': 12, 'N': 12})
protect(ws)

# ---------------------------------------------------------------- Инструкция
ws = ws_i
ws.sheet_view.showGridLines = False
put(ws, 'A1', 'Экспансия: калькулятор ведущего', f_title)
put(ws, 'A2', 'Файл считает итоги каждого года по решениям команд. Макросов нет, интернет не нужен.', f_sub)
STEPS = [
    ('До игры', 'Лист «Настройки»: укажите число банков и впишите названия команд.'),
    ('Каждый год', 'Лист «Год 1» (затем «Год 2», «Год 3», «Год 4»): перенесите решения из бланков команд в жёлтые ячейки. Пустая ячейка — без изменений.'),
    ('Проверка', 'В графе «Проверка» у каждого банка должно стоять «ОК». Если нет — команда потратила больше бюджета или ошиблась в бланке. Исправьте вместе с командой.'),
    ('Показ итогов', 'Откройте лист «Табло» и выведите его на экран. Он сам показывает последний год, по которому введены решения.'),
    ('После 4-го года', 'Лист «Финал» — места банков. Лист «Разбор» — цифры для дебрифа.'),
]
header_row(ws, 4, 1, ['Когда', 'Что делать'], 22)
for k, (a, b_) in enumerate(STEPS):
    r = 5 + k
    put(ws, f'A{r}', a, f_bold, fill_tint, Alignment(vertical='top', wrap_text=True), None, box)
    put(ws, f'B{r}', b_, f_base, None, Alignment(vertical='top', wrap_text=True), None, box)
    ws.row_dimensions[r].height = 34
put(ws, 'A11', 'Какие ячейки заполнять', Font(name=FONT, size=12, bold=True, color=DARK))
put(ws, 'A12', None, f_in, fill_in, center, None, box)
put(ws, 'B12', 'Жёлтые ячейки с синим шрифтом — для ввода. Все остальные ячейки считаются по формулам и защищены от случайной правки.', f_base, None, left)
put(ws, 'A13', None, f_base, fill_tint, center, None, box)
put(ws, 'B13', 'Светло-зелёные ячейки — главные результаты: прибыль и стоимость банка.', f_base, None, left)
put(ws, 'A15', 'Пример заполнения строки решений', Font(name=FONT, size=12, bold=True, color=DARK))
ex_heads = ['Банк'] + REG + FUN + ['Политика', 'Аналитика', 'Прогноз']
for k, h in enumerate(ex_heads):
    put(ws, f'{L(2 + k)}16', h, f_head, fill_head, center, border=box)
ex_vals = ['Пример', None, 1, None, 2, None, 1, None, None, 1, 'С', 1, 85]
for k, v in enumerate(ex_vals):
    put(ws, f'{L(2 + k)}17', v, f_in if k else f_bold, fill_in if k else None, center, None, box)
put(ws, 'B18', 'Читается так: банк открывает один офис на Севере и два на Юге, повышает риск-менеджмент и сервис на один уровень, выбирает сбалансированную политику, покупает аналитический обзор и ждёт прибыль 85 млрд сум.', f_note, None, Alignment(wrap_text=True, vertical='top'))
ws.merge_cells('B18:N19')
put(ws, 'B20', 'Стоимость такого решения: 3 офиса × 25 + два повышения до 2-го уровня × 20 + обзор 8 = 123 млрд сум.', f_note)
put(ws, 'A22', 'Если что-то пошло не так', Font(name=FONT, size=12, bold=True, color=DARK))
FAQ = [
    ('В ячейке ####', 'Столбец узкий. Раздвиньте его: формулы от этого не пострадают.'),
    ('Ошиблись при вводе', 'Просто исправьте число в жёлтой ячейке. Всё пересчитается, включая следующие годы.'),
    ('Команда закрывает офис', 'Введите число со знаком минус, например -1. Закрытый офис перестаёт приносить доход и расходы с начала года.'),
    ('Бюджет банка ушёл в минус', 'Игра продолжается. Пока бюджет отрицательный, банк не может открывать офисы и повышать функции.'),
    ('Нужно снять защиту листа', 'Рецензирование → Снять защиту листа. Пароля нет.'),
]
header_row(ws, 23, 1, ['Ситуация', 'Что делать'], 22)
for k, (a, b_) in enumerate(FAQ):
    r = 24 + k
    put(ws, f'A{r}', a, f_bold, None, Alignment(vertical='top', wrap_text=True), None, box)
    put(ws, f'B{r}', b_, f_base, None, Alignment(vertical='top', wrap_text=True), None, box)
    ws.row_dimensions[r].height = 30
for r in list(range(5, 10)) + list(range(24, 29)):
    ws.merge_cells(f'B{r}:N{r}')
ws.merge_cells('B12:N12')
ws.merge_cells('B13:N13')
ws.merge_cells('B20:N20')
widths(ws, {'A': 26, 'B': 14, 'C': 10, 'D': 10, 'E': 10, 'F': 10, 'G': 10, 'H': 10, 'I': 10, 'J': 10, 'K': 10, 'L': 11, 'M': 11, 'N': 11})

protect(ws_k)
protect(ws_c)
for ws in wb.worksheets:           # печать: альбомная страница, лист целиком по ширине
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.paperSize = 9
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_options.horizontalCentered = True
ws_s.protection.sheet = True
for ws in wb.worksheets:
    ws.sheet_view.zoomScale = 100
ws_b.sheet_view.zoomScale = 110
wb.active = 0
wb.save(OUT)
print('saved', os.path.abspath(OUT))
