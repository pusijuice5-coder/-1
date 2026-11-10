# -*- coding: utf-8 -*-
"""Параметры и эталонная модель игры «Экспансия». Все суммы — млрд сум.

Этот файл — единственный источник чисел: из него берут значения калькулятор (Excel),
слайды и раздаточные материалы. Меняя параметр здесь, пересоберите всё: python3 build_all.py
"""

REGIONS = ['CAP', 'NORTH', 'VALLEY', 'SOUTH', 'SEZ']
REGION_NAME = {'CAP': 'Столица', 'NORTH': 'Север', 'VALLEY': 'Долина', 'SOUTH': 'Юг', 'SEZ': 'СЭЗ'}
REGION_FULL = {'CAP': 'Столица', 'NORTH': 'Промышленный Север', 'VALLEY': 'Аграрная долина',
               'SOUTH': 'Туристический Юг', 'SEZ': 'Свободная экономическая зона'}
FUNCS = ['R', 'D', 'P', 'S']
FUNC_NAME = {'R': 'Риск-менеджмент', 'D': 'Цифровые каналы', 'P': 'Команда', 'S': 'Сервис'}
POLICIES = ['О', 'С', 'А']
POLICY_NAME = {'О': 'Осторожная', 'С': 'Сбалансированная', 'А': 'Агрессивная'}
YEARS = [1, 2, 3, 4]

P = dict(
    start_budget=100,        # бюджет развития на старте
    start_offices=2,         # офисов в Столице на старте
    open_cost=25,            # открыть офис
    upkeep=8,                # содержание офиса в год
    capacity=45,             # предел дохода одного офиса в год
    base_loss=3,             # обычные кредитные потери на офис в год
    level_cost={2: 20, 3: 30, 4: 40},
    analytics=8,             # аналитический обзор на год
    risk_cut=0.25,           # снижение потерь за каждый уровень риск-менеджмента выше 1-го
    digital_save=2,          # экономия на содержании офиса за уровень цифровых каналов
    service_gain=0.20,       # прибавка к весу в разделе рынка за уровень сервиса
    span_base=2, span_step=2,  # норма управляемости: 2 + 2 × уровень команды
    final_mult=2,            # стоимость банка = бюджет + 2 × прибыль года
    policy={'О': (0.90, 0.5), 'С': (1.00, 1.0), 'А': (1.15, 1.6)},  # (доход, потери)
)

# Объём рынка региона в расчёте на один банк; фактический объём = значение × число банков.
POOL = {'CAP': [60, 60, 62, 64], 'NORTH': [40, 44, 30, 46], 'VALLEY': [30, 36, 40, 28],
        'SOUTH': [20, 30, 42, 50], 'SEZ': [8, 20, 44, 60]}
# Публичный прогноз (от, до) на один банк. Год 1 известен точно.
FORECAST = {'CAP': [(60, 60), (58, 62), (60, 64), (62, 66)],
            'NORTH': [(40, 40), (40, 48), (28, 48), (40, 50)],
            'VALLEY': [(30, 30), (32, 40), (36, 44), (24, 44)],
            'SOUTH': [(20, 20), (26, 34), (38, 46), (44, 56)],
            'SEZ': [(8, 8), (12, 28), (36, 52), (50, 70)]}
# Спад в регионе: дополнительные кредитные потери на офис.
SHOCK = {'CAP': [0, 0, 0, 0], 'NORTH': [0, 0, 24, 0], 'VALLEY': [0, 0, 0, 20], 'SOUTH': [0, 0, 0, 0], 'SEZ': [0, 0, 0, 0]}
# События для банков, у которых функция осталась на 1-м уровне.
EVENTS = dict(
    inspection=dict(year=2, func='R', fine=20),     # проверка регулятора: штраф
    cyber=dict(year=3, func='D', loss=30),          # кибератака: ущерб
    talent=dict(year=4, func='P', cut=0.10),        # отток сотрудников: доля дохода
)


def new_state(n_banks):
    return [dict(budget=P['start_budget'],
                 offices={r: (P['start_offices'] if r == 'CAP' else 0) for r in REGIONS},
                 level={f: 1 for f in FUNCS}) for _ in range(n_banks)]


def play_year(state, decisions, year):
    """state — список банков (изменяется), decisions[i] = dict(offices={region: +n/-n}, up=[функции],
    policy='О|С|А', analytics=bool). Возвращает список результатов по банкам."""
    n = len(state)
    t = year - 1
    calc = []
    for b, d in zip(state, decisions):
        ch = {r: int(d.get('offices', {}).get(r, 0) or 0) for r in REGIONS}
        mature = {r: max(0, b['offices'][r] - max(0, -ch[r])) for r in REGIONS}
        new = {r: max(0, ch[r]) for r in REGIONS}
        invest = sum(new.values()) * P['open_cost']
        lvl = dict(b['level'])
        for f in d.get('up', []):
            if lvl[f] < 4:
                lvl[f] += 1
                invest += P['level_cost'][lvl[f]]
        if d.get('analytics'):
            invest += P['analytics']
        total = sum(mature.values()) + sum(new.values())
        span = P['span_base'] + P['span_step'] * lvl['P']
        over = max(0, total - span)
        span_k = (total - 0.5 * over) / total if total else 1.0
        eff = {r: (mature[r] + 0.5 * new[r]) * span_k for r in REGIONS}
        weight = {r: eff[r] * (1 + P['service_gain'] * (lvl['S'] - 1)) for r in REGIONS}
        calc.append(dict(mature=mature, new=new, lvl=lvl, invest=invest, total=total, span=span, span_k=span_k,
                         eff=eff, weight=weight, policy=d.get('policy') or 'С'))
    results = []
    for b, c in zip(state, calc):
        inc_k, loss_k = P['policy'][c['policy']]
        income = {}
        for r in REGIONS:
            w_all = sum(x['weight'][r] for x in calc)
            share = POOL[r][t] * n * c['weight'][r] / w_all if w_all else 0.0
            income[r] = min(c['eff'][r] * P['capacity'], share) * inc_k
        inc = sum(income.values())
        offices = {r: c['mature'][r] + c['new'][r] for r in REGIONS}
        upkeep = c['total'] * max(0, P['upkeep'] - P['digital_save'] * (c['lvl']['D'] - 1))
        rk = max(0.0, 1 - P['risk_cut'] * (c['lvl']['R'] - 1))
        base_loss = c['total'] * P['base_loss'] * loss_k * rk
        shock = sum(offices[r] * SHOCK[r][t] for r in REGIONS) * loss_k * rk
        ev = {}
        e = EVENTS['inspection']; ev['inspection'] = e['fine'] if (year == e['year'] and c['lvl'][e['func']] < 2) else 0
        e = EVENTS['cyber']; ev['cyber'] = e['loss'] if (year == e['year'] and c['lvl'][e['func']] < 2) else 0
        e = EVENTS['talent']; ev['talent'] = e['cut'] * inc if (year == e['year'] and c['lvl'][e['func']] < 2) else 0
        events = sum(ev.values())
        profit = inc - upkeep - base_loss - shock - events
        budget_start = b['budget']
        budget_end = budget_start - c['invest'] + profit
        results.append(dict(year=year, income=inc, income_by_region=income, upkeep=upkeep, base_loss=base_loss, shock=shock,
                            events=events, ev=ev, profit=profit, invest=c['invest'], budget_start=budget_start,
                            budget_end=budget_end, value=budget_end + P['final_mult'] * profit, offices=offices,
                            level=dict(c['lvl']), span=c['span'], span_k=c['span_k'], policy=c['policy']))
        b['budget'] = budget_end
        b['offices'] = offices
        b['level'] = dict(c['lvl'])
    return results


def play(all_decisions):
    """all_decisions[год-1][банк] -> решения. Возвращает results[год-1][банк]."""
    state = new_state(len(all_decisions[0]))
    return [play_year(state, all_decisions[y - 1], y) for y in YEARS]


def decision_cost(level_before, d):
    cost = sum(max(0, int(v or 0)) for v in d.get('offices', {}).values()) * P['open_cost']
    lvl = dict(level_before)
    for f in d.get('up', []):
        if lvl[f] < 4:
            lvl[f] += 1
            cost += P['level_cost'][lvl[f]]
    if d.get('analytics'):
        cost += P['analytics']
    return cost


if __name__ == '__main__':
    # Пример из правил: четыре банка, первый год
    demo = [[dict(offices={'NORTH': 1, 'SOUTH': 1}, up=['R', 'S'], policy='С'),
             dict(offices={'NORTH': 1, 'VALLEY': 1, 'SOUTH': 1, 'SEZ': 1}, policy='А'),
             dict(offices={'VALLEY': 2}, up=['R', 'D'], policy='С'),
             dict(up=['R', 'D', 'P', 'S'], policy='О')]] + [[dict(policy='С')] * 4] * 3
    for y, res in enumerate(play(demo), 1):
        print('Год', y)
        for i, r in enumerate(res, 1):
            print('  Банк %d: доход %6.1f сеть %5.1f потери %5.1f спад %5.1f события %5.1f прибыль %6.1f инвест %5.1f бюджет %6.1f стоимость %6.1f' % (
                i, r['income'], r['upkeep'], r['base_loss'], r['shock'], r['events'], r['profit'], r['invest'], r['budget_end'], r['value']))
