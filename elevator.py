from boxlift_api import Command
import coloredlogs
import logging

coloredlogs.install()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Elevator(object):
    def __init__(self, state, floors):
        self.cur_direction = 0
        self.next_direction = 0
        self.location = 0
        self.last_floor = 0
        self.speed = 0
        self.wait_count = 0
        self.stops = []
        self.el_id = state['id']
        self.floors = floors
        self.update_state(state)
        self.bored = False

    def __repr__(self):
        return "Elevator(id=%d, location=%d, speed=%d, cur_direction=%d, " \
            "next_direction=%d, stops=%s)" % (self.el_id, self.location,
                                              self.speed, self.cur_direction,
                                              self.next_direction, self.stops)

    def process_request(self, request):
        """Handles an external request, returns True if it will, Flase
        otherwise"""

        # See if we're allowed to go to that floor
        will_do = self.go_to(request.floor, request.direction)

        # If we'll do it, make it so
        if will_do:
            self.next_direction = request.direction

        return will_do

    def is_on_the_way(self, floor, direction):
        """Tests if a floor is on the current trajectory"""
        if self.cur_direction == 1:
            will_do = self.location < floor
        elif self.cur_direction == -1:
            will_do = self.location > floor
        else:
            will_do = True

        # Check the desired direction
        if self.next_direction != 0:
            # If the requested direction is different than where we're going
            # then nope
            will_do &= self.next_direction == direction

        return will_do

    def go_to(self, floor, direction):
        """Put the elevator on a course for a new floor"""
        result = False

        # Check if we want to visit this place
        if self.is_on_the_way(floor, direction):
            self.process_buttons([floor])
            result = True

        return result

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
        if self.last_floor == self.location:
            self.wait_count += 1
        else:
            self.wait_count = 0
        self.last_floor = self.location
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
        elif self.stops[0] > self.location:
            self.cur_direction = 1
        elif self.stops[0] < self.location:
            self.cur_direction = -1
        elif self.stops[0] == self.location and len(self.stops) > 1:
            self.speed = 0
        else:
            self.cur_direction = self.next_direction
            self.next_direction = 0
            self.speed = 0

        self.bored = self.wait_count > 1

        return Command(self.el_id, self.cur_direction, self.speed)

    def calculate_distance(self, request):
        # The distance in floors between the current and the request
        distance = abs(self.location - request.floor)

        if not self.is_on_the_way(request.floor, request.direction):
            distance += self.floors

        if request.floor in self.stops:
            distance *= 0

        return distance
