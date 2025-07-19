from src.chatbot.chatbot import Chatbot

def main():
    print("Welcome to the Chatbot! Type 'exit' to quit.")
    chatbot = Chatbot()
    while True:
        query = input("Enter your query: ")
        if query.lower() == "exit":
            break
        response = chatbot.process_query(query)
        print(response)

if __name__ == "__main__":
    main()