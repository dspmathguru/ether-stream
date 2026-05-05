from migen import *
from litex.soc.interconnect.stream import Endpoint
from litex.soc.interconnect.csr import AutoCSR, CSRStatus, CSRStorage


class MyLightweightProtocol(Module, AutoCSR):
    def __init__(self, data_width=256):
        # RX path: from Ethernet → clean payload
        # "last" is added automatically — do NOT declare it
        self.sink   = Endpoint([("data", data_width)])
        self.source = Endpoint([("data", data_width)])

        # TX path: from user logic → Ethernet
        self.user_sink   = Endpoint([("data", data_width)])
        self.user_source = Endpoint([("data", data_width)])

        # Control / Status registers
        self.seq_num    = CSRStorage(32)
        self.tx_packets = CSRStatus(32)
        self.rx_packets = CSRStatus(32)
        self.errors     = CSRStatus(32)

        # === Simple RX logic ===
        rx_state = Signal()   # 0 = header, 1 = payload

        self.sync += [
            If(self.sink.valid & self.sink.ready,
                If(~rx_state,
                    self.rx_packets.status.eq(self.rx_packets.status + 1),
                    rx_state.eq(1),
                ).Else(
                    self.source.valid.eq(1),
                    self.source.data.eq(self.sink.data),
                    self.source.last.eq(self.sink.last),
                    If(self.sink.last,
                        rx_state.eq(0)
                    )
                )
            )
        ]

        self.comb += [
            self.sink.ready.eq(~rx_state | self.source.ready),
            self.source.valid.eq(rx_state & self.sink.valid),
        ]

        # === Simple TX logic (pass-through for now) ===
        self.comb += [
            self.user_source.valid.eq(self.user_sink.valid),
            self.user_source.data.eq(self.user_sink.data),
            self.user_source.last.eq(self.user_sink.last),
            self.user_sink.ready.eq(self.user_source.ready),
        ]

        self.sync += [
            If(self.user_sink.valid & self.user_sink.ready & self.user_sink.last,
                self.tx_packets.status.eq(self.tx_packets.status + 1)
            )
        ]
