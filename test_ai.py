from ai import ask_ai

while True:
    question = input("You: ")

    if question.lower() == "exit":
        break

    print("\nECHO X:", ask_ai(question))
    print()