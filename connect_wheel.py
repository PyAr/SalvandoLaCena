import time
import math
from constants import FIFO_WHEEL_FILE


def convert_speed_value(value):
    try:
        converted_value = -1 * math.log10(-value + 497) + 2.22
    except:
        converted_value = None
    return converted_value


def convert_speed_value_manual(value):
    if 2<=value<4: return -1
    if 4<=value<56: return -0.8
    if 56<=value<148: return -0.7
    if 148<=value<200: return -0.6
    if 200<=value<237: return -0.5
    if 237<=value<303: return -0.4
    if 303<=value<341: return -0.3
    if 341<=value<375: return -0.2
    if 375<=value<400: return -0.1
    if 400<=value<444: return -0.05
    if 444<=value<483: return 0
    if 483<=value<500: return 0.05
    if 500<=value<512: return 0.1
    if 512<=value<541: return 0.2
    if 541<=value<571: return 0.3
    if 571<=value<600: return 0.4
    if 600<=value<615: return 0.5
    if 615<=value<633: return 0.6
    if 633<=value<642: return 0.7
    if 642<=value<652: return 0.8
    if 652<=value<655: return 0.9
    if 655<=value<663: return 1
    if value>663: return None


def convert_speed_value_linear(value):
    # if the value is greater than 496 it means hardware error, loose pin, etc
    # Therefore ignore the reading

    if value > 496:
        return

    try:
        converted_value = (value / 250) - 1
    except:
        converted_value = None
    return converted_value


def read_wheel():
    fp = open(FIFO_WHEEL_FILE)
    while True:
        time.sleep(0.05)
        raw_value = int(fp.readline())
        converted_value = convert_speed_value_manual(raw_value)
        #print(raw_value, converted_value)
        if converted_value is not None:
            yield converted_value


if __name__=="__main__":
    for value in read_wheel():
        pass
        #print("el value, ",value)
