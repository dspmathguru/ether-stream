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

class HighPerfRawEthernetStreamer(Module, AutoCSR):
    def __init__(self, data_width=256):
        # Incoming data stream (from your 2D array source / DMA / etc.)
        self.sink = Endpoint([("data", data_width)])

        # Outgoing stream to Ethernet MAC
        self.source = Endpoint([("data", data_width)])

        # Control interface
        self.start       = Signal()
        self.total_bytes = Signal(32)
        self.done        = Signal()

        # Internal state
        seq    = Signal(32)
        offset = Signal(32)

        # Header = seq(4) + total_bytes(4) + offset(4) + flags(4)
        # flags[0] = last chunk
        header = Cat(seq, self.total_bytes, offset, C(0, 32))

        self.comb += [
            self.source.valid.eq(self.sink.valid),
            self.source.last.eq(self.sink.last),
            # Insert 16-byte header at the beginning of each frame
            self.source.data.eq(Cat(header, self.sink.data[128:])),
            self.sink.ready.eq(self.source.ready),
        ]

        self.sync += [
            If(self.start,
                seq.eq(0),
                offset.eq(0),
                self.done.eq(0)
            ),
            If(self.sink.valid & self.sink.ready & self.sink.last,
                seq.eq(seq + 1),
                offset.eq(offset + (data_width // 8)),
                If(offset + (data_width // 8) >= self.total_bytes,
                    self.done.eq(1)
                )
            )
        ]
