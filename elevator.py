from boxlift_api import Command


class Elevator:
    def __init__(self, state):
        self.cur_direction = 0
        self.next_direction = 0
        self.location = 0
        self.speed = 0
        self.stops = []
        self.el_id = state['id']
        self.update_state(state)

    def __repr__(self):
        return "Elevator(id=%d, location=%d, speed=%d, cur_direction=%d, " \
            "next_direction=%d, stops=%s)" % (self.el_id, self.location,
                                              self.speed, self.cur_direction,
                                              self.next_direction, self.stops)

    def process_request(self, request):
        """Handles a request, returns True if it will, Flase otherwise"""
        will_do = self.go_to(request['floor'])
        if will_do:
            self.next_direction = request['direction']

        return will_do

    def go_to(self, floor):
        """Put the elevator on a course for a new floor"""
        # TODO: handle buttons first
        if self.cur_direction == -1 and floor > self.location:
            return False
        elif self.cur_direction == 1 and floor < self.location:
            return False

        self.process_buttons([floor])
        return True

    def sort_stops(self):
        """Sorts the stops in the current cur_direction order"""
        self.stops = sorted(self.stops, reverse=(self.cur_direction == -1))

    def process_buttons(self, buttons):
        """Get a union between the stops we have currenty and the newly reported
        ones"""
        self.stops = list(set(self.stops) | set(buttons))
        self.sort_stops()

    def update_state(self, state):
        """Update ourselves with the latest state from the API"""
        self.location = state.get('floor', 0)
        self.stops = list(set(self.stops) - set([self.location]))
        self.process_buttons(state.get('buttons_pressed', []))

    def get_command(self):
        """Returns a command object for sending to the API"""
        self.speed = 1
        if len(self.stops) == 0:
            self.cur_direction = self.next_direction
            self.next_direction = 0
            self.speed = 0
        elif self.stops[-1] > self.location:
            self.cur_direction = 1
        elif self.stops[-1] < self.location:
            self.cur_direction = -1
        else:
            self.cur_direction = self.next_direction
            self.next_direction = 0
            self.speed = 0

        return Command(self.el_id, self.cur_direction, self.speed)
