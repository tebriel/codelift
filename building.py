import coloredlogs
import logging
# import webbrowser
from elevator import Elevator
from collections import namedtuple
from boxlift_api import PYCON2015_EVENT_NAME, BoxLift, Command

coloredlogs.install()
logging.basicConfig(level=logging.DEBUG)
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
        self.floors = 0

    def connect(self):
        self.bl = BoxLift(self.bot_name, self.plan, self.email,
                          self.registration_id, self.event_name)
        # webbrowser.open_new_tab(self.bl.visualization_url)

    def build_elevators(self, state):
        """Build our elevator objects"""
        self.elevators = [0] * len(state['elevators'])
        for elevator in state['elevators']:
            self.elevators[elevator['id']] = Elevator(elevator, self.floors)

    def process_elevators(self, state):
        """Handle the elevator state objects"""
        for elevator in state['elevators']:
            self.elevators[elevator['id']].update_state(elevator)

    def process_requests(self, state):
        """Handle the requests from the state object"""
        for request_obj in state['requests']:
            request = Request(request_obj['floor'], request_obj['direction'])
            if request in self.acked:
                continue
            elevator = self.find_cheapest_elevator(request, self.floors)
            if elevator is not None:
                elevator.process_request(request)
                self.acked.append(request)

    def find_cheapest_elevator(self, request, floors):
        """Finds the cheapest elevator to send

        Sends none if the cost is > # of floors
        """
        costs = []
        for elevator in self.elevators:
            costs.append(elevator.calculate_distance(request))
        cheapest = costs.index(min(costs))
        if costs[cheapest] <= floors:
            return self.elevators[cheapest]

    def generate_commands(self):
        """Gathers the commands from the elevators and clears finished
        requests"""
        commands = []
        for elevator in self.elevators:
            commands.append(elevator.get_command())
            if elevator.speed == 0:
                request = Request(elevator.location, elevator.cur_direction)
                self.acked = list(set(self.acked) - {request})
        self.manage_idle_elevators(commands)
        return commands

    def do_step(self, state):
        self.process_elevators(state)
        self.process_requests(state)

        return self.generate_commands()

    def start(self):
        state = self.bl.send_commands()
        self.floors = state['floors']
        self.build_elevators(state)

        steps = 0
        while state.get('status', 'finished') == 'in_progress':
            logger.info("Step %d", steps)
            to_send = self.do_step(state)
            state = self.bl.send_commands(to_send)
            for e in self.elevators:
                logger.info(e)
            logger.info("Requests: %s", state['requests'])
            logger.info("Acked Requests: %s", self.acked)
            steps += 1

        logger.info(state)
        for elevator in self.elevators:
            logger.info(elevator)
        logger.info("%d steps", steps)

    def manage_idle_elevators(self, commands):
        average = 0
        bored_elevators = []
        for elevator in self.elevators:
            average += elevator.location
            if elevator.bored:
                bored_elevators.append(elevator)
        average /= len(self.elevators)

        half_floors = self.floors // 2
        quarter_floors = self.floors // 4
        if average < half_floors:
            for elevator in bored_elevators:
                if abs(half_floors - elevator.location) < quarter_floors:
                    continue
                if elevator.location > half_floors:
                    direction = -1
                else:
                    direction = 1

                command = Command(elevator.el_id, direction, 1)
                commands[elevator.el_id] = command
