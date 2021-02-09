#!/usr/bin/env python3
from litex import RemoteClient
from litescope import LiteScopeAnalyzerDriver
import sys
sys.path.append('../..')
from common import *


r = conLitexServer('../build/csr.csv')

# # #

analyzer = LiteScopeAnalyzerDriver(
    r.regs,
    "analyzer",
    config_csv="../build/analyzer.csv",
    debug=True
)
analyzer.configure_subsampler(1)
analyzer.configure_group(0)
trig = sys.argv[1]
if trig != 'snapshot':
    if trig[0] == '~':
        analyzer.add_falling_edge_trigger(trig[1:])
    else:
        analyzer.add_rising_edge_trigger(trig)
print("Trigger:", trig)
analyzer.run(offset=32)
analyzer.wait_done()
analyzer.upload()
analyzer.save("dump.vcd", samplerate=160e6)

# # #

r.close()
