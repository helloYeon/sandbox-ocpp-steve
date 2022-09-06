#! /usr/bin/env python3
import asyncio
import logging
import websockets


from ocpp.v16 import call, call_result
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.call_result import (
    BootNotificationPayload,
)
from ocpp.v16.enums import (
    DataTransferStatus,
    Action,
)

logging.basicConfig(level=logging.INFO)

###########################
# Parameters
###########################
CP_ID = "my-cp-001"
CP_VENDOR = "MY-VENDOR"
CP_SERIAL = "MY-SERIAL-001"
CP_MODEL = "MY-MODEL"

WS_ENDPOINT = f"ws://localhost:8180/steve/websocket/CentralSystemService/{CP_ID}"


class ChargePoint(cp):
    @on(Action.DataTransfer)
    async def respond_datatransfer(self, vendor_id, message_id, data):
        print(f"DataTransfer Vendor ID -> {vendor_id}")
        print(f"DataTransfer Message ID -> {message_id}")
        print(f"Datatransfer Data -> {data}")

        if vendor_id != CP_VENDOR:
            message = f"{CP_ID}:NG Vendor ID ({vendor_id}) not valid , please set correct vendor id"
            return call_result.DataTransferPayload(DataTransferStatus.rejected, message)

        message = f"{CP_ID}:OK"
        return call_result.DataTransferPayload(DataTransferStatus.accepted, message)

    async def send_boot_notification(self, model, serial, vendor):
        req = call.BootNotificationPayload(
            charge_point_model=model,
            charge_point_serial_number=serial,
            charge_point_vendor=vendor,
        )
        response: BootNotificationPayload = await self.call(req)
        print(f"Res -> {response}")
        return response


async def main():
    async with websockets.connect(WS_ENDPOINT, subprotocols=["ocpp1.6"]) as ws:
        cp = ChargePoint(CP_ID, ws, response_timeout=5)
        await asyncio.gather(
            cp.start(),
            cp.send_boot_notification(CP_MODEL, CP_SERIAL, CP_VENDOR),
        )


if __name__ == "__main__":
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()

