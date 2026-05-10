import os
import shutil
import sys
from datetime import datetime

# ANSI colors
G = "\033[92m"
Y = "\033[93m"
B = "\033[94m"
C = "\033[96m"
R = "\033[91m"
W = "\033[97m"
DIM = "\033[90m"
RESET = "\033[0m"
BOLD = "\033[1m"

# File type categories
CATEGORIES = {
    "🖼️  Images":      [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg",
                        ".webp", ".ico", ".tiff", ".raw"],
    "🎵  Music":       [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
    "🎬  Videos":      [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
                        ".webm", ".m4v"],
    "📄  Documents":   [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx",
                        ".ppt", ".pptx", ".odt", ".rtf", ".csv"],
    "🗜️  Archives":    [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
    "💻  Code":        [".py", ".js", ".ts", ".html", ".css", ".java",
                        ".cpp", ".c", ".cs", ".php", ".rb", ".go",
                        ".rs", ".json", ".xml", ".yaml", ".yml",
                        ".sh", ".bat", ".ipynb"],
    "🖥️  Executables": [".exe", ".msi", ".apk", ".dmg", ".deb"],
    "🔤  Fonts":       [".ttf", ".otf", ".woff", ".woff2"],
    "📦  Others":      []
}

def get_category(ext):
    ext = ext.lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "📦  Others"

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes/(1024**2):.1f} MB"
    return f"{size_bytes/(1024**3):.1f} GB"

def scan_folder(folder):
    files = []
    for f in os.listdir(folder):
        full = os.path.join(folder, f)
        if os.path.isfile(full):
            ext = os.path.splitext(f)[1]
            size = os.path.getsize(full)
            files.append((f, ext, size, full))
    return files

def print_summary(files):
    if not files:
        print(f"\n  {Y}⚠️  No files found in this folder.{RESET}\n")
        return

    category_groups = {}
    for name, ext, size, path in files:
        cat = get_category(ext)
        if cat not in category_groups:
            category_groups[cat] = []
        category_groups[cat].append((name, size))

    total_size = sum(s for _, _, s, _ in files)

    print(f"\n  {BOLD}{W}📊 Scan Results{RESET}")
    print(f"  {DIM}{'─' * 50}{RESET}")
    print(f"  {W}Total files: {RESET}{C}{len(files)}{RESET}   "
          f"{W}Total size: {RESET}{C}{format_size(total_size)}{RESET}")
    print(f"  {DIM}{'─' * 50}{RESET}\n")

    for cat, items in sorted(category_groups.items()):
        cat_size = sum(s for _, s in items)
        print(f"  {BOLD}{cat}{RESET}  "
              f"{DIM}({len(items)} files · {format_size(cat_size)}){RESET}")
        for name, size in items[:5]:
            print(f"    {DIM}· {name[:45]:<45} {format_size(size)}{RESET}")
        if len(items) > 5:
            print(f"    {DIM}  ... and {len(items)-5} more{RESET}")
        print()

def organize(folder, dry_run=False):
    files = scan_folder(folder)
    if not files:
        print(f"\n  {Y}No files to organize.{RESET}\n")
        return

    print_summary(files)

    if dry_run:
        print(f"  {Y}🔍 DRY RUN — no files will be moved.{RESET}")
        print(f"  {DIM}Run without --dry-run to actually organize.{RESET}\n")

    moved = 0
    skipped = 0
    errors = 0
    log = []

    print(f"  {BOLD}{W}{'─' * 50}{RESET}")
    print(f"  {BOLD}{W}{'Moving files...' if not dry_run else 'Preview...'}{RESET}")
    print(f"  {DIM}{'─' * 50}{RESET}\n")

    for name, ext, size, full_path in files:
        cat = get_category(ext)
        # clean folder name: remove emoji and strip
        folder_name = cat.split()[-1].strip()
        dest_dir = os.path.join(folder, folder_name)

        dest_path = os.path.join(dest_dir, name)

        # handle duplicates
        if os.path.exists(dest_path):
            base, extension = os.path.splitext(name)
            timestamp = datetime.now().strftime('%H%M%S')
            name = f"{base}_{timestamp}{extension}"
            dest_path = os.path.join(dest_dir, name)
            skipped += 1

        if dry_run:
            print(f"  {DIM}[preview]{RESET} {name[:40]:<40} → {folder_name}/")
            moved += 1
        else:
            try:
                os.makedirs(dest_dir, exist_ok=True)
                shutil.move(full_path, dest_path)
                print(f"  {G}[moved]{RESET}   {name[:40]:<40} → {folder_name}/")
                log.append(f"{full_path} → {dest_path}")
                moved += 1
            except Exception as e:
                print(f"  {R}[error]{RESET}   {name} — {e}")
                errors += 1

    # save log
    if not dry_run and log:
        log_path = os.path.join(folder, "organizer_log.txt")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"Organized on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write('\n'.join(log))

    print(f"\n  {DIM}{'─' * 50}{RESET}")
    print(f"  {G}✅ Done!{RESET}")
    print(f"  {W}Moved:   {RESET}{G}{moved}{RESET}")
    print(f"  {W}Skipped: {RESET}{Y}{skipped}{RESET}")
    print(f"  {W}Errors:  {RESET}{R}{errors}{RESET}")
    if not dry_run:
        print(f"  {DIM}Log saved: organizer_log.txt{RESET}")
    print()

def main():
    args = sys.argv[1:]

    if not args:
        print(f"\n  {C}{BOLD}📁 File Organizer{RESET}")
        print(f"\n  {W}usage:{RESET}")
        print(f"  {DIM}python organizer.py <folder>{RESET}")
        print(f"  {DIM}python organizer.py <folder> --dry-run{RESET}")
        print(f"\n  {W}examples:{RESET}")
        print(f"  {DIM}python organizer.py C:\\Users\\VICTUS\\Downloads{RESET}")
        print(f"  {DIM}python organizer.py C:\\Users\\VICTUS\\Downloads --dry-run{RESET}\n")
        return

    folder = args[0]
    dry_run = "--dry-run" in args

    if not os.path.exists(folder):
        print(f"\n  {R}❌ Folder not found: {folder}{RESET}\n")
        return

    if not os.path.isdir(folder):
        print(f"\n  {R}❌ Not a folder: {folder}{RESET}\n")
        return

    print(f"\n  {C}{BOLD}📁 File Organizer{RESET}")
    print(f"  {DIM}Target: {W}{folder}{RESET}")
    print(f"  {DIM}Mode:   {W}{'Dry Run (preview)' if dry_run else 'Live (will move files)'}{RESET}")

    if not dry_run:
        confirm = input(f"\n  {Y}⚠️  This will move files. Continue? (y/n): {RESET}").strip().lower()
        if confirm != 'y':
            print(f"\n  {DIM}Cancelled. Run with --dry-run to preview first.{RESET}\n")
            return

    organize(folder, dry_run)

if __name__ == "__main__":
    main()