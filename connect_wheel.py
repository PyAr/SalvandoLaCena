import time
import math
from constants import FIFO_WHEEL_FILE


def convert_speed_value(value):
    # Fixme: Need to get linear regresion
    try:
        converted_value = -1 * math.log10(-value + 497) + 2.22
    except:
        converted_value = None
    return converted_value


def read_wheel():
    fp = open(FIFO_WHEEL_FILE)
    while True:
        time.sleep(0.1)
        raw_value = int(fp.readline())
        converted_value = convert_speed_value(raw_value)
        #print(raw_value, converted_value)
        if converted_value is not None:
            yield converted_value


if __name__=="__main__":
    for value in read_wheel():
        print("el value, ",value)
