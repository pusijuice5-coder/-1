# -*- coding: utf-8 -*-
"""Демонстрационная партия на четыре банка: для скриншотов, примера в руководстве и пробного прогона ведущего."""
import game as G

NAMES = ['Алмаз', 'Барс', 'Вектор', 'Гранит']
# Алмаз — сбалансированный рост; Барс — быстрая сеть без функций; Вектор — ставка на Долину и СЭЗ; Гранит — осторожный.
DECISIONS = [
    [dict(offices={'NORTH': 1, 'SOUTH': 1}, up=['R', 'S'], policy='С'),
     dict(offices={'NORTH': 1, 'VALLEY': 1, 'SOUTH': 1, 'SEZ': 1}, up=[], policy='А'),
     dict(offices={'VALLEY': 2}, up=['R', 'D'], policy='С'),
     dict(offices={'NORTH': 1}, up=['R', 'D', 'P'], policy='О')],
    [dict(offices={'SEZ': 1}, up=['D', 'P'], policy='С', analytics=True),
     dict(offices={'SOUTH': 1, 'SEZ': 1}, up=[], policy='А'),
     dict(offices={'SOUTH': 1, 'SEZ': 1}, up=['P'], policy='А'),
     dict(offices={'SOUTH': 1}, up=['S'], policy='С')],
    [dict(offices={'SEZ': 1, 'SOUTH': 1}, up=['R'], policy='О', analytics=True),
     dict(offices={'NORTH': 1, 'CAP': 1}, up=['P'], policy='А'),
     dict(offices={'SEZ': 1}, up=['S', 'R'], policy='С'),
     dict(offices={'SEZ': 1}, up=['R'], policy='С', analytics=True)],
    [dict(offices={}, up=['P', 'S'], policy='С', analytics=True),
     dict(offices={'SEZ': 1}, up=['R', 'D'], policy='А'),
     dict(offices={'VALLEY': -1, 'SOUTH': 1}, up=['D'], policy='С', analytics=True),
     dict(offices={'SOUTH': 1}, up=['S', 'P'], policy='А')],
]
FORECASTS = [[70, 60, 65, 45], [115, 110, 120, 80], [110, 100, 150, 100], [200, 130, 160, 170]]


def check():
    state = G.new_state(len(NAMES))
    out = []
    for y in G.YEARS:
        for i, d in enumerate(DECISIONS[y - 1]):
            cost = G.decision_cost(state[i]['level'], d)
            assert cost <= max(state[i]['budget'], 0) + 1e-9, ('бюджет', y, NAMES[i], cost, round(state[i]['budget'], 1))
        out.append(G.play_year(state, DECISIONS[y - 1], y))
    return out


if __name__ == '__main__':
    res = check()
    for y, yr in enumerate(res, 1):
        print('Год', y)
        for i, r in enumerate(yr):
            print('  %-7s доход %6.1f сеть %5.1f потери %5.1f события %5.1f прибыль %6.1f инвест %5.1f бюджет %6.1f стоимость %6.1f  офисы %s уровни %s' % (
                NAMES[i], r['income'], r['upkeep'], r['base_loss'] + r['shock'], r['events'], r['profit'], r['invest'], r['budget_end'], r['value'],
                '/'.join(str(r['offices'][x]) for x in G.REGIONS), ''.join(str(r['level'][f]) for f in G.FUNCS)))
