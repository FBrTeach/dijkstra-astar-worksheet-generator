import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from render.graph_view import build_figure
from render.worksheet import build_table_frame
from graph.graph import Question


class QuestionPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._questions: list[Question] = []
        self._index: int = 0
        self._revealed: bool = False
        self._show_working: bool = False
        self._canvas_widget = None
        self._table_frame = None
        self._footer_frame = None
        self._note_label = None
        self._layout_counters: dict = {}   # index -> number of regenerations
        self._build_chrome()

    # ------------------------------------------------------------------
    def _build_chrome(self):
        """Build the permanent chrome (nav bar, canvas area, table area)."""
        # Top navigation bar
        nav = ttk.Frame(self)
        nav.pack(side='top', fill='x', padx=6, pady=4)

        self._prev_btn = ttk.Button(nav, text='◀ Prev', command=self._prev)
        self._prev_btn.pack(side='left')

        self._counter_var = tk.StringVar(value='No questions loaded')
        ttk.Label(nav, textvariable=self._counter_var,
                  font=('Arial', 10, 'bold')).pack(side='left', padx=12)

        self._next_btn = ttk.Button(nav, text='Next ▶', command=self._next)
        self._next_btn.pack(side='left')

        self._regen_btn = ttk.Button(nav, text='↺ Layout',
                                     command=self._regenerate_layout)
        self._regen_btn.pack(side='left', padx=(8, 0))

        self._reveal_btn = ttk.Button(nav, text='Show Answer',
                                      command=self._toggle_reveal)
        self._reveal_btn.pack(side='right', padx=6)

        ttk.Separator(self, orient='horizontal').pack(fill='x')

        # Graph canvas placeholder
        self._graph_area = ttk.Frame(self, relief='flat')
        self._graph_area.pack(side='top', fill='both', expand=True)

        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=2)

        # Table area
        self._table_area = ttk.Frame(self, padding=6)
        self._table_area.pack(side='top', fill='x')

    # ------------------------------------------------------------------
    def load(self, questions: list, show_working: bool = False):
        self._questions = questions
        self._index = 0
        self._revealed = False
        self._show_working = show_working
        self._layout_counters = {}
        self._refresh()

    # Public navigation methods (used for keyboard shortcuts)
    def go_prev(self):
        self._prev()

    def go_next(self):
        self._next()

    def toggle_reveal(self):
        self._toggle_reveal()

    # ------------------------------------------------------------------
    def _prev(self):
        if self._index > 0:
            self._index -= 1
            self._revealed = False
            self._refresh()

    def _next(self):
        if self._index < len(self._questions) - 1:
            self._index += 1
            self._revealed = False
            self._refresh()

    def _toggle_reveal(self):
        if not self._questions:
            return
        self._revealed = not self._revealed
        self._refresh()

    def _regenerate_layout(self):
        if not self._questions:
            return
        import random
        from graph.layout import generate_positions_with_edges
        q = self._questions[self._index]
        counter = self._layout_counters.get(self._index, 0) + 1
        self._layout_counters[self._index] = counter
        rng = random.Random(q.seed + counter * 9973)
        q.graph.positions = generate_positions_with_edges(
            q.graph.nodes, q.graph.edges, rng)
        self._draw_graph(q, len(self._questions))

    # ------------------------------------------------------------------
    def _refresh(self):
        if not self._questions:
            self._counter_var.set('No questions loaded')
            return

        q = self._questions[self._index]
        total = len(self._questions)
        self._counter_var.set(f'Question {self._index + 1} of {total}')
        self._reveal_btn.config(
            text='Hide Answer' if self._revealed else 'Show Answer')
        self._prev_btn.config(state='normal' if self._index > 0 else 'disabled')
        self._next_btn.config(
            state='normal' if self._index < total - 1 else 'disabled')

        self._draw_graph(q, total)
        self._draw_table(q)

    def _draw_graph(self, q: Question, total: int):
        # Destroy previous canvas
        if self._canvas_widget:
            self._canvas_widget.get_tk_widget().destroy()
            self._canvas_widget = None

        highlight = q.final_path if self._revealed else None
        fig = build_figure(q.graph, self._index + 1, total,
                           q.seed, getattr(q, 'difficulty', ''),
                           highlight_path=highlight)
        canvas = FigureCanvasTkAgg(fig, master=self._graph_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self._canvas_widget = canvas
        import matplotlib.pyplot as plt
        plt.close(fig)

    def _draw_table(self, q: Question):
        # Remove old table widgets
        for w in self._table_area.winfo_children():
            w.destroy()
        self._table_frame = None
        self._footer_frame = None
        self._note_label = None

        table_f, footer_f = build_table_frame(
            self._table_area, q, self._revealed,
            show_working=self._show_working)
        table_f.pack(side='top', anchor='w', padx=4, pady=(0, 4))
        footer_f.pack(side='top', anchor='w', padx=4, pady=(0, 6))
        self._table_frame = table_f
        self._footer_frame = footer_f
