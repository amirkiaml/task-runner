def run_text_processor(text: str, operation: str) -> str:
    if operation == "uppercase": return text.upper()
    if operation == "lowercase": return text.lower()
    if operation == "word_count": return str(len(text.split()))
    return f"Error: unknown operation '{operation}'."

def run_calculator(num1: float, num2: float, operation: str) -> str:
    if operation == "addition": return str(num1 + num2)
    if operation == "subtraction": return str(num1 - num2)
    if operation == "multiplication": return str(num1 * num2)
    if operation == "division":
        if num2 == 0: return "Error: division by zero."
        return str(num1 / num2)
    return f"Error: unknown operation '{operation}'."

def run_weather_mock(city: str) -> str:
    mock_data = {"toronto": "18°C, partly cloudy", "new york": "22°C, sunny", "london": "14°C, rainy"}
    condition = mock_data.get(city.strip().lower(), "20°C, clear (default mock data)")
    return f"[MOCK] Weather in {city}: {condition}"

def run_unit_converter(value: float, from_unit: str, to_unit: str) -> str:
    conversions = {
        ("km", "miles"): lambda v: v * 0.621371,
        ("miles", "km"): lambda v: v / 0.621371,
        ("celsius", "fahrenheit"): lambda v: v * 9/5 + 32,
        ("fahrenheit", "celsius"): lambda v: (v - 32) * 5/9,
        ("kg", "lbs"): lambda v: v * 2.20462,
        ("lbs", "kg"): lambda v: v / 2.20462,
    }
    key = (from_unit.strip().lower(), to_unit.strip().lower())
    if key not in conversions:
        return f"Error: no conversion available from {from_unit} to {to_unit}."
    return f"{conversions[key](value):.2f} {to_unit}"
