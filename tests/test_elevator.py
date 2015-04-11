from elevator import Elevator
from nose.tools import assert_equals


class TestElevator:
    """Test the Elevator class and its internal methods"""
    def setup(self):
        self.elevator = Elevator(0)

    def test_go_to_up(self):
        """Elevator will go up"""
        will_do_it = self.elevator.go_to(2)
        assert self.elevator.stops[-1] == 2
        assert will_do_it is True

    def test_get_command(self):
        """Elevator will give the correct command object"""
        self.elevator.go_to(2)
        comm = self.elevator.get_command()

        assert comm.direction == 1
        assert comm.id == 0
        assert comm.speed == 1

    def test_process_buttons(self):
        """Will take buttons in and set up the next stops"""
        buttons = [2, 3]
        self.elevator.process_buttons(buttons)
        assert self.elevator.stops == buttons

        new_buttons = [3, 4]
        self.elevator.process_buttons(new_buttons)
        assert self.elevator.stops == [2, 3, 4]

    def test_update_state_no_buttons(self):
        """Takes in a state object with no buttons"""
        state = {
            'id': 1,
            'floor': 2
        }

        self.elevator.update_state(state)
        assert self.elevator.location == state['floor']

    def test_update_state_with_buttons(self):
        """Takes in a state object with buttons"""
        state = {
            'id': 1,
            'floor': 2,
            'buttons_pressed': [1, 2]
        }

        self.elevator.update_state(state)
        assert self.elevator.location == state['floor']
        assert self.elevator.stops == state['buttons_pressed']

    def test_update_state_with_more_buttons(self):
        """Updates the elevator state by adding more buttons"""
        self.elevator.process_buttons([1, 2])
        state = {
            'id': 1,
            'floor': 2,
            'buttons_pressed': [2, 3]
        }

        self.elevator.update_state(state)

        assert self.elevator.stops == [1, 2, 3]

    def test_update_state_with_high_dest(self):
        """Updating state with a higher destination updates buttons"""
        self.elevator.go_to(5)
        self.elevator.process_buttons([5, 6])

        assert_equals(self.elevator.stops, [5, 6])
        assert_equals(self.elevator.stops[-1], 6)

    def test_go_to_down(self):
        """Elevator will go to a lower floor"""
        self.elevator.location = 5
        self.elevator.go_to(3)
        comm = self.elevator.get_command()
        assert comm.id == 0
        assert comm.direction == -1
        assert comm.speed == 1

    def test_will_not_go_to(self):
        """Should refuse to go to a floor beacuse it's out of the way"""
        self.elevator.location = 5
        self.elevator.process_buttons([9])
        self.elevator.get_command()
        assert self.elevator.go_to(4) is False

    def test_process_request(self):
        """Handle a request object"""
        request = {
            "direction": 1,
            "floor": 5
        }
        will_do = self.elevator.process_request(request)
        assert will_do is True

    def test_elevator_request_up(self):
        """Works how I expect it to work"""
        cur_floor = 0
        while self.elevator.location < 5:
            request = {
                "direction": 1,
                "floor": 5
            }
            res = self.elevator.process_request(request)
            assert res is True
            comm = self.elevator.get_command()
            assert comm.direction == 1
            assert comm.speed == 1
            assert self.elevator.next_direction == 1
            cur_floor += 1
            state = {
                "floor": cur_floor,
                "id": 0
            }
            self.elevator.update_state(state)

        comm = self.elevator.get_command()
        assert comm.direction == 1
        assert self.elevator.speed == 0
