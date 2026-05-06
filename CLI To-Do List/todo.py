import json
import sys
import os
from datetime import date

DATA_FILE = "tasks.json"

def load():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE) as f:
        return json.load(f)

def save(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def next_id(tasks):
    return max((t["id"] for t in tasks), default=0) + 1

def cmd_list(tasks):
    if not tasks:
        print("  no tasks yet. add one with: python todo.py add <text>")
        return
    done = sum(1 for t in tasks if t["done"])
    print(f"\n  ── tasks ({done}/{len(tasks)} done) ─────────────\n")
    for t in tasks:
        chk = "✓" if t["done"] else " "
        txt = f"\033[90m{t['text']}\033[0m" if t["done"] else t["text"]
        print(f"  [{chk}] \033[33m#{t['id']}\033[0m  {txt}")
    print()

def cmd_add(tasks, args):
    if not args:
        print("  usage: python todo.py add <task description>")
        return
    text = " ".join(args)
    task = {"id": next_id(tasks), "text": text, "done": False, "created": str(date.today())}
    tasks.append(task)
    save(tasks)
    print(f"  \033[32madded task #{task['id']}: \"{text}\"\033[0m")

def cmd_done(tasks, args):
    if not args or not args[0].isdigit():
        print("  usage: python todo.py done <id>")
        return
    tid = int(args[0])
    task = next((t for t in tasks if t["id"] == tid), None)
    if not task:
        print(f"  \033[31merror: task #{tid} not found\033[0m")
        return
    task["done"] = True
    save(tasks)
    print(f"  \033[32mdone: \"{task['text']}\"\033[0m")

def cmd_delete(tasks, args):
    if not args or not args[0].isdigit():
        print("  usage: python todo.py delete <id>")
        return
    tid = int(args[0])
    task = next((t for t in tasks if t["id"] == tid), None)
    if not task:
        print(f"  \033[31merror: task #{tid} not found\033[0m")
        return
    tasks.remove(task)
    save(tasks)
    print(f"  \033[31mdeleted: \"{task['text']}\"\033[0m")

def cmd_clear(tasks):
    removed = [t for t in tasks if t["done"]]
    remaining = [t for t in tasks if not t["done"]]
    save(remaining)
    print(f"  removed {len(removed)} completed task(s). {len(remaining)} remaining.")
    return remaining

def cmd_help():
    print("""
  usage: python todo.py [command]

  list              show all tasks
  add <text>        add a new task
  done <id>         mark task as complete
  delete <id>       remove a task
  clear             remove all completed tasks
  export            print tasks as JSON
    """)

def main():
    tasks = load()
    args = sys.argv[1:]
    cmd = args[0] if args else "list"

    if cmd == "list":      cmd_list(tasks)
    elif cmd == "add":     cmd_add(tasks, args[1:])
    elif cmd == "done":    cmd_done(tasks, args[1:])
    elif cmd == "delete":  cmd_delete(tasks, args[1:])
    elif cmd == "clear":   cmd_clear(tasks)
    elif cmd == "export":  print(json.dumps(tasks, indent=2))
    elif cmd in ("--help", "-h", "help"): cmd_help()
    else:
        print(f"  unknown command: {cmd}. try --help")

if __name__ == "__main__":
    main()