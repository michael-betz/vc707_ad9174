"""
Hello world (blinking LED) example for the vc707 with litex
"""
import sys
from migen import *
from litex_boards.platforms import vc707

p = vc707.Platform()


def main():
    led = p.request("user_led")
    module = Module()
    # 156.25 MHz / 2**26 = 2.33 Hz
    counter = Signal(26)
    module.comb += led.eq(counter[-1])
    module.sync += counter.eq(counter + 1)
    p.build(module)


if __name__ == '__main__':
    if "load" in sys.argv:
        prog = p.create_programmer()
        prog.load_bitstream("build/top.bit")
    else:
        main()
