from boxlift_api import Command


class Elevator:
    def __init__(self, el_id):
        self.direction = 0
        self.location = 0
        self.speed = 0
        self.stops = []
        self.el_id = el_id

    def go_to(self, floor):
        """Put the elevator on a course for a new floor"""
        # TODO: handle buttons first
        if self.direction == -1 and floor > self.location:
            return False
        elif self.direction == 1 and floor < self.location:
            return False

        self.process_buttons([floor])
        return True

    def sort_stops(self):
        """Sorts the stops in the current direction order"""
        self.stops = sorted(self.stops, reverse=(self.direction == -1))

    def process_buttons(self, buttons):
        """Get a union between the stops we have currenty and the newly reported
        ones"""
        self.stops = list(set(self.stops) | set(buttons))
        self.sort_stops()

    def update_state(self, state):
        """Update ourselves with the latest state from the API"""
        self.location = state.get('floor', 0)
        self.process_buttons(state.get('buttons_pressed', []))

    def get_command(self):
        """Returns a command object for sending to the API"""
        self.speed = 1
        if self.stops[-1] > self.location:
            self.direction = 1
        elif self.stops[-1] < self.location:
            self.direction = -1
        else:
            self.direction = 0
            self.speed = 0

        return Command(self.el_id, self.direction, self.speed)
