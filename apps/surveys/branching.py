def condition_matches(condition: dict, answers: dict) -> bool:
    """Shared, code-based survey branching predicate for server-side validation/tests."""
    return all(answers.get(code) in allowed for code, allowed in condition.items())
