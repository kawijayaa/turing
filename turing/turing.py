from __future__ import annotations
from typing import Literal, List, Set
from enum import Enum


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


class State:
    def __init__(self, name: str, is_final: bool = False, is_initial: bool = False):
        self.__name = name
        self.__is_final = is_final
        self.__is_initial = is_initial
        self.__lazy_deleted = False

    def __str__(self) -> str:
        name = self.__name

        if self.__is_final is True:
            name = f"({name})"
        if self.__is_initial is True:
            name = f">{name}"

        return name


class Transition:
    def __init__(
            self,
            name: str,
            read: str,
            write: str,
            move: Literal[Direction.LEFT, Direction.RIGHT, Direction.STAY],
            source_state: State,
            destination_state: State
    ):
        self.__name = name
        self.read = read
        self.write = write
        self.move = move
        self.source_state = source_state
        self.destination_state = destination_state


class TuringMachine:
    def __init__(self, alphabets: str | List[str] | Set[str]) -> None:
        self.__states: List[State] = []
        self.__transitions: List[Transition] = []
        self.__alphabets: Set[str] = set(alphabets)
        self.__head: State | None = None
        self.__state_lazy_deletion: List[State] = []
        self.__has_initial: bool = False

    def __generate_name(self) -> str:
        if len(self.__states) > 0:
            if self.__state_lazy_deletion == []:
                return f"q{len(self.__states)}"
            else:
                return f"q{self.__state_lazy_deletion.pop(0)}"
        else:
            return f"q0"

    def add_state(self, is_final: bool = False, is_initial: bool = False) -> State:
        if is_initial is True and self.__has_initial is True:
            raise ValueError(
                "This turing machine already have an initial state.")
        else:
            state_name = self.__generate_name()
            created_state = State(state_name, is_final, is_initial)

            self.__states.append(created_state)

            if is_initial is True:
                self.__head = created_state
                self.__has_initial = True

            return created_state

    def delete_state(self, state: str | int | State) -> State:
        if isinstance(state, str):
            if not state.startswith("q"):
                raise ValueError(
                    "State name must start with 'q' and followed by a number (e.g. q0).")

            state_index = int(state[1:])
            if state_index < 0:
                raise IndexError("State index must be larger than 0.")
            if state_index > len(self.__states) - 1:
                raise AttributeError("State not found.")

            deleted_state = self.__states[state_index]

            if deleted_state._State__lazy_deleted is True:
                raise AttributeError("State not found.")
        elif isinstance(state, int):
            if state < 0:
                raise IndexError("State index must be larger than 0.")
            if state > len(self.__states) - 1:
                raise AttributeError("State not found.")

            deleted_state = self.__states[state]

            if deleted_state._State__lazy_deleted is True:
                raise AttributeError("State not found.")
        elif isinstance(state, State):
            if state not in self.__states or state._State__lazy_deleted is True:
                raise AttributeError("State not found.")

            deleted_state = state
        else:
            raise TypeError(
                "Argument must be a string, an integer or a State object.")

        deleted_state._State__lazy_deleted = True
        self.__state_lazy_deletion.append(deleted_state._State__name)

        return deleted_state

    @property
    def initial_state(self) -> State:
        return self.__head

    @initial_state.setter
    def initial_state(self, value: any) -> None:
        if isinstance(value, str):
            if not value.startswith("q"):
                raise ValueError(
                    "State name must start with 'q' and followed by a number (e.g. q0).")

            state_index = int(value[1:])
            if state_index > len(self.__states) - 1:
                raise AttributeError("State not found.")
            if state_index < 0:
                raise IndexError("State index must be larger than 0.")

            target_state = self.__states[state_index]
        elif isinstance(value, int):
            if value > len(self.__states) - 1:
                raise AttributeError("State not found.")
            if value < 0:
                raise IndexError("State index must be larger than 0.")

            target_state = self.__states[value]
        elif isinstance(value, State):
            if value not in self.__states or value._State__lazy_deleted is True:
                raise AttributeError("State not found.")

            target_state = value
        else:
            raise TypeError(f"Cannot assign type {
                            type(value)} as initial state.")

        if self.__head is not None:
            self.__head._State__is_initial = False
        self.__head = target_state
        self.__head._State__is_initial = True

    def clear(self) -> None:
        self.__init__(self.__alphabets)

    def __str__(self) -> str:
        return ", ".join([str(state) for state in self.__states if state._State__lazy_deleted is False])
