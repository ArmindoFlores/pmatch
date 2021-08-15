__all__ = ["_compile"]

from .NFA import NFA


class DictWrapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

def _get_error_string(pattern, col, size=1):
    return f"""
Column {col} of pattern:
\t{pattern}
\t{' '*(col-size+1)}{'~'*(size-1)}^
"""

def _get_group(stack, group):
    p = stack
    for _ in range(group):
        p = p["objects"][-1]
    return p

def _process_word(word, pattern, stack, col, group, is_or, variables):
    if len(word) > 0:
        should_raise = False
        try:
            obj = eval(word, {vname: v for vname, v in variables.items()})
        except Exception:
            should_raise = True
        if should_raise:
            raise RuntimeError(_get_error_string(pattern, col, len(word)) + f"Unkown object: {word}")
        _get_group(stack, group)["objects"].append(obj)
        if is_or == group and is_or != 0:
            group -= 1
            is_or = 0
    return group, is_or

def _produce_stack(pattern: str, variables: dict):
    stack = DictWrapper({"objects": [], "flags": set()})
    group = 0
    escaped = False
    col = 0
    word = ""
    is_or = 0
    for char in pattern:
        if char == "(" and not escaped:
            group, is_or = _process_word(word, pattern, stack, col-1, group, is_or, variables)
            word = ""
            _get_group(stack, group)["objects"].append(DictWrapper({"objects": [], "flags": set()}))
            group += 1
        elif char == ")" and not escaped:
            if group-1 < 0:
                raise SystemError(_get_error_string(pattern, col) + "Extra '('. Did you forget a '('?")
            group, is_or = _process_word(word, pattern, stack, col-1, group, is_or, variables)
            group -= 1
            word = ""
        elif char == "?" and not escaped:
            group, is_or = _process_word(word, pattern, stack, col-1, group, is_or, variables)
            word = ""
            _get_group(stack, group)["flags"].add("optional")
        elif char == "*" and not escaped:
            group, is_or = _process_word(word, pattern, stack, col-1, group, is_or, variables)
            word = ""
            _get_group(stack, group)["flags"].add("any")
        elif char == "+" and not escaped:
            group, is_or = _process_word(word, pattern, stack, col-1, group, is_or, variables)
            word = ""
            _get_group(stack, group)["flags"].add("some")
        elif char == "|" and not escaped:
            group, is_or = _process_word(word, pattern, stack, col-1, group, is_or, variables)
            word = ""
            g = _get_group(stack, group)
            if len(g["objects"]) > 0:
                objects, flags = g["objects"], g["flags"]
                g["objects"] = [DictWrapper({"objects": [DictWrapper({"objects": objects, "flags": flags})], "flags": {"or"}})]
                g["flags"] = set()
                group += 1
                is_or = group
            else:
                SyntaxError(_get_error_string(pattern, col) + f"No left operand for '|'.")
        elif char == " " and not escaped:
            group, is_or = _process_word(word, pattern, stack, col-1, group, is_or, variables)
            word = ""
        elif char != "\\":
            word += char
        if char == "\\" and not escaped:
            escaped = True
        else:
            escaped = False
        col += 1

    group, is_or = _process_word(word, pattern, stack, col, group, is_or, variables)
    if group == is_or and is_or != 0:
        group -= 1
    if group != 0:
        raise SystemError(_get_error_string(pattern, col) + "Missing ')'.")
    return stack

def _inspect_stack(stack, nfa):
    results = []
    for obj in stack["objects"]:
        if not isinstance(obj, DictWrapper):
            results.append(nfa(obj))
        else:
            results.append(_inspect_stack(obj))
    if len(results) > 0:
        expr = results[0]
        if not "or" in stack["flags"]:
            for result in results[1:]:
                expr.concatenate(result)
            if "optional" in stack["flags"]:
                expr.optional()
            elif "some" in stack["flags"]:
                expr.semi_closure()
            elif "any" in stack["flags"]:
                expr.closure()
        else:
            expr.union(results[1])
        return expr

def _compile(pattern: str, variables: dict, nfa=NFA):
    stack = _produce_stack(pattern, variables)
    return _inspect_stack(stack, nfa)