"""
Deterministic task router. Parses the user's input with keyword/pattern
matching and routes each part to a tool - no LLM, no external API calls.
Satisfies "agent selects and executes predefined tools" purely in code.
"""
import re


_WORD_TO_NUM = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18",
    "nineteen": "19", "twenty": "20",
}


def _spell_out_numbers(text: str) -> str:
    """Replaces spelled-out small numbers ('six') with digits ('6') so the
    calculator/converter matchers, which look for digits, can find them."""
    def replace(match):
        return _WORD_TO_NUM[match.group(0).lower()]
    pattern = r"\b(" + "|".join(_WORD_TO_NUM.keys()) + r")\b"
    return re.sub(pattern, replace, text, flags=re.IGNORECASE)


def _match_calculator(clause: str):
    clause = _spell_out_numbers(clause)
    clause_l = clause.lower()
    op_words = {
        "add": "addition", "plus": "addition", "+": "addition", "sum of": "addition",
        "subtract": "subtraction", "minus": "subtraction", "-": "subtraction",
        "multiply": "multiplication", "times": "multiplication", "*": "multiplication",
        "divide": "division", "divided": "division", "/": "division",
    }
    numbers = re.findall(r"-?\d+\.?\d*", clause)
    if len(numbers) >= 2:
        for word, op in op_words.items():
            if word in clause_l:
                return {"tool": "CalculatorTool", "num1": float(numbers[0]),
                        "num2": float(numbers[1]), "operation": op}
    return None


def _match_unit_converter(clause: str):
    clause_l = clause.lower()
    unit_map = {"kilometers": "km", "kilogram": "kg", "kilograms": "kg", "pounds": "lbs"}
    known = ["celsius", "fahrenheit", "km", "kilometers", "miles",
             "kg", "kilogram", "kilograms", "lbs", "pounds"]
    # Order matters: find each unit's position in the actual clause so
    # "from X to Y" is preserved correctly, not the order they happen to
    # appear in the `known` reference list.
    positions = []
    for u in known:
        m = re.search(rf"\b{u}\b", clause_l)
        if m:
            positions.append((m.start(), u))
    positions.sort()
    found = [u for _, u in positions]

    numbers = re.findall(r"-?\d+\.?\d*", clause)
    if len(found) >= 2 and numbers:
        from_unit = unit_map.get(found[0], found[0])
        to_unit = unit_map.get(found[1], found[1])
        return {"tool": "UnitConvertor", "value": float(numbers[0]),
                "from_unit": from_unit, "to_unit": to_unit}
    return None


def _match_weather(clause: str):
    clause_l = clause.lower()
    if "weather" in clause_l:
        match = re.search(r"weather.*?\bin\s+([a-zA-Z\s]+?)(?:$|[.,?!])", clause_l)
        city = match.group(1).strip().title() if match else "Unknown"
        return {"tool": "WeatherMockTool", "city": city}
    return None


def _match_text_processor(clause: str):
    clause_l = clause.lower()
    quoted = re.search(r'"([^"]+)"', clause)
    if "uppercase" in clause_l:
        op = "uppercase"
    elif "lowercase" in clause_l:
        op = "lowercase"
    elif "word count" in clause_l or "count the words" in clause_l:
        op = "word_count"
    else:
        return None
    # If no quoted text is present, this likely refers to a prior step's
    # result (e.g. "turn the result into uppercase") - resolved by the
    # caller, which has access to prior outputs. `text=None` signals that.
    return {"tool": "TextProcessorTool", "text": quoted.group(1) if quoted else None, "operation": op}


def parse_task(user_input: str) -> list[dict]:
    """Splits input into clauses on simple, transparent delimiters and
    matches each against known tool patterns, in order. Unmatched clauses
    are flagged, not guessed at - no fabricated answers, since there's no
    model here to generate one."""
    clauses = re.split(r"\band then\b|,?\s*\bthen\b|\.\s+|,\s*|\n+", user_input, flags=re.IGNORECASE)
    clauses = [c.strip() for c in clauses if c.strip()]

    matched = []
    for clause in clauses:
        result = (
            _match_calculator(clause)
            or _match_unit_converter(clause)
            or _match_weather(clause)
            or _match_text_processor(clause)
        )
        matched.append(result if result else {"tool": "none", "clause": clause})
    return matched
