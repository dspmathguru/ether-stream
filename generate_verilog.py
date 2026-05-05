#! /usr/bin/env python
from migen import *
from migen.fhdl import verilog
from ckts.HighPerfRawEthernetStreamer import HighPerfRawEthernetStreamer
import os
import shutil

if os.path.exists("build"):
    shutil.rmtree("build")
os.makedirs("build", exist_ok=True)

# Original module
dut = HighPerfRawEthernetStreamer(data_width=256)

# Wrapper that explicitly exposes everything we need
class Wrapper(Module):
    def __init__(self):
        self.submodules.dut = dut

        # Top-level ports we want to drive from cocotb
        self.clk         = Signal()
        self.rst         = Signal()
        self.start       = Signal()
        self.total_bytes = Signal(32)
        self.done        = Signal()

        # Connect internal signals to top-level ports
        self.comb += [
            dut.clk.eq(self.clk),
            dut.rst.eq(self.rst),
            dut.start.eq(self.start),
            dut.total_bytes.eq(self.total_bytes),
        ]
        self.comb += self.done.eq(dut.done)

        # Connect streams (we'll drive sink_* and read source_* from cocotb)
        self.sink_valid = Signal()
        self.sink_ready = Signal()
        self.sink_data  = Signal(256)
        self.sink_last  = Signal()

        self.source_valid = Signal()
        self.source_ready = Signal()
        self.source_data  = Signal(256)
        self.source_last  = Signal()

        self.comb += [
            dut.sink.valid.eq(self.sink_valid),
            self.sink_ready.eq(dut.sink.ready),
            dut.sink.data.eq(self.sink_data),
            dut.sink.last.eq(self.sink_last),

            self.source_valid.eq(dut.source.valid),
            dut.source.ready.eq(self.source_ready),
            self.source_data.eq(dut.source.data),
            self.source_last.eq(dut.source.last),
        ]

top = Wrapper()

# Explicitly list all ports we want
ios = {
    top.clk,
    top.rst,
    top.start,
    top.total_bytes,
    top.done,
    top.sink_valid,
    top.sink_ready,
    top.sink_data,
    top.sink_last,
    top.source_valid,
    top.source_ready,
    top.source_data,
    top.source_last,
}

verilog.convert(
    top,
    name="HighPerfRawEthernetStreamer",
    ios=ios
).write("build/HighPerfRawEthernetStreamer.v")

print("Verilog generated successfully in build/")

