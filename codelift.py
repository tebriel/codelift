#!/usr/bin/env python3

import json
import collections
from elevator import Elevator
from boxlift_api import PYCON2015_EVENT_NAME, BoxLift

PLANS = ['training_1', 'training_2', 'training_3', 'ch_rnd_500_1']

Request = collections.namedtuple('Request', ['direction', 'floor'])
CommandTuple = collections.namedtuple('Command', ['id', 'direction', 'speed'])


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


def build_elevators(state):
    """Build our elevator objects"""
    elevators = [0] * len(state['elevators'])
    for elevator in state['elevators']:
        elevators[elevator['id']] = Elevator(elevator)
    return elevators


def process_elevators(state, elevators):
    """Handle the elevator state objects"""
    for elevator in state['elevators']:
        elevators[elevator['id']].update_state(elevator)


def process_requests(state, elevators):
    """Handle the requests from the state object"""
    # import pdb; pdb.set_trace()
    for request in state['requests']:
        for elevator in elevators:
            if elevator.next_direction == 0:
                elevator.process_request(request)
                break


def run_elevator(boxlift):
    state = boxlift.send_commands()
    elevators = build_elevators(state)
    steps = 0
    while state.get('status', 'finished') == 'in_progress':
        print("\n\nStep %d\n\n" % (steps))
        process_elevators(state, elevators)
        process_requests(state, elevators)

        to_send = [e.get_command() for e in elevators]
        state = boxlift.send_commands(to_send)
        for e in elevators:
            print(e)
        print("Requests: %s " % (state['requests']))
        steps += 1

    print(state)
    for elevator in elevators:
        print(elevator)
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
    print("Finished plan: %s" % (plan))

if __name__ == '__main__':
    init_boxlift(PLANS[1])
