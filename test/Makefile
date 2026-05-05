SIM = verilator
TOPLEVEL_LANG = verilog

VERILOG_SOURCES = $(wildcard ../build/*.v)

TOPLEVEL = HighPerfRawEthernetStreamer
MODULE = test_ethernet_stream

# Verilator flags
EXTRA_ARGS += --trace --trace-structs
EXTRA_ARGS += -Wno-WIDTHEXPAND -Wno-INITIALDLY   # ← Add this line

include $(shell cocotb-config --makefiles)/Makefile.sim

