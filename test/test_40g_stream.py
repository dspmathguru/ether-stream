import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotbext.eth import EthernetFrame, EtherType

@cocotb.test()
async def test_high_perf_stream(dut):
    clock = Clock(dut.clk, 6.4, units="ns")   # ~156.25 MHz
    cocotb.start_soon(clock.start())

    # Reset
    dut.rst.value = 1
    await Timer(100, units="ns")
    dut.rst.value = 0

    # Example: send a large 2D array as a stream
    total_bytes = 1024 * 1024 * 8   # 8 MB example

    dut.start.value = 1
    dut.total_bytes.value = total_bytes

    # Feed data into sink (you can make this smarter)
    for i in range(10000):
        dut.sink.valid.value = 1
        dut.sink.data.value = i
        dut.sink.last.value = (i == 9999)
        await RisingEdge(dut.clk)
        while not dut.sink.ready.value:
            await RisingEdge(dut.clk)

    # Now the Python side should receive frames via cocotb
    # and verify sequence + offset + data
    print("Simulation finished")
