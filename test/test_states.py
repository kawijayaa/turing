import unittest
import io
import sys
from turing import *


class StateTesting(unittest.TestCase):
    def setUp(self):
        self.alphabets = "abc"
        self.tm = TuringMachine(self.alphabets)

    def test_add_state(self):
        self.tm.add_state()

        self.assertEqual(self.tm._TuringMachine__states[0]._State__name, "q0")
        self.assertIs(
            self.tm._TuringMachine__states[0]._State__is_initial, False)
        self.assertIs(
            self.tm._TuringMachine__states[0]._State__is_final, False)
        self.assertIs(
            self.tm._TuringMachine__states[0]._State__lazy_deleted, False)

    def test_clear_tm(self):
        self.tm.clear()

        self.assertEqual(self.tm._TuringMachine__states, [])
        self.assertEqual(self.tm._TuringMachine__transitions, [])
        self.assertEqual(self.tm._TuringMachine__alphabets,
                         set(self.alphabets + "~"))
        self.assertEqual(self.tm._TuringMachine__head, None)
        self.assertEqual(self.tm._TuringMachine__state_lazy_deletion, [])
        self.assertIs(self.tm._TuringMachine__has_initial, False)

    def test_add_state_arguments(self):
        self.tm.clear()

        state = self.tm.add_state(True, True)

        self.assertEqual(
            self.tm._TuringMachine__states[0]._State__is_initial, True)
        self.assertEqual(
            self.tm._TuringMachine__states[0]._State__is_final, True)
        self.assertIs(self.tm._TuringMachine__head, state)
        self.assertIs(self.tm.initial_state, state)

    def test_multiple_initial(self):
        self.tm.clear()

        self.tm.add_state(False, True)

        with self.assertRaises(ValueError):
            self.tm.add_state(False, True)

    def test_delete_state(self):
        self.tm.clear()

        self.tm.add_state()
        self.tm.delete_state("q0")

        self.tm.clear()

        self.tm.add_state()
        self.tm.delete_state(0)

        q0 = self.tm.add_state()
        self.tm.delete_state(q0)

    def test_delete_state_with_lazy(self):
        self.tm.clear()

        self.tm.add_state()
        self.tm.delete_state("q0")

        with self.assertRaises(AttributeError):
            self.tm.delete_state("q0")

        self.tm.clear()

        self.tm.add_state()
        self.tm.delete_state(0)

        with self.assertRaises(AttributeError):
            self.tm.delete_state(0)

        q0 = self.tm.add_state()
        self.tm.delete_state(q0)

        with self.assertRaises(AttributeError):
            self.tm.delete_state(q0)

    def test_delete_state_exceptions(self):
        self.tm.clear()

        test_q = State("q69")

        with self.assertRaises(AttributeError):
            self.tm.delete_state("q1")

        with self.assertRaises(IndexError):
            self.tm.delete_state("q-1")

        with self.assertRaises(AttributeError):
            self.tm.delete_state(1)

        with self.assertRaises(IndexError):
            self.tm.delete_state(-1)

        with self.assertRaises(ValueError):
            self.tm.delete_state("asdf")

        with self.assertRaises(ValueError):
            self.tm.delete_state("1")

        with self.assertRaises(TypeError):
            self.tm.delete_state(self.tm)

        with self.assertRaises(TypeError):
            self.tm.delete_state([])

        with self.assertRaises(AttributeError):
            self.tm.delete_state(test_q)

    def test_initial_setter_getter(self):
        self.tm.clear()

        q0 = self.tm.add_state(False, True)
        q1 = self.tm.add_state()
        test_q = State("q69")

        self.tm.initial_state = q1
        self.assertEqual(self.tm.initial_state, q1)
        
        self.tm.initial_state = "q0"
        self.assertEqual(self.tm.initial_state, q0)

        self.tm.initial_state = 1
        self.assertEqual(self.tm.initial_state, q1)

        with self.assertRaises(ValueError):
            self.tm.initial_state = "asdf"
        with self.assertRaises(AttributeError):
            self.tm.initial_state = "q2"
        with self.assertRaises(IndexError):
            self.tm.initial_state = "q-2"

        with self.assertRaises(AttributeError):
            self.tm.initial_state = 2
        with self.assertRaises(IndexError):
            self.tm.initial_state = -2

        with self.assertRaises(AttributeError):
            self.tm.initial_state = test_q

        with self.assertRaises(TypeError):
            self.tm.initial_state = []

    # TODO: Fix this test using new state_names()
    # def test_states_representation(self):
    #     self.tm.clear()

    #     self.tm.add_state(False, True)
    #     self.tm.add_state()

    #     self.assertEqual(self.tm.states, ">q0, q1")

    #     self.tm.delete_state(0)

    #     self.assertEqual(self.tm.states, "q1")

    #     self.tm.clear()

    #     self.tm.add_state()
    #     self.tm.add_state(False, True)
    #     self.tm.add_state()
    #     self.tm.add_state(True)

    #     self.assertEqual(self.tm.states, "q0, >q1, q2, (q3)")

    #     self.tm.clear()

    #     self.tm.add_state(True)
    #     self.tm.add_state(True)
    #     self.tm.add_state()
    #     self.tm.add_state(True, True)

    #     self.assertEqual(self.tm.states, "(q0), (q1), q2, >(q3)")

    #     self.tm.clear()