"""
Ties the deterministic router (router.py) to the actual tool implementations
(tools.py) and builds the numbered execution trace. No AI/LLM involved -
this whole module is plain, deterministic Python.
"""
from router import parse_task
from tools import run_text_processor, run_calculator, run_weather_mock, run_unit_converter


def run_task(user_input: str) -> dict:
    steps = parse_task(user_input)

    trace = [f'Step 1: Received input "{user_input}"']
    n = 2
    final_parts = []
    tools_used = []
    prev_output = None

    for step in steps:
        tool = step["tool"]

        if tool == "none":
            trace.append(f"Step {n}: No matching tool for: \"{step['clause']}\"")
            n += 1
            continue

        trace.append(f"Step {n}: Selected tool: {tool}")
        n += 1

        if tool == "CalculatorTool":
            output = run_calculator(step["num1"], step["num2"], step["operation"])
        elif tool == "TextProcessorTool":
            # If no quoted text was found, this step refers to the previous
            # step's result (e.g. "turn the result into uppercase").
            text = step["text"] if step["text"] is not None else (
                str(prev_output) if prev_output is not None else ""
            )
            output = run_text_processor(text, step["operation"])
        elif tool == "WeatherMockTool":
            output = run_weather_mock(step["city"])
        elif tool == "UnitConvertor":
            output = run_unit_converter(step["value"], step["from_unit"], step["to_unit"])
        else:
            output = f"Error: unrecognized tool '{tool}'."

        trace.append(f"Step {n}: Tool result: {output}")
        n += 1
        tools_used.append(tool)
        final_parts.append(str(output))
        prev_output = output

    trace.append(f"Step {n}: Returning result to user")
    if len(final_parts) > 1:
        final_output = "\n".join(f"• {part}" for part in final_parts)
    elif final_parts:
        final_output = final_parts[0]
    else:
        final_output = "No applicable tool was used for this request."

    return {"final_output": final_output, "trace": trace, "tools_used": tools_used}
