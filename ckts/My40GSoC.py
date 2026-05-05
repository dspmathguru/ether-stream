from litex.soc.integration.soc import SoC
from litex.soc.cores.ethernet import LiteEthPHYNative  # or your custom PHY

class My40GSoC(SoC):
    def __init__(self, platform):
        super().__init__(platform)

        # Ethernet PHY (you will replace with Arria 10 Native PHY wrapper)
        self.submodules.eth_phy = LiteEthPHYNative(...)  

        self.submodules.eth = LiteEth(phy=self.eth_phy, mac_address=0x123456789abc)

        # Your lightweight protocol
        self.submodules.protocol = MyLightweightProtocol(data_width=256)

        # Connect streams
        self.comb += [
            self.eth.source.connect(self.protocol.sink),
            self.protocol.user_source.connect(self.eth.sink),
        ]

        # Expose control registers
        self.add_csr("protocol")
