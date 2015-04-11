from elevator import Elevator
from boxlift_api import PYCON2015_EVENT_NAME, BoxLift


class Building:
    def __init__(self, plan, settings):
        bot_name = settings['bot_name']
        email = settings['email']
        registration_id = settings['registration_id']
        event_name = PYCON2015_EVENT_NAME
        self.bl = BoxLift(bot_name, plan, email, registration_id, event_name)

    def build_elevators(self, state):
        """Build our elevator objects"""
        elevators = [0] * len(state['elevators'])
        for elevator in state['elevators']:
            elevators[elevator['id']] = Elevator(elevator)
        return elevators

    def process_elevators(self, state, elevators):
        """Handle the elevator state objects"""
        for elevator in state['elevators']:
            elevators[elevator['id']].update_state(elevator)

    def process_requests(self, state, elevators):
        """Handle the requests from the state object"""
        # import pdb; pdb.set_trace()
        for request in state['requests']:
            for elevator in elevators:
                if elevator.process_request(request):
                    break

    def start(self):
        state = self.bl.send_commands()
        elevators = self.build_elevators(state)
        steps = 0
        while state.get('status', 'finished') == 'in_progress':
            print("\n\nStep %d\n\n" % (steps))
            self.process_elevators(state, elevators)
            self.process_requests(state, elevators)

            to_send = [e.get_command() for e in elevators]
            state = self.bl.send_commands(to_send)
            for e in elevators:
                print(e)
            print("Requests: %s " % (state['requests']))
            steps += 1

        print(state)
        for elevator in elevators:
            print(elevator)
        print("%d steps" % (steps))
