from orchestrator import run_task


def main():
    user_input = "add 5 and six, turn the result into uppercase letters, then tell me how's the weather in London, in celsius and fahrenheit."

    result = run_task(user_input)

    print("FINAL OUTPUT:")
    print(result["final_output"])

    print("\nTRACE:")
    for step in result["trace"]:
        print(step)


if __name__ == "__main__":
    main()
