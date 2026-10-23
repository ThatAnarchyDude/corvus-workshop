"""Fuchsia Gym (map 480): Yellow's Koga and three of his gym trainers in HeartGold's gym; native flow and the Soul Badge stay.

HG's gym has three trainers (Yellow has seven), so Juggler 8, Tamer 2 and the rest are deferred. The native reward stays.
"""
import gym_conversion

LEADER = 257
NATIVE = {136: ('JugglerData', 3), 84: ('JugglerData', 4), 83: ('TamerData', 1)}


def patch(rom, source):
    teams = gym_conversion.convert(rom, source, NATIVE, LEADER, 'KogaData')
    return dict(map=480, teams=teams, deferred='Juggler 7/8, Tamer 2, Yellow dialogue and the Koga-specific TM')
