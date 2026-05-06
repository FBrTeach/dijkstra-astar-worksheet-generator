# Dijkstra's & A\* Worksheet Generator

A Python desktop application that generates ready-to-print graph-algorithm worksheets for **OCR A Level Computer Science (H446)**. Set a difficulty and seed, click Generate, and export a clean PDF — blank for students, with a full answer key if needed.

---

## Features

- **Dijkstra's and A\*** question generation, including a Mixed mode that alternates between the two
- **Difficulty levels** — Easy, Medium, Hard, or Escalating (ramps from Easy to Hard across the question set)
- **Seeded generation** — the same seed always produces the same question; share a seed to reproduce any sheet
- **PDF export**
  - Optional title page with student Name / Class / Date fields
  - Blank worksheet for students
  - Answer key with highlighted shortest path, filled table, and final path/distance
  - Optional Dijkstra working-steps table with superseded values struck through
- **GUI preview** — browse questions with path highlighting, show/hide answers, regenerate the graph layout without changing the question
- **Keyboard shortcuts** — `←` / `→` to navigate, `Space` to toggle the answer
- **Persistent settings** — all options are saved between sessions

---

## Requirements

- Python 3.10+
- `matplotlib`

`tkinter` is included with the standard Python installer on Windows and macOS. Install the one external dependency with:

```
pip install matplotlib
```

---

## Running

```
python main.py
```

---

## Usage

### Generating questions

| Setting | Options |
|---|---|
| Algorithm | Dijkstra, A\*, Mixed |
| Difficulty | Easy, Medium, Hard, Escalating |
| Questions | 1 – 20 |
| Seed | Any integer — click 🎲 for a random one |

Click **Generate Questions** to preview the set in the panel on the right.

### Previewing

- Use **◀ Prev / Next ▶** (or `←` / `→`) to move between questions
- Click **Show Answer** (or `Space`) to reveal the shortest path, highlighted in orange, with the answer table filled in
- Click **↺ Layout** to regenerate the node positions for the current question without changing the graph itself — the new layout carries through to any subsequent PDF export

### Exporting

Set an **Output folder** (defaults to `output/` next to `main.py`).

| Button | File written |
|---|---|
| Worksheet (blank) | `worksheet_blank.pdf` |
| Worksheet + Answer Key | `worksheet_with_answers.pdf` |

Use **Open Worksheet** / **Open Answer Key** to launch the last-exported file directly from the output folder.

#### PDF options

- **Include title page** — adds a cover page with student info fields and a question summary table
- **Show working (Dijkstra)** — the answer-key table shows every tentative distance in the order it was recorded; values later superseded by a shorter path are struck through

### Student info

Fill in Name, Class, and Date in the Settings panel. These appear on the title page when exported; leave them blank to print underlines for students to fill in by hand.

---

## Difficulty presets

| Difficulty | Nodes | Extra edges | Edge weights |
|---|---|---|---|
| Easy | 5 – 6 | 1 – 2 | 1 – 10 |
| Medium | 7 – 8 | 2 – 4 | 1 – 20 |
| Hard | 9 – 10 | 3 – 6 | 1 – 30 |

**Escalating** maps the first third of questions to Easy, the middle third to Medium, and the final third to Hard.

All graphs are undirected and connected. The generator guarantees no ties in edge weights or shortest-path distances, so every question has a unique correct answer.

---

## Project structure

```
main.py                 Entry point
config.py               Difficulty presets and constants
settings_store.py       JSON persistence for GUI settings
algorithms/
    dijkstra.py         Dijkstra's algorithm solver
    a_star.py           A* solver
graph/
    graph.py            Data classes (Graph, Question, SolveStep, WorkingStep)
    generator.py        Random graph generation
    layout.py           Fruchterman-Reingold layout with overlap resolution
gui/
    app.py              Main tkinter window and event wiring
    settings_panel.py   Left-hand settings sidebar
    question_panel.py   Right-hand question preview panel
render/
    graph_view.py       Matplotlib graph drawing (GUI and PDF)
    worksheet.py        tkinter answer-table widget
    pdf_export.py       A4 PDF generation
output/                 Default export destination (git-ignored)
```
