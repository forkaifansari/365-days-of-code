import requests
import random

def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random")
        data = response.json()
        quote = data[0]['q']
        author = data[0]['a']
        return quote, author
    except:
        # fallback quotes if API fails
        quotes = [
            ("Code is like humor. When you have to explain it, it's bad.", "Cory House"),
            ("First, solve the problem. Then, write the code.", "John Johnson"),
            ("Experience is the name everyone gives to their mistakes.", "Oscar Wilde"),
            ("The best way to predict the future is to invent it.", "Alan Kay"),
        ]
        return random.choice(quotes)

def print_quote(quote, author):
    width = 60
    print("\n" + "─" * width)
    print(f"\033[96m  \"{quote}\"\033[0m")
    print(f"\033[93m  — {author}\033[0m")
    print("─" * width + "\n")

def main():
    print("\033[92m  fetching your daily quote...\033[0m")
    quote, author = get_quote()
    print_quote(quote, author)

if __name__ == "__main__":
    main()