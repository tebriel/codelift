from elevator import Elevator
from nose.tools import assert_equals


class TestElevator:
    def setup(self):
        self.elevator = Elevator(1)

    def test_go_to_up(self):
        will_do_it = self.elevator.go_to(2)
        assert self.elevator.stops[-1] == 2
        assert will_do_it is True

    def test_get_command(self):
        self.elevator.go_to(2)
        comm = self.elevator.get_command()

        assert comm.direction == 1
        assert comm.id == 1
        assert comm.speed == 1

    def test_process_buttons(self):
        buttons = [2, 3]
        self.elevator.process_buttons(buttons)
        assert self.elevator.stops == buttons

        new_buttons = [3, 4]
        self.elevator.process_buttons(new_buttons)
        assert self.elevator.stops == [2, 3, 4]

    def test_update_state_no_buttons(self):
        state = {
            'id': 1,
            'floor': 2
        }

        self.elevator.update_state(state)
        assert self.elevator.location == state['floor']

    def test_update_state_with_buttons(self):
        state = {
            'id': 1,
            'floor': 2,
            'buttons_pressed': [1, 2]
        }

        self.elevator.update_state(state)
        assert self.elevator.location == state['floor']
        assert self.elevator.stops == state['buttons_pressed']

    def test_update_state_with_more_buttons(self):
        self.elevator.process_buttons([1, 2])
        state = {
            'id': 1,
            'floor': 2,
            'buttons_pressed': [2, 3]
        }

        self.elevator.update_state(state)

        assert self.elevator.stops == [1, 2, 3]

    def test_update_state_with_high_dest(self):
        self.elevator.go_to(5)
        self.elevator.process_buttons([5, 6])

        assert_equals(self.elevator.stops, [5, 6])
        assert_equals(self.elevator.stops[-1], 6)

    def test_go_to_down(self):
        self.elevator.location = 5
        self.elevator.go_to(3)
        comm = self.elevator.get_command()
        assert comm.id == 1
        assert comm.direction == -1
        assert comm.speed == 1

    def test_will_not_go_to(self):
        """Should refuse to go to a floor beacuse it's out of the way"""
        self.elevator.location = 5
        self.elevator.process_buttons([9])
        self.elevator.get_command()
        assert self.elevator.go_to(4) is False
