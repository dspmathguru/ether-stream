from migen import *
from migen.sim import run_simulation
from MyLightweightProtocol import MyLightweightProtocol


def testbench(dut):
    # Send one simple packet (header + payload)
    # Header format (64 bits): seq[31:0] + length[15:0] + flags[15:0]
    # We send it as the first word (256-bit data width)
    header = 0x0000000A_0008_0001_0000000000000000_0000000000000000_0000000000000000_0000000000000000

    yield dut.sink.valid.eq(1)
    yield dut.sink.data.eq(header)
    yield dut.sink.last.eq(1)
    yield
    yield dut.sink.valid.eq(0)
    yield dut.sink.last.eq(0)

    # Wait a few cycles and observe output
    for cycle in range(10):
        if (yield dut.source.valid):
            payload = (yield dut.source.data)
            print(f"Cycle {cycle}: Received payload = 0x{payload:064x}")
        yield

    print("Test finished successfully!")


if __name__ == "__main__":
    dut = MyLightweightProtocol(data_width=256)
    run_simulation(dut, testbench(dut), vcd_name="protocol.vcd")
    print("Simulation complete. VCD file generated: protocol.vcd")

