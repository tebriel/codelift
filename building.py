import logging
from elevator import Elevator
from collections import namedtuple
from boxlift_api import PYCON2015_EVENT_NAME, BoxLift

logger = logging.getLogger(__name__)
Request = namedtuple('Request', ['floor', 'direction'])


class Building:
    def __init__(self, plan, settings):
        self.bot_name = settings['bot_name']
        self.email = settings['email']
        self.registration_id = settings['registration_id']
        self.event_name = PYCON2015_EVENT_NAME
        self.plan = plan
        self.acked = []

    def connect(self):
        self.bl = BoxLift(self.bot_name, self.plan, self.email,
                          self.registration_id, self.event_name)

    def build_elevators(self, state):
        """Build our elevator objects"""
        self.elevators = [0] * len(state['elevators'])
        for elevator in state['elevators']:
            self.elevators[elevator['id']] = Elevator(elevator)

    def process_elevators(self, state):
        """Handle the elevator state objects"""
        for elevator in state['elevators']:
            self.elevators[elevator['id']].update_state(elevator)

    def process_requests(self, state):
        """Handle the requests from the state object"""
        for request in state['requests']:
            req_tup = Request(request['floor'], request['direction'])
            if req_tup in self.acked:
                continue
            for elevator in self.elevators:
                if elevator.process_request(request):
                    self.acked.append(req_tup)
                    break

    def generate_commands(self):
        """Gathers the commands from the elevators and clears finished
        requests"""
        commands = []
        for elevator in self.elevators:
            commands.append(elevator.get_command())
            if elevator.speed == 0:
                request = Request(elevator.location, elevator.cur_direction)
                self.acked = list(set(self.acked) - {request})
        return commands

    def do_step(self, state):
        self.process_elevators(state)
        self.process_requests(state)

        return self.generate_commands()

    def start(self):
        state = self.bl.send_commands()
        self.build_elevators(state)

        steps = 0
        while state.get('status', 'finished') == 'in_progress':
            logger.info("Step %d", steps)
            to_send = self.do_step(state)
            state = self.bl.send_commands(to_send)
            for e in self.elevators:
                logger.debug(e)
            logger.info("Requests: %s ", state['requests'])
            steps += 1

        logger.info(state)
        for elevator in self.elevators:
            logger.debug(elevator)
        logger.info("%d steps", steps)
