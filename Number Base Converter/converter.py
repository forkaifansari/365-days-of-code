import sys
import math

# ANSI colors
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
C = "\033[96m"
R = "\033[91m"
W = "\033[97m"
M = "\033[95m"
DIM = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def validate(number, base):
    valid = DIGITS[:base]
    for ch in number.upper():
        if ch not in valid:
            return False
    return True

def to_decimal(number, base):
    number = number.upper()
    result = 0
    for i, ch in enumerate(reversed(number)):
        result += DIGITS.index(ch) * (base ** i)
    return result

def from_decimal(decimal, base):
    if decimal == 0:
        return "0"
    result = ""
    while decimal > 0:
        result = DIGITS[decimal % base] + result
        decimal //= base
    return result

def explain_to_decimal(number, base):
    number = number.upper()
    print(f"\n  {BOLD}{W}📖 Step-by-step: {number} (base {base}) → Decimal{RESET}\n")
    print(f"  {DIM}Formula: each digit × base^position (right to left, starting at 0){RESET}\n")

    total = 0
    steps = []
    for i, ch in enumerate(reversed(number)):
        val = DIGITS.index(ch)
        power = base ** i
        contribution = val * power
        total += contribution
        steps.append((ch, val, base, i, power, contribution))

    for ch, val, b, pos, power, contrib in reversed(steps):
        print(f"  {C}{ch}{RESET} × {Y}{b}^{pos}{RESET} = "
              f"{C}{val}{RESET} × {Y}{power}{RESET} = {G}{contrib}{RESET}")

    print(f"\n  {DIM}Sum: {RESET}" +
          " + ".join(f"{G}{s[5]}{RESET}" for s in reversed(steps)))
    print(f"  {BOLD}{W}Result: {G}{total}{RESET}\n")
    return total

def explain_from_decimal(decimal, base):
    print(f"\n  {BOLD}{W}📖 Step-by-step: {decimal} (Decimal) → Base {base}{RESET}\n")
    print(f"  {DIM}Formula: repeatedly divide by {base}, remainders give digits (bottom to top){RESET}\n")

    remainders = []
    n = decimal
    while n > 0:
        q, r = divmod(n, base)
        print(f"  {W}{n}{RESET} ÷ {Y}{base}{RESET} = "
              f"{C}{q}{RESET} remainder {G}{DIGITS[r]}{RESET}")
        remainders.append(DIGITS[r])
        n = q

    result = ''.join(reversed(remainders)) if remainders else "0"
    print(f"\n  {DIM}Read remainders bottom to top:{RESET} "
          + " ← ".join(f"{G}{r}{RESET}" for r in remainders))
    print(f"  {BOLD}{W}Result: {G}{result}{RESET}\n")
    return result

def convert_all(number, from_base):
    decimal = to_decimal(number, from_base)
    results = {
        2:   from_decimal(decimal, 2),
        8:   from_decimal(decimal, 8),
        10:  str(decimal),
        16:  from_decimal(decimal, 16),
    }
    return results, decimal

def print_all(number, from_base, results):
    base_names = {2: "Binary", 8: "Octal", 10: "Decimal", 16: "Hexadecimal"}
    base_colors = {2: C, 8: Y, 10: G, 16: M}

    print(f"\n  {BOLD}{W}🔄 Conversion Results{RESET}")
    print(f"  {DIM}{'─' * 45}{RESET}")
    print(f"  {DIM}Input: {RESET}{W}{number.upper()}{RESET} "
          f"{DIM}(Base {from_base} · {base_names.get(from_base, f'Base {from_base}')}){RESET}\n")

    for base, result in results.items():
        active = "◀ input" if base == from_base else ""
        color = base_colors.get(base, W)
        prefix = {2: "0b", 8: "0o", 16: "0x"}.get(base, "")
        print(f"  {DIM}Base {base:2d} ({base_names.get(base, f'Base {base}'):<13}){RESET}  "
              f"{color}{BOLD}{prefix}{result}{RESET}  {DIM}{active}{RESET}")

    print(f"  {DIM}{'─' * 45}{RESET}\n")

def interactive_mode():
    print(f"\n  {C}{BOLD}🔢 Number Base Converter{RESET}")
    print(f"  {DIM}Convert between Binary, Octal, Decimal, Hex & more{RESET}")
    print(f"  {DIM}Type 'quit' to exit · Type 'help' for commands{RESET}\n")

    while True:
        try:
            inp = input(f"  {G}>{RESET} ").strip()
        except KeyboardInterrupt:
            print(f"\n\n  {DIM}Bye! 👋{RESET}\n")
            break

        if not inp:
            continue

        if inp.lower() == 'quit':
            print(f"\n  {DIM}Bye! Keep building. 👋{RESET}\n")
            break

        if inp.lower() == 'help':
            print(f"""
  {BOLD}{W}Commands:{RESET}
  {G}<number> <from_base>{RESET}              convert to all bases
  {G}<number> <from_base> <to_base>{RESET}    convert to specific base
  {G}<number> <from_base> --explain{RESET}    show step-by-step working
  {G}quit{RESET}                              exit

  {BOLD}{W}Examples:{RESET}
  {DIM}> 1010 2{RESET}           (binary 1010 to all bases)
  {DIM}> FF 16{RESET}            (hex FF to all bases)
  {DIM}> 255 10 2{RESET}         (decimal 255 to binary)
  {DIM}> 1010 2 --explain{RESET} (show working steps)
  {DIM}> 42 10 --explain{RESET}  (decimal to binary explained)
            """)
            continue

        parts = inp.split()
        explain = "--explain" in parts
        parts = [p for p in parts if p != "--explain"]

        if len(parts) < 2:
            print(f"  {R}❌ Please enter: <number> <from_base>{RESET}\n")
            continue

        number = parts[0]
        try:
            from_base = int(parts[1])
            to_base = int(parts[2]) if len(parts) > 2 else None
        except ValueError:
            print(f"  {R}❌ Base must be a number (2-36){RESET}\n")
            continue

        if from_base < 2 or from_base > 36:
            print(f"  {R}❌ Base must be between 2 and 36{RESET}\n")
            continue

        if not validate(number, from_base):
            valid_digits = DIGITS[:from_base]
            print(f"  {R}❌ Invalid digits for base {from_base}. "
                  f"Valid: {valid_digits}{RESET}\n")
            continue

        if explain:
            decimal = explain_to_decimal(number, from_base)
            if to_base and to_base != 10:
                explain_from_decimal(decimal, to_base)
            elif not to_base:
                for b in [2, 8, 16]:
                    if b != from_base:
                        explain_from_decimal(decimal, b)
                        break
        else:
            if to_base:
                decimal = to_decimal(number, from_base)
                result = from_decimal(decimal, to_base) if to_base != 10 else str(decimal)
                base_names = {2:"Binary",8:"Octal",10:"Decimal",16:"Hexadecimal"}
                print(f"\n  {W}{number.upper()}{RESET} (base {from_base}) = "
                      f"{G}{BOLD}{result}{RESET} "
                      f"(base {to_base} · {base_names.get(to_base, f'Base {to_base}')})\n")
            else:
                results, _ = convert_all(number, from_base)
                print_all(number, from_base, results)

def cli_mode(args):
    explain = "--explain" in args
    args = [a for a in args if a != "--explain"]

    if len(args) < 2:
        print(f"\n  {R}usage: python converter.py <number> <from_base> [to_base] [--explain]{RESET}\n")
        return

    number = args[0]
    try:
        from_base = int(args[1])
        to_base = int(args[2]) if len(args) > 2 else None
    except ValueError:
        print(f"  {R}❌ Base must be a number{RESET}\n")
        return

    if not validate(number, from_base):
        print(f"  {R}❌ Invalid number for base {from_base}{RESET}\n")
        return

    if explain:
        decimal = explain_to_decimal(number, from_base)
        if to_base:
            explain_from_decimal(decimal, to_base)
    else:
        if to_base:
            decimal = to_decimal(number, from_base)
            result = from_decimal(decimal, to_base) if to_base != 10 else str(decimal)
            print(f"\n  {W}{number.upper()}{RESET} (base {from_base}) = {G}{BOLD}{result}{RESET} (base {to_base})\n")
        else:
            results, _ = convert_all(number, from_base)
            print_all(number, from_base, results)

def main():
    if len(sys.argv) == 1:
        interactive_mode()
    else:
        cli_mode(sys.argv[1:])

if __name__ == "__main__":
    main()