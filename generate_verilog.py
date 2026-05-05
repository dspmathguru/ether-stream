#! /usr/bin/env python
from migen import *
from migen.fhdl import verilog
from ckts.HighPerfRawEthernetStreamer import HighPerfRawEthernetStreamer
import os
import shutil

if os.path.exists("build"):
    shutil.rmtree("build")
os.makedirs("build", exist_ok=True)

dut = HighPerfRawEthernetStreamer(data_width=256)

verilog.convert(
    dut,
    name="HighPerfRawEthernetStreamer"
).write("build/HighPerfRawEthernetStreamer.v")

print("Verilog generated successfully in build/")
