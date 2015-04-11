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
        self.building.floors = 10

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
            ],
            'floors': 10
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
            ],
            'floors': 10
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
            ],
            'floors': 10
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
            ],
            'floors': 10
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
            ],
            'floors': 10
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
        self.building.generate_commands()
        assert_equals(len(self.building.acked), 0)

    def test_find_cheapest_elevator_equal(self):
        request = Request(floor=9, direction=-1)
        result = self.building.find_cheapest_elevator(request, 10)
        assert_equals(result, self.building.elevators[0])

    def test_find_cheapest_elevator_closer(self):
        state = {'elevators': [{'id': 1, 'floor': 5}], 'floors': 10}
        self.building.process_elevators(state)

        request = Request(floor=9, direction=-1)
        result = self.building.find_cheapest_elevator(request, 10)
        assert_equals(result, self.building.elevators[1])

    def test_manage_idle_elevators(self):
        self.building.elevators[0].wait_count = 2
        self.building.elevators[1].wait_count = 2
        commands = self.building.generate_commands()
        self.building.manage_idle_elevators(commands)
        for command in commands:
            assert_equals(command.direction, 1)
            assert_equals(command.speed, 1)

        state = {'requests': [{'floor': 5, 'direction': -1}]}
        self.building.process_requests(state)
        commands = self.building.generate_commands()
        for command in commands:
            assert_equals(command.direction, 1)
            assert_equals(command.speed, 1)

    def test_manage_idle_elevators_more(self):
        state = {'elevators': [{'id': 0, 'floor': 6}]}
        self.building.process_elevators(state)
        self.building.elevators[0].wait_count = 2
        self.building.elevators[1].wait_count = 2
        state = {'requests': [{'floor': 5, 'direction': -1}]}
        self.building.process_requests(state)
        commands = self.building.generate_commands()
        assert_equals(commands[0].direction, -1)
        assert_equals(commands[0].speed, 1)
        assert_equals(commands[1].direction, 1)
        assert_equals(commands[1].speed, 1)
