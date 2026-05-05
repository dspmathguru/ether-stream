from migen import *
from litex.soc.interconnect.stream import Endpoint
from litex.soc.interconnect.csr import AutoCSR, CSRStatus, CSRStorage

class HighPerfRawEthernetStreamer(Module, AutoCSR):
    def __init__(self, data_width=256):
        self.clk = Signal()
        self.rst = Signal()

        # Correct way to create the clock domain
        self.clock_domains.cd_sys = ClockDomain()
        self.cd_sys.clk = self.clk
        self.cd_sys.rst = self.rst

        self.sink   = Endpoint([("data", data_width)])
        self.source = Endpoint([("data", data_width)])

        self.start       = Signal()
        self.total_bytes = Signal(32)
        self.done        = Signal()

        seq    = Signal(32, reset=0)
        offset = Signal(32, reset=0)
        payload_bytes = data_width // 8

        header = Cat(seq, self.total_bytes, offset, C(0, 32))

        self.comb += [
            self.source.valid.eq(self.sink.valid),
            self.source.last.eq(self.sink.last),
            self.source.data.eq(Cat(header, self.sink.data[128:])),
            self.sink.ready.eq(self.source.ready),
        ]

        self.sync += [
            If(self.rst,
                seq.eq(0),
                offset.eq(0),
                self.done.eq(0)
            ).Elif(self.start & self.sink.valid & self.sink.ready & self.sink.last,
                seq.eq(seq + 1),
                offset.eq(offset + payload_bytes),
                If(offset + payload_bytes >= self.total_bytes,
                    self.done.eq(1)
                )
            )
        ]
