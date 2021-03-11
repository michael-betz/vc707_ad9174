# verilator + litex_server simulation

Connect to a piece of emulated hardware (verilator simulation)
in the same way as connecting to real hardware.

## the setup

  * Add the serial2tcp plugin to verilator such that I can connect to the SOC UART from outside
  * Run litex_server to connect to the tcp socket instead to a serial port
    such that I can access the emulated wishbone bus from outside

## to run the `SampleGen` simulation

```bash
# all 3 run at the same time in separate windows ...
$ python3 sim_sample_gen.py
$ litex_server --uart --uart-port socket://localhost:1111
# Open test_samplegen.ipynb to interact with the simulation

gtkwave out/gateware/sim.vcd
# look for `TOP/sim/source_converter0` which is the DAC sample stream
```
