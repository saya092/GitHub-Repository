#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 19 10:50:21 2025

@author: monicahu
"""

import time, random, json

def simulate_sensor_data():
    rooms = {
        "B101": "empty",
        "B102": "empty",
        "B103": "empty"
    }

    while True:
        for room in rooms:
            rooms[room] = random.choice(["empty", "occupied"])
        with open("room_status.json", "w") as f:
            json.dump(rooms, f, indent=2)
        print("已更新感測器資料：", rooms)
        time.sleep(10)

# 呼叫主函式
simulate_sensor_data()