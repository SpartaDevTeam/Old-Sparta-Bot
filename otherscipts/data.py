import json
import asyncio


class Data:
    filename = "data.json"
    with open(filename, "r") as data_file:
        server_data = json.load(data_file)

    @staticmethod
    async def auto_update_data():
        while True:
            # erase file and dump data
            with open(Data.filename, "w") as data_file:
                json.dump(Data.server_data, data_file)

            await asyncio.sleep(10)

    @staticmethod
    def create_new_data():
        data_entry = {
            "active": False,
            "users": [],
            "urls": [],
            "channels": [],
            "welcome_msg": None,
            "leave_msg": None,
            "welcome_channel": None,
            "leave_channel": None,
            "join_role": None,
            "pay_respects": False,
            "afks": [],
            "prefix": "s!"
        }
        return data_entry
