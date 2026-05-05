import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

@cocotb.test()
async def test_high_perf_raw_ethernet(dut):
    """Basic test for HighPerfRawEthernetStreamer"""

    # Use sys_clk (what Migen actually generated)
    clock = Clock(dut.sys_clk, 6.4, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut.sys_rst.value = 1
    await Timer(200, units="ns")
    dut.sys_rst.value = 0
    await RisingEdge(dut.sys_clk)

    total_bytes = 1024 * 1024 * 2   # 2 MB example

    dut.start.value = 1
    dut.total_bytes.value = total_bytes

    received = 0
    for i in range(5000):
        dut.sink.valid.value = 1
        dut.sink.data.value = i
        dut.sink.last.value = (i == 4999)
        await RisingEdge(dut.sys_clk)

        if int(dut.source.valid.value):
            received += 1

        while not int(dut.sink.ready.value):
            await RisingEdge(dut.sys_clk)

    dut.sink.valid.value = 0
    await RisingEdge(dut.sys_clk)

    print(f"Test finished. Frames generated: {received}")
    assert received > 0, "No frames were produced!"
    print("✅ cocotb test passed!")
