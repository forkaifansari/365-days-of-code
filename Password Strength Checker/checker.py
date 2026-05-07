import re
import math

def check_length(password):
    if len(password) >= 12:
        return 2
    elif len(password) >= 8:
        return 1
    return 0

def check_patterns(password):
    score = 0
    if re.search(r'[A-Z]', password): score += 1
    if re.search(r'[a-z]', password): score += 1
    if re.search(r'[0-9]', password): score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): score += 1
    return score

def check_entropy(password):
    charset = 0
    if re.search(r'[A-Z]', password): charset += 26
    if re.search(r'[a-z]', password): charset += 26
    if re.search(r'[0-9]', password): charset += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password): charset += 32
    if charset == 0: return 0
    entropy = len(password) * math.log2(charset)
    if entropy >= 60: return 3
    elif entropy >= 40: return 2
    elif entropy >= 20: return 1
    return 0

COMMON = ["password", "123456", "qwerty", "abc123", "letmein",
          "monkey", "iloveyou", "admin", "welcome", "password1"]

def check_common(password):
    if password.lower() in COMMON:
        return -5
    return 0

def get_rating(score):
    if score <= 2:
        return "\033[91m[WEAK]\033[0m", "❌"
    elif score <= 5:
        return "\033[93m[MODERATE]\033[0m", "⚠️"
    elif score <= 8:
        return "\033[92m[STRONG]\033[0m", "✅"
    else:
        return "\033[96m[VERY STRONG]\033[0m", "🔐"

def get_suggestions(password):
    tips = []
    if len(password) < 12:
        tips.append("  → Use at least 12 characters")
    if not re.search(r'[A-Z]', password):
        tips.append("  → Add uppercase letters (A-Z)")
    if not re.search(r'[a-z]', password):
        tips.append("  → Add lowercase letters (a-z)")
    if not re.search(r'[0-9]', password):
        tips.append("  → Add numbers (0-9)")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        tips.append("  → Add special characters (!@#$...)")
    if password.lower() in COMMON:
        tips.append("  → This is a commonly used password — change it!")
    return tips

def analyze(password):
    score = (check_length(password) +
             check_patterns(password) +
             check_entropy(password) +
             check_common(password))

    rating, emoji = get_rating(score)
    suggestions = get_suggestions(password)

    print("\n" + "─" * 45)
    print(f"  Password : {'*' * len(password)}")
    print(f"  Length   : {len(password)} characters")
    print(f"  Score    : {max(score, 0)}/10")
    print(f"  Rating   : {rating} {emoji}")

    if suggestions:
        print("\n  \033[93mSuggestions to improve:\033[0m")
        for tip in suggestions:
            print(tip)
    else:
        print("\n  \033[92mYour password is solid. Nice work!\033[0m")
    print("─" * 45 + "\n")

def main():
    print("\n\033[96m  🔐 Password Strength Checker\033[0m")
    print("  \033[90mYour password is never stored or sent anywhere.\033[0m\n")
    while True:
        import getpass
        password = getpass.getpass("  Enter password (hidden): ")
        if not password:
            print("  \033[91mNo password entered. Exiting.\033[0m")
            break
        analyze(password)
        again = input("  Check another? (y/n): ").strip().lower()
        if again != 'y':
            print("\n  \033[90mStay secure. 👋\033[0m\n")
            break

if __name__ == "__main__":
    main()