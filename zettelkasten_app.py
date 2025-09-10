#!/usr/bin/env python3
"""
Zettelkasten App
---------------
Features:
- Incremental numeric note IDs (1, 2, 3…)
- Create, edit, and manage notes
- Use [[note_id]] to link notes
- Shows backlinks when opening a note
- Search notes by keyword
- Detect and filter by tags (#example)
- Keyboard shortcuts (⌘N, ⌘S, ⌘F, ⌘R, ⌘D, ⌘⌫)
- Resizable split bars (sidebar ↔ editor, editor ↔ backlinks/tags)
- Dark Mode toggle (remembers preference)
- Remembers window size
- Remembers last opened note
- Delete notes with backlink cleanup
"""

import os
import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import re
import json

NOTES_DIR = "zettel"
SETTINGS_FILE = "settings.json"

# === SETTINGS HANDLING ===
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception:
        pass

# === NOTE HELPERS ===
def ensure_notes_dir():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

def list_note_files():
    return [f for f in os.listdir(NOTES_DIR) if f.endswith(".md") and not f.startswith(".")]

def get_next_id():
    ensure_notes_dir()
    ids = []
    for fname in list_note_files():
        try:
            note_id = int(fname.split("_", 1)[0])
            ids.append(note_id)
        except ValueError:
            continue
    return str(max(ids) + 1 if ids else 1)

def generate_filename(note_id: str, title: str) -> str:
    slug = "_".join(title.strip().split())[:30]
    return f"{note_id}_{slug}.md"

def extract_id_from_filename(filename: str) -> str:
    return filename.split("_", 1)[0]

def find_backlinks(note_id: str):
    backlinks = []
    for fname in list_note_files():
        filepath = os.path.join(NOTES_DIR, fname)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                if f"[[{note_id}]]" in content:
                    backlinks.append(fname)
        except Exception:
            continue
    return backlinks

def extract_tags():
    tags = set()
    for fname in list_note_files():
        filepath = os.path.join(NOTES_DIR, fname)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                found = re.findall(r"#\w+", content)
                tags.update(found)
        except Exception:
            continue
    return sorted(tags)

# === MAIN APP ===
class ZettelkastenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zettelkasten")

        ensure_notes_dir()
        self.settings = load_settings()

        # Theme + Window
        self.dark_mode = self.settings.get("dark_mode", False)
        width = self.settings.get("width", 900)
        height = self.settings.get("height", 600)
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(700, 500)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # === UI SETUP ===
        # Search bar
        search_frame = tk.Frame(root)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(search_frame, text="Go", command=self.search_notes).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=self.refresh_list).pack(side=tk.LEFT)

        # Paned windows
        outer_paned = tk.PanedWindow(root, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=6)
        outer_paned.pack(fill=tk.BOTH, expand=True)
        inner_paned = tk.PanedWindow(outer_paned, orient=tk.HORIZONTAL, sashrelief=tk.RAISED, sashwidth=6)
        outer_paned.add(inner_paned, stretch="always")

        # Sidebar
        self.sidebar = tk.Listbox(inner_paned, width=35)
        inner_paned.add(self.sidebar)
        self.sidebar.bind("<Double-Button-1>", self.load_note)

        # Editor
        self.text = scrolledtext.ScrolledText(inner_paned, wrap=tk.WORD, font=("Helvetica", 12))
        inner_paned.add(self.text)

        # Bottom frame (backlinks + tags)
        bottom_frame = tk.Frame(outer_paned)
        outer_paned.add(bottom_frame, stretch="never")

        self.backlinks_label = tk.Label(bottom_frame, text="Backlinks:", anchor="w")
        self.backlinks_label.pack(fill=tk.X)
        self.backlinks_box = tk.Listbox(bottom_frame, height=4)
        self.backlinks_box.pack(fill=tk.X)
        self.backlinks_box.bind("<Double-Button-1>", self.open_backlink)

        tag_frame = tk.Frame(bottom_frame)
        tag_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(tag_frame, text="Tags:").pack(side=tk.LEFT)
        self.tag_list = tk.Listbox(tag_frame, height=3, exportselection=False)
        self.tag_list.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.tag_list.bind("<<ListboxSelect>>", self.filter_by_tag)
        tk.Button(tag_frame, text="Refresh Tags", command=self.refresh_tags).pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        tk.Button(button_frame, text="New Note (⌘N)", command=self.new_note).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Save Note (⌘S)", command=self.save_note).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Delete Note (⌘⌫)", command=self.delete_note).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Refresh (⌘R)", command=self.refresh_list).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(button_frame, text="Toggle Dark Mode (⌘D)", command=self.toggle_dark_mode).pack(side=tk.LEFT, padx=5, pady=5)

        # Track state
        self.current_file = None
        self.current_id = None

        # Load initial data
        self.refresh_list()
        self.refresh_tags()
        self.apply_theme()

        # Auto-load last note if available
        last_note = self.settings.get("last_note")
        if last_note and last_note in list_note_files():
            self.load_note_by_name(last_note)

        # Keyboard shortcuts
        self.root.bind("<Command-n>", lambda e: self.new_note())
        self.root.bind("<Command-s>", lambda e: self.save_note())
        self.root.bind("<Command-f>", lambda e: self.focus_search())
        self.root.bind("<Command-r>", lambda e: self.refresh_list())
        self.root.bind("<Command-d>", lambda e: self.toggle_dark_mode())
        self.root.bind("<Command-BackSpace>", lambda e: self.delete_note())

    # === SETTINGS SAVE ON EXIT ===
    def on_close(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        save_settings({
            "dark_mode": self.dark_mode,
            "width": width,
            "height": height,
            "last_note": os.path.basename(self.current_file) if self.current_file else None
        })
        self.root.destroy()

    # === THEME HANDLING ===
    def apply_theme(self):
        bg, fg = ("#1e1e1e", "#ffffff") if self.dark_mode else ("#ffffff", "#000000")
        self.root.configure(bg=bg)
        self.text.configure(bg=bg, fg=fg, insertbackground=fg)
        self.sidebar.configure(bg=bg, fg=fg)
        self.backlinks_box.configure(bg=bg, fg=fg)
        self.tag_list.configure(bg=bg, fg=fg)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        settings = load_settings()
        settings["dark_mode"] = self.dark_mode
        save_settings(settings)

    # === CORE FUNCTIONS ===
    def refresh_list(self, filter_func=None):
        self.sidebar.delete(0, tk.END)
        files = sorted(list_note_files(), key=lambda x: int(x.split("_", 1)[0]))
        for f in files:
            if filter_func and not filter_func(f):
                continue
            self.sidebar.insert(tk.END, f)

    def new_note(self):
        title = simpledialog.askstring("New Note", "Enter note title:")
        if not title:
            return
        note_id = get_next_id()
        filename = generate_filename(note_id, title)
        filepath = os.path.join(NOTES_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"ID: {note_id}\n")
            f.write(f"Created: {datetime.datetime.now().isoformat()}\n\n")
            f.write("Links: Use [[note_id]] to reference another note.\n")
            f.write("Tags: Add with #example\n")
        self.refresh_list()
        self.refresh_tags()
        messagebox.showinfo("Note Created", f"Created note: {filename}")

    def save_note(self):
        if not self.current_file:
            messagebox.showwarning("No File", "No note is open.")
            return
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", tk.END))
        messagebox.showinfo("Saved", f"Saved {os.path.basename(self.current_file)}")
        self.update_backlinks()
        self.refresh_tags()

    def load_note_by_name(self, filename):
        filepath = os.path.join(NOTES_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content)
        self.current_file = filepath
        self.current_id = extract_id_from_filename(filename)
        self.update_backlinks()

    def load_note(self, event=None):
        try:
            selection = self.sidebar.curselection()
            if not selection:
                return
            filename = self.sidebar.get(selection[0])
            self.load_note_by_name(filename)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_backlinks(self):
        if not self.current_id:
            return
        self.backlinks_box.delete(0, tk.END)
        links = find_backlinks(self.current_id)
        for f in links:
            self.backlinks_box.insert(tk.END, f)

    def open_backlink(self, event):
        selection = self.backlinks_box.curselection()
        if not selection:
            return
        filename = self.backlinks_box.get(selection[0])
        index = None
        for i in range(self.sidebar.size()):
            if self.sidebar.get(i) == filename:
                index = i
                break
        if index is not None:
            self.sidebar.selection_clear(0, tk.END)
            self.sidebar.selection_set(index)
            self.sidebar.event_generate("<<ListboxSelect>>")
            self.load_note_by_name(filename)

    def delete_note(self):
        """Delete the currently open note and update backlinks"""
        if not self.current_file:
            messagebox.showwarning("No File", "No note is open.")
            return

        note_id = self.current_id
        filename = os.path.basename(self.current_file)

        confirm = messagebox.askyesno("Delete Note", f"Are you sure you want to delete:\n\n{filename}?")
        if not confirm:
            return

        try:
            os.remove(self.current_file)

            # Update backlinks
            for fname in list_note_files():
                if fname == filename:
                    continue
                filepath = os.path.join(NOTES_DIR, fname)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if f"[[{note_id}]]" in content:
                    new_content = content.replace(f"[[{note_id}]]", f"(deleted note {note_id})")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)

            messagebox.showinfo("Deleted", f"Deleted {filename} and updated backlinks")

            self.current_file = None
            self.current_id = None
            self.text.delete("1.0", tk.END)
            self.backlinks_box.delete(0, tk.END)
            self.refresh_list()
            self.refresh_tags()

        except Exception as e:
            messagebox.showerror("Error", f"Could not delete note:\n{e}")

    def search_notes(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            self.refresh_list()
            return

        def filter_func(fname):
            filepath = os.path.join(NOTES_DIR, fname)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().lower()
                    return (keyword in fname.lower()) or (keyword in content)
            except Exception:
                return False

        self.refresh_list(filter_func)

    def refresh_tags(self):
        self.tag_list.delete(0, tk.END)
        for tag in extract_tags():
            self.tag_list.insert(tk.END, tag)

    def filter_by_tag(self, event):
        selection = self.tag_list.curselection()
        if not selection:
            return
        tag = self.tag_list.get(selection[0])

        def filter_func(fname):
            filepath = os.path.join(NOTES_DIR, fname)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    return tag in content
            except Exception:
                return False

        self.refresh_list(filter_func)

    def focus_search(self):
        self.search_entry.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = ZettelkastenApp(root)
    root.mainloop()
