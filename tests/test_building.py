from nose.tools import assert_equals  # , assert_true, assert_false
# from nose.plugins.skip import SkipTest
from building import Building, Request


class TestBuilding:
    """Test the Building class and its internal methods"""
    def setup(self):
        settings = {
            'bot_name': 'unittest',
            'email': 'unit@test.com',
            'registration_id': 'test_123'
        }
        self.building = Building('training_1', settings)

        state = {
            'elevators': [
                {
                    'id': 0,
                    'floor': 0
                },
                {
                    'id': 1,
                    'floor': 0
                }
            ]
        }

        self.building.build_elevators(state)

    def test_build_elevators(self):
        """Tests that we build all the elevator objects"""
        # This is testing that the setup method worked
        assert_equals(len(self.building.elevators), 2)

    def test_process_elevators(self):
        """Processes the new elevator states"""
        state = {
            'elevators': [
                {
                    'id': 0,
                    'floor': 2
                },
                {
                    'id': 1,
                    'floor': 4
                }
            ]
        }
        self.building.process_elevators(state)
        assert_equals(self.building.elevators[0].location, 2)
        assert_equals(self.building.elevators[1].location, 4)

    def test_process_requests(self):
        """Processes the new elevator requests"""
        state = {
            'requests': [
                {
                    "direction": -1,
                    "floor": 3
                }
            ]
        }

        self.building.process_requests(state)
        [e.get_command() for e in self.building.elevators]
        elevator = self.building.elevators[0]
        assert_equals(elevator.next_direction, -1)

        state = {
            'requests': [
                {
                    "direction": -1,
                    "floor": 3
                },
                {
                    "direction": 1,
                    "floor": 5
                }
            ]
        }

        self.building.process_requests(state)
        [e.get_command() for e in self.building.elevators]
        elevator1 = self.building.elevators[0]
        elevator2 = self.building.elevators[1]
        assert_equals(elevator1.cur_direction, 1)
        assert_equals(elevator1.next_direction, -1)
        assert_equals(elevator2.cur_direction, 1)
        assert_equals(elevator2.next_direction, 1)

    def test_add_acked(self):
        """Adds a request to the acked list"""
        state = {
            'requests': [
                {
                    "direction": -1,
                    "floor": 3
                }
            ]
        }
        self.building.process_requests(state)
        expected = Request(3, -1)
        assert_equals(expected, self.building.acked[0])

    def test_remove_acked(self):
        """Removes a finished request from the acked list"""
        state = {
            'requests': [
                {
                    "direction": -1,
                    "floor": 3
                }
            ]
        }
        self.building.process_requests(state)
        assert_equals(len(self.building.acked), 1)

        state = {
            'elevators': [
                {
                    'id': 0,
                    'floor': 3
                }
            ]
        }
        self.building.process_elevators(state)
        # import pdb; pdb.set_trace()
        self.building.generate_commands()
        assert_equals(len(self.building.acked), 0)
