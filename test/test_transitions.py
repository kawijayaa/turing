import unittest
from turing import *


class TransitionTesting(unittest.TestCase):
    def setUp(self):
        self.alphabets = "abc"
        self.tm = TuringMachine(self.alphabets)

    def test_transition_init(self):
        q0 = self.tm.add_state()
        q1 = self.tm.add_state(False, True)

        t0 = Transition("t0", "a", "b", Direction.LEFT, q0, q1)

    # TODO: Add more tests for transition