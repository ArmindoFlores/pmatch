__all__ = ["NFA"]

from typing import Any, Sequence

import _pmatch


class NFA:
    """A Python object that represents a non-deterministic finite automaton"""
    def __init__(self, symbol: Any):
        self.__NFA = _pmatch.NFA(symbol)
        self.__symbol_type = type(symbol)
        self.__symbol_type_name = symbol.__class__.__name__

    def match(self, sequence: Sequence) -> int:
        """
        Tries to apply the pattern represented by the NFA to the start of the sequence.
        Returns the size of the match if one is found and -1 otherwise.
        """
        if len(sequence) > 0 and self.__symbol_type != type(sequence[0]):
            raise TypeError(f"Invalid type for matching operation: '{sequence[0].__class__.__name__}' (should be '{self.__symbol_type_name}')")
        return self.__NFA.match([symbol for symbol in sequence])

    def concatenate(self, nfa: "NFA") -> "NFA":
        """Concatenate self with the provided NFA."""
        if not isinstance(nfa, self.__class__):
            raise TypeError(f"Invalid argument: nfa must be of type '{self.__class__.__name__}' (was '{nfa.__class__.__name__}')")
        self.__NFA.concatenation(nfa.__NFA)
        return self

    def union(self, nfa: "NFA") -> "NFA":
        """Create a union with self and the provided NFA."""
        if not isinstance(nfa, self.__class__):
            raise TypeError(f"Invalid argument: nfa must be of type '{self.__class__.__name__}' (was '{nfa.__class__.__name__}')")
        self.__NFA.union(nfa.__NFA)
        return self

    def closure(self) -> "NFA":
        """Create a closure."""
        self.__NFA.closure()
        return self

    def semi_closure(self) -> "NFA":
        """Create a semi-closure. This is a made-up term that is supposed to represent the '+' operation from regex."""
        self.__NFA.semi_closure()
        return self

    def optional(self) -> "NFA":
        """Create an optional path. This is a made-up term that is supposed to represent the '?' operation from regex."""
        self.__NFA.optional()
        return self