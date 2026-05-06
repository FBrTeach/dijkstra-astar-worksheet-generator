import os
import tkinter as tk
from tkinter import ttk, messagebox
from config import OUTPUT_DIR, escalating_difficulty
from gui.settings_panel import SettingsPanel
from gui.question_panel import QuestionPanel
from graph.generator import generate_graph
from algorithms import dijkstra, a_star
from render.pdf_export import export_pdf
from settings_store import save as _save_settings


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dijkstra's / A* Question Generator")
        self.geometry('1100x760')
        self.minsize(900, 620)
        self._questions = []
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self._build()
        self._bind_keys()
        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def _on_close(self):
        _save_settings(self._settings.collect())
        self.destroy()

    def _build(self):
        self._settings = SettingsPanel(
            self,
            on_generate=self._generate,
            on_export=self._export,
        )
        self._settings.pack(side='left', fill='y', padx=8, pady=8)

        ttk.Separator(self, orient='vertical').pack(side='left', fill='y', pady=4)

        self._question_panel = QuestionPanel(self)
        self._question_panel.pack(side='left', fill='both', expand=True,
                                  padx=8, pady=8)

    def _bind_keys(self):
        self.bind('<Left>',  lambda e: self._question_panel.go_prev())
        self.bind('<Right>', lambda e: self._question_panel.go_next())
        self.bind('<space>', lambda e: self._question_panel.toggle_reveal())

    # ------------------------------------------------------------------
    def _generate(self, algorithm: str, difficulty: str,
                  num_questions: int, seed: int):
        self._settings.set_status('Generating…')
        self.update_idletasks()

        questions = []

        try:
            for i in range(num_questions):
                q_seed = seed + i

                # Per-question difficulty
                if difficulty == 'Escalating':
                    q_diff = escalating_difficulty(i, num_questions)
                else:
                    q_diff = difficulty

                # Per-question algorithm
                if algorithm == 'Mixed':
                    algo = 'Dijkstra' if i % 2 == 0 else 'A*'
                else:
                    algo = algorithm

                graph = generate_graph(q_diff, algo, q_seed)
                question = (dijkstra.solve(graph, q_seed)
                            if algo == 'Dijkstra'
                            else a_star.solve(graph, q_seed))
                question.difficulty = q_diff
                questions.append(question)

        except RuntimeError as exc:
            self._settings.set_status(str(exc), error=True)
            return

        self._questions = questions
        cfg = self._settings.collect()
        self._settings.set_status(
            f'{num_questions} question(s) ready.', error=False)
        self._settings.enable_export()
        self._question_panel.load(questions,
                                  show_working=cfg.get('show_working', False))

    # ------------------------------------------------------------------
    def _export(self, include_answers: bool, output_folder: str):
        if not self._questions:
            messagebox.showwarning('No questions', 'Generate questions first.')
            return

        os.makedirs(output_folder, exist_ok=True)
        suffix   = '_with_answers' if include_answers else '_blank'
        filepath = os.path.join(output_folder, f'worksheet{suffix}.pdf')

        cfg = self._settings.collect()
        student_info = {
            'student_name':  cfg.get('student_name',  ''),
            'student_class': cfg.get('student_class', ''),
            'student_date':  cfg.get('student_date',  ''),
        }

        try:
            export_pdf(self._questions, filepath,
                       include_answers=include_answers,
                       student_info=student_info,
                       show_working=cfg.get('show_working', False),
                       include_title_page=cfg.get('include_title_page', True))
            self._settings.set_status(f'Saved: worksheet{suffix}.pdf')
        except Exception as exc:
            messagebox.showerror('Export failed', str(exc))
