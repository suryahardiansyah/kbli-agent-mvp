from classifier import classify_query, format_for_chat

print("=== KBLI Agent CLI Chat ===")
while True:
    query = input("\nAnda: ")
    if query.lower() in ["exit", "quit"]:
        break
    result = classify_query(query)
    print("\nAgent:\n")
    print(format_for_chat(result))
