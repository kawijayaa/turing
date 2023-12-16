from __future__ import annotations
from typing import Any, Literal, List, Set
from enum import Enum
import re


class Direction(Enum):
    LEFT = "L"
    RIGHT = "R"
    STAY = "S"


class Status(Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    UNDEFINED = "UNDEFINED"


class GrowingList(list):
    def __init__(self, default_value: str):
        self.default_value: str = default_value

    def __getitem__(self, i: int) -> Any | str:
        return list.__getitem__(self, i) if i < len(self) else self.default_value

    def __setitem__(self, i: int, v: str) -> None:
        if i >= len(self):
            self.extend([self.default_value]*(i + 1 - len(self)))
        list.__setitem__(self, i, v)


class Tape:
    def __init__(self, empty_alphabet: str):
        self.positive_list = GrowingList(empty_alphabet)
        self.negative_list = GrowingList(empty_alphabet)
        self.__pointer = 0

    def __getitem__(self, i: int) -> str:
        if isinstance(i, int):
            if i >= 0:
                return self.positive_list[i]
            else:
                return self.negative_list[-i-1]

    def __setitem__(self, i: int, v: str) -> Any | str:
        if i >= 0:
            self.positive_list[i] = v
        else:
            self.negative_list[-i-1] = v

    def peek(self) -> str:
        return self[self.__pointer]

    def move(self, direction: Direction) -> None:
        if direction == Direction.LEFT:
            if self.__pointer - 1 < -len(self.negative_list):
                self.negative_list.append(self.negative_list.default_value)
            self.__pointer -= 1
        elif direction == Direction.RIGHT:
            if self.__pointer + 1 >= len(self.positive_list):
                self.positive_list.append(self.positive_list.default_value)
            self.__pointer += 1
        elif direction == Direction.STAY:
            pass
        else:
            raise ValueError("Invalid direction")

    def __repr__(self) -> str:
        data = list(reversed(self.negative_list)) + self.positive_list
        tape_string = "".join(f"[{char}]" for char in data)
        index_legend = ""

        if len(self.negative_list) == 0:
            index_legend = "0" + \
                f"{len(self.positive_list) - 1}".rjust(len(tape_string) - 1)

            if self.__pointer > len(self.positive_list) - 1:
                index_legend = index_legend[:-1] + \
                    f"{self.__pointer - len(self.positive_list) + 1}"
        else:
            index_legend = f"-{len(self.negative_list) - 1}" + \
                "0".rjust(len(self.negative_list)*3)

            index_legend += f"{len(self.positive_list) - 1}".rjust(
                len(tape_string) - len(index_legend))

        return index_legend + "\n" + tape_string + "\n" + "^".rjust(((self.__pointer + len(self.negative_list)) * 3) + 2)


class State:
    def __init__(self, name: str, is_final: bool = False, is_initial: bool = False):
        self.__name: str = name
        self.__is_final: bool = is_final
        self.__is_initial: bool = is_initial
        self.__lazy_deleted: bool = False
        self.__transitions: List[Transition] = []

    def __str__(self) -> str:
        name = self.__name

        if self.__is_final is True:
            name = f"({name})"
        if self.__is_initial is True:
            name = f">{name}"

        return name

    def isActive(self) -> bool:
        return not self.__lazy_deleted


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
        self.__name: str = name
        self.read: str = read
        self.write: str = write
        self.move: Literal[Direction.LEFT,
                           Direction.RIGHT, Direction.STAY] = move
        self.source_state: State = source_state
        self.destination_state: State = destination_state
        self.__lazy_deleted: bool = False

    def isActive(self) -> bool:
        return self.__lazy_deleted

    def __str__(self) -> str:
        return f"{self.__name}: {self.source_state}({self.read} | {self.write} | {self.move.value}) --> {self.destination_state}"


class TuringMachine:
    def __init__(self, alphabets: str | List[str] | Set[str], empty_alphabet: str = "~") -> None:
        self.__states: List[State] = []
        self.__transitions: List[Transition] = []

        if isinstance(alphabets, str) or isinstance(alphabets, list) or isinstance(alphabets, set):
            self.__alphabets: Set[str] = set(alphabets)
        else:
            raise TypeError

        self.__head: State | None = None
        self.__state_lazy_deletion: List[State] = []
        self.__transition_lazy_deletion: List[Transition] = []
        self.__has_initial: bool = False

        if not isinstance(empty_alphabet, str):
            raise ValueError

        self.__alphabets.add(empty_alphabet)
        self.__empty_alphabet = empty_alphabet

    def __generate_state_name(self) -> str:
        if len(self.__states) > 0:
            if self.__state_lazy_deletion == []:
                return f"q{len(self.__states)}"
            else:
                return f"q{self.__state_lazy_deletion.pop(0)}"
        else:
            return f"q0"

    def __generate_transition_name(self) -> str:
        if len(self.__transitions) > 0:
            if self.__transition_lazy_deletion == []:
                return f"t{len(self.__transitions)}"
            else:
                return f"t{self.__transition_lazy_deletion.pop(0)}"
        else:
            return f"t0"

    def get_state(self, state: str | int) -> State:
        if isinstance(state, str):
            if not state.startswith("q"):
                raise ValueError(
                    "State name must start with 'q' and followed by a number (e.g. q0).")

            state_index = int(state[1:])
            if state_index < 0:
                raise IndexError("State index must be larger than 0.")
            if state_index > len(self.__states) - 1:
                raise AttributeError("State not found.")

            target_state = self.__states[state_index]

            if target_state._State__lazy_deleted is True:
                raise AttributeError("State not found.")
        elif isinstance(state, int):
            if state < 0:
                raise IndexError("State index must be larger than 0.")
            if state > len(self.__states) - 1:
                raise AttributeError("State not found.")

            target_state = self.__states[state]

            if target_state._State__lazy_deleted is True:
                raise AttributeError("State not found.")

        return target_state
    
    def get_transition(self, transition: str | int) -> Transition:
        if isinstance(transition, str):
            if not transition.startswith("q"):
                raise ValueError(
                    "Transition name must start with 't' and followed by a number (e.g. t0).")

            transition_index = int(transition[1:])
            if transition_index < 0:
                raise IndexError("Transition index must be larger than 0.")
            if transition_index > len(self.__transitions) - 1:
                raise AttributeError("Transition not found.")

            target_transition = self.__transitions[transition_index]

            if target_transition._Transition__lazy_deleted is True:
                raise AttributeError("Transition not found.")
        elif isinstance(transition, int):
            if transition < 0:
                raise IndexError("Transition index must be larger than 0.")
            if transition > len(self.__transitions) - 1:
                raise AttributeError("Transition not found.")

            target_transition = self.__transitions[transition]

            if target_transition._Transition__lazy_deleted is True:
                raise AttributeError("Transition not found.")

        return target_transition

    def add_state(self, is_final: bool = False, is_initial: bool = False) -> State:
        if is_initial is True and self.__has_initial is True:
            raise ValueError(
                "This turing machine already have an initial state.")
        else:
            state_name = self.__generate_state_name()
            created_state = State(state_name, is_final, is_initial)

            self.__states.append(created_state)

            if is_initial is True:
                self.__head = created_state
                self.__has_initial = True

            return created_state

    def delete_state(self, state: str | int | State) -> State:
        if isinstance(state, str) or isinstance(state, int):
            deleted_state = self.get_state(state)
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
        if isinstance(value, str) or isinstance(value, int):
            target_state = self.get_state(value)
        elif isinstance(value, State):
            if value not in self.__states or value._State__lazy_deleted is True:
                raise AttributeError("State not found.")

            target_state = value
        else:
            raise TypeError(
                f"Cannot assign type {type(value)} as initial state.")

        if self.__head is not None:
            self.__head._State__is_initial = False
        self.__head = target_state
        self.__head._State__is_initial = True

    def add_transition(
        self,
        source_state: str | int | State,
        destination_state: str | int | State,
        read: str = None,
        write: str = None,
        move: Literal[Direction.LEFT, Direction.RIGHT,
                      Direction.STAY] = Direction.RIGHT,
    ) -> Transition:
        if read is None:
            read = self.__empty_alphabet
        elif read not in self.__alphabets:
            raise ValueError

        if write is None:
            write = self.__empty_alphabet
        elif write not in self.__alphabets:
            raise ValueError

        if not isinstance(source_state, State) and (isinstance(source_state, str) or isinstance(source_state, int)):
            source_state = self.get_state(source_state)
        elif isinstance(source_state, State):
            pass
        else:
            raise TypeError

        if not isinstance(destination_state, State) and (isinstance(destination_state, str) or isinstance(destination_state, int)):
            destination_state = self.get_state(destination_state)
        elif isinstance(destination_state, State):
            pass
        else:
            raise TypeError

        if not isinstance(move, Direction):
            raise TypeError

        new_transition = Transition(self.__generate_transition_name(
        ), read, write, move, source_state, destination_state)

        source_state._State__transitions.append(new_transition)
        self.__transitions.append(new_transition)

        return new_transition
    
    def delete_transition(self, transition: str | int | Transition) -> Transition:
        if isinstance(transition, str) or isinstance(transition, int):
            deleted_transition = self.get_transition(transition)
        elif isinstance(transition, transition):
            if transition not in self.__transitions or transition._Transition__lazy_deleted is True:
                raise AttributeError("Transition not found.")

            deleted_transition = transition
        else:
            raise TypeError(
                "Argument must be a string, an integer or a Transition object.")

        deleted_transition._Transition__lazy_deleted = True
        self.__transition_lazy_deletion.append(deleted_transition._Transition__name)

        return deleted_transition

    def clear(self) -> None:
        self.__init__(self.__alphabets)

    def display(self) -> None:
        for state in self.__states:
            if state not in self.__state_lazy_deletion:
                print(state)
                for transition in state._State__transitions:
                    if transition not in self.__transition_lazy_deletion:
                        print(f"  {transition}")

    def display_states(self) -> None:
        print(", ".join([str(state) for state in self.__states if state._State__lazy_deleted is False]))

    @property
    def state_names(self) -> str:
        return [state._State__name for state in self.__states if state._State__lazy_deleted is False]
    
    @property
    def transition_names(self) -> str:
        return [transition._Transition__name for transition in self.__transitions if transition._Transition__lazy_deleted is False]
