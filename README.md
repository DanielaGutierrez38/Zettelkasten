# Zettelkasten

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)  
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)](#)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)  
[![Works Offline](https://img.shields.io/badge/Works-Offline-blue)](#)  

A **minimal, local-first Zettelkasten note-taking app** built with Python and Tkinter.  
Designed to be **offline, distraction-free, and extensible** — perfect for organizing your ideas without clutter.  

---

## Features  
- Incremental numeric note IDs (`1`, `2`, `3` …)  
- Backlinks via `[[note_id]]` (shows which notes reference the current one)  
- Tagging with `#example` (filter notes by tags)  
- Full-text search across notes  
- Dark Mode toggle (⌘D), remembers your preference  
- Remembers window size & last opened note  
- Delete notes with backlink cleanup (replaces `[[id]]` with `(deleted note id)`)  
- Resizable split bars (sidebar ↔ editor, editor ↔ backlinks/tags)  
- Keyboard shortcuts (Mac):  
  - ⌘N → New note  
  - ⌘S → Save note  
  - ⌘F → Focus search  
  - ⌘R → Refresh notes  
  - ⌘D → Toggle dark mode  
  - ⌘⌫ → Delete note  

---

## Installation  

Clone the repo:  

```bash
git clone https://github.com/DanielaGutierrez38/Zettelkasten.git
cd Zettelkasten
```

Install dependencies (Tkinter is included by default on macOS, but Linux users may need this):

```
pip install -r requirements.txt
```

##Usage

Run the app:

```
python3 zettelkasten_app.py
```

Notes are stored in the local zettel/ folder as Markdown (.md) files.
They are not uploaded anywhere — your Zettelkasten is fully offline.

##Project Structure

```
zettelkasten-app/
├── zettelkasten_app.py   # Main application
├── requirements.txt      # Dependencies
├── .gitignore            # Ignore local notes/settings
├── README.md             # Documentation
└── zettel/               # Your notes (ignored by Git)
```

##Contributions
Pull requests and suggestions are welcome!
This project is kept minimal on purpose, but you can fork and extend it with:

*Graph visualization of notes

*Export/import

*Syncing (Dropbox, GitHub, etc.)


