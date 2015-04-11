#!/usr/bin/env python3

import json
import collections
from elevator import Elevator
from boxlift_api import PYCON2015_EVENT_NAME, BoxLift, Command

PLANS = ['training_1']

Request = collections.namedtuple('Request', ['direction', 'floor'])
CommandTuple = collections.namedtuple('Command', ['id', 'direction', 'speed'])


def process_requests(state, requests):
    for request in state.get('requests', []):
        direction = request.get('direction', 0)
        floor = request.get('floor', 0)
        req = Request(direction, floor)
        if req in requests:
            continue
        requests.append(req)
        print(requests)


def process_elevator_buttons(state):
    commands = []
    for elevator in state['elevators']:
        for button_pressed in elevator['buttons_pressed']:
            direction = 0
            if elevator['floor'] > button_pressed:
                direction = -1
            elif elevator['floor'] < button_pressed:
                direction = 1
            command = CommandTuple(elevator['id'], direction, 1)
            if command not in commands:
                commands.append(command)
    return commands


def run_elevator(boxlift):
    state = boxlift.send_commands()
    new_requests = []
    elevator_tasks = []
    steps = 0
    while state.get('status', 'finished') != 'finished':
        process_requests(state, new_requests)

        commands = process_elevator_buttons(state)

        for elevator in state['elevators']:
            cur_floor = elevator['floor']
            el_id = elevator['id']
            for request in new_requests:
                new_command = None
                if cur_floor < request.floor:
                    new_command = CommandTuple(el_id, 1, 1)
                elif cur_floor > request.floor:
                    new_command = CommandTuple(el_id, -1, 1)
                elif cur_floor == request.floor:
                    new_command = CommandTuple(el_id, request.direction, 0)

                if new_command is not None and new_command not in commands:
                    commands.append(new_command)

        to_send = []
        ele_seen = []
        for com in commands:
            print(com.id, com.direction, com.speed)
            if com.id not in ele_seen:
                to_send.append(Command(com.id, com.direction, com.speed))
                ele_seen.append(com.id)
        state = boxlift.send_commands(to_send)
        steps += 1

    print(state)
    print("%d steps" % (steps))


def init_boxlift(plan):
    with open('codeliftsettings.json') as settings:
        cl_settings = json.load(settings)
    bot_name = cl_settings['bot_name']
    email = cl_settings['email']
    registration_id = cl_settings['registration_id']
    event_name = PYCON2015_EVENT_NAME
    bl = BoxLift(bot_name, plan, email, registration_id, event_name)
    run_elevator(bl)

if __name__ == '__main__':
    init_boxlift(PLANS[0])
