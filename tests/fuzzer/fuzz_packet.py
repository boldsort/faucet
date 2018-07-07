#!/usr/bin/env python3

"""Run AFL repeatedly with externally supplied generated packet from STDIN."""

import logging
import sys
from faucet import faucet
from faucet import faucet_experimental_api
from ryu.controller import dpset
import afl
import Fake


logging.disable(logging.CRITICAL)


def main():
    # run faucet
    application = faucet.Faucet(
        dpset=dpset.DPSet(),
        faucet_experimental_api=faucet_experimental_api.FaucetExperimentalAPI())
    application.start()

    # make sure dps are running
    for valve in list(application.valves_manager.valves.values()):
        valve.dp.running = True

    while afl.loop(1000):
        # receive input from afl
        rcv = sys.stdin.read()
        data = None
        try:
            data = bytearray.fromhex(rcv)
        except (ValueError, TypeError):
            continue

        # create fake packet
        dp = Fake.Datapath(1)
        msg = Fake.Message(datapath=dp, cookie=1524372928, port=1, data=data, in_port=1)
        pkt = Fake.RyuEvent(msg)

        # send fake packet to faucet
        application.packet_in_handler(pkt)


if __name__ == "__main__":
    main()
