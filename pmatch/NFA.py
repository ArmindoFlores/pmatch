__all__ = ["NFA", "NFAContext"]

from typing import Iterable, Sequence, Type


class ordered_set:
    def __init__(self, iterable: Iterable=None):
        if iterable is None: iterable = ()
        self._dict = {i: 0 for i in iterable}

    def __repr__(self):
        return "{" + ", ".join([repr(key) for key in self._dict]) + "}"

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return (item for item in self._dict)

    def __getitem__(self, i):
        if i > len(self):
            raise IndexError("Index out of bounds")
        n = 0
        for k in self._dict:
            if n == i:
                return k
            n += 1
    
    def add(self, item):
        self._dict[item] = 0

    def update(self, other):
        if isinstance(other, self.__class__):
            self._dict.update(other._dict)
        elif isinstance(other, dict):
            self._dict.update(other)

    def copy(self):
        return self.__class__(self._dict)

class Node:
    def __init__(self, is_terminal):
        self._is_terminal = is_terminal
        self._transition = None
        self._epsilon_transitions = []

    @property
    def is_terminal(self):
        return self._is_terminal

    def set_terminal(self, is_terminal=True):
        self._is_terminal = is_terminal

    def add_epsilon_transition(self, to):
        assert self._transition is None
        assert len(self._epsilon_transitions) < 2
        self._epsilon_transitions.append(to)

    @property
    def epsilon_transitions(self):
        return self._epsilon_transitions

    @property
    def n_epsilon_transitions(self):
        return len(self._epsilon_transitions)

    @property
    def has_epsilon_transitions(self):
        return self.n_epsilon_transitions > 0

    def set_transition(self, symbol, to):
        assert not self.has_epsilon_transitions
        assert self._transition is None
        self._transition = (to, symbol)

    @property
    def transition(self):
        return self._transition

    @property
    def has_transition(self):
        return self._transition is not None


class NFAContext:
    def __init__(self):
        self.offset: int = 0
        self.visited_objs = ordered_set()
        self.visited = ordered_set()
        self.path = []
        self.cache = {}

    def add_path(self, path):
        self.path.append(path)

    def pop_path(self):
        return self.path.pop()

    @property
    def string_path(self):
        return "/".join(self.path)

    def copy(self):
        new_nfactx = self.__class__()
        new_nfactx.offset = self.offset
        new_nfactx.visited_objs = self.visited_objs.copy()
        new_nfactx.visited = self.visited.copy()
        new_nfactx.path = self.path[:]
        new_nfactx.cache = self.cache.copy()
        return new_nfactx


def get_next_states(state, states, visited, i):
    if state.has_epsilon_transitions:
        for transition in state.epsilon_transitions:
            if (transition, i) not in visited:
                visited.add((transition, i))
                get_next_states(transition, states, visited, i)
    else:
        states.add((state, i+1))

class NFA:
    def __init__(self, symbol=None):
        self._start = Node(False)
        self._end = Node(True)
        if symbol is not None:
            self._start.set_transition(symbol, self._end)
        else:
            self._start.add_epsilon_transition(self._end)

    def concatenate(self, other):
        self._end.set_terminal(False)
        self._end.add_epsilon_transition(other._start)
        self._end = other._end
        return self

    def union(self, other):
        new_start, new_end = Node(False), Node(True)
        self._end.set_terminal(False)
        other._end.set_terminal(False)
        new_start.add_epsilon_transition(self._start)
        new_start.add_epsilon_transition(other._start)
        self._end.add_epsilon_transition(new_end)
        other._end.add_epsilon_transition(new_end)
        self._start, self._end = new_start, new_end
        return self

    def closure(self):
        new_start, new_end = Node(False), Node(True)
        self._end.set_terminal(False)
        new_start.add_epsilon_transition(new_end)
        new_start.add_epsilon_transition(self._start)
        self._end.add_epsilon_transition(new_end)
        self._end.add_epsilon_transition(self._start)
        self._start, self._end = new_start, new_end
        return self
        
    def semi_closure(self):
        new_start, new_end = Node(False), Node(True)
        self._end.set_terminal(False)
        new_start.add_epsilon_transition(self._start)
        self._end.add_epsilon_transition(new_end)
        self._end.add_epsilon_transition(self._start)
        self._start, self._end = new_start, new_end
        return self

    def optional(self):
        new_start, new_end = Node(False), Node(True)
        self._end.set_terminal(False)
        new_start.add_epsilon_transition(new_end)
        new_start.add_epsilon_transition(self._start)
        self._end.add_epsilon_transition(new_end)
        self._start, self._end = new_start, new_end
        return self

    def match(self, sequence: Sequence, custom_context: Type[NFAContext]=NFAContext) -> int:
        return max(self._match(sequence, custom_context()))

    def _match(self, sequence: Sequence, ctx: NFAContext) -> ordered_set:
        can_call = True
        if ctx.visited_objs is not None and (self, ctx.offset) in ctx.visited_objs: 
            can_call = False
        ctx.visited_objs.add((self, ctx.offset))
        current_states = ordered_set()
        next_states = ordered_set()
        new_visited = ordered_set()
        matches = ordered_set([-1])

        get_next_states(self._start, current_states, ctx.visited, ctx.offset-1)

        running = True
        while running:
            next_states = ordered_set()
            running = False
            for state, i in current_states:
                if i >= len(sequence):
                    continue
                running = True
                if state.has_transition:
                    if state.transition[1] == sequence[i] and not isinstance(state.transition[1], self.__class__):
                        get_next_states(state.transition[0], next_states, ctx.visited, i)
                    elif isinstance(state.transition[1], self.__class__):
                        results = ordered_set()
                        if (state.transition[1], i) in ctx.cache:
                            results = ctx.cache[(state.transition[1], i)]
                        elif can_call:
                            new_context = ctx.copy()
                            new_context.visited = ordered_set()
                            new_context.offset = i
                            results = state.transition[1]._match(sequence, new_context)
                            new_context.cache[(state.transition[1], i)] = results
                            new_context.visited.update(ctx.visited)
                            ctx = new_context
                        for r in results:
                            if r >= 0:
                                get_next_states(state.transition[0], next_states, ctx.visited, r-1)

            current_states = next_states
            ctx.visited.update(new_visited)
            #new_visited = ctx.visited.copy()
            new_visited = ordered_set()
            for state, i in current_states:
                if state.is_terminal:
                    matches.add(i)
            if len(next_states) == 0:
                break

        return matches


# class NFA:
#     """A Python object that represents a non-deterministic finite automaton"""
#     def __init__(self, symbol: Any):
#         self.__NFA = _pmatch.NFA(symbol)
#         self.__symbol_type = type(symbol)
#         self.__symbol_type_name = symbol.__class__.__name__

#     def set_visited(self, visited):
#         self.__NFA.set_visited(visited)

#     def match(self, sequence: Sequence, offset: int=0, visited=None) -> int:
#         """
#         Tries to apply the pattern represented by the NFA to the start of the sequence.
#         Returns the size of the match if one is found and -1 otherwise.
#         """
#         if visited is None: visited = set()
#         self.__NFA.set_visited(visited)
#         # if len(sequence) > 0 and self.__symbol_type != type(sequence[0]):
#         #     raise TypeError(f"Invalid type for matching operation: '{sequence[0].__class__.__name__}' (should be '{self.__symbol_type_name}')")
#         return self.__NFA.match([symbol for symbol in sequence], offset)

#     def concatenate(self, nfa: "NFA") -> "NFA":
#         """Concatenate self with the provided NFA."""
#         if not isinstance(nfa, self.__class__):
#             raise TypeError(f"Invalid argument: nfa must be of type '{self.__class__.__name__}' (was '{nfa.__class__.__name__}')")
#         self.__NFA.concatenate(nfa.__NFA)
#         return self

#     def union(self, nfa: "NFA") -> "NFA":
#         """Create a union with self and the provided NFA."""
#         if not isinstance(nfa, self.__class__):
#             raise TypeError(f"Invalid argument: nfa must be of type '{self.__class__.__name__}' (was '{nfa.__class__.__name__}')")
#         self.__NFA.union(nfa.__NFA)
#         return self

#     def closure(self) -> "NFA":
#         """Create a closure."""
#         self.__NFA.closure()
#         return self

#     def semi_closure(self) -> "NFA":
#         """Create a semi-closure. This is a made-up term that is supposed to represent the '+' operation from regex."""
#         self.__NFA.semi_closure()
#         return self

#     def optional(self) -> "NFA":
#         """Create an optional path. This is a made-up term that is supposed to represent the '?' operation from regex."""
#         self.__NFA.optional()
#         return self
