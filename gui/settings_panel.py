import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
from config import ALGORITHM_CHOICES, DIFFICULTY_OPTIONS, OUTPUT_DIR
from settings_store import load as _load_settings


class SettingsPanel(ttk.LabelFrame):
    def __init__(self, parent, on_generate, on_export):
        super().__init__(parent, text='Settings', padding=10)
        self._on_generate = on_generate
        self._on_export = on_export
        self._saved = _load_settings()
        # Fill in default output folder if none was saved
        if not self._saved['output_folder']:
            self._saved['output_folder'] = OUTPUT_DIR
        self._build()

    def _build(self):
        row = 0

        # Algorithm
        ttk.Label(self, text='Algorithm:').grid(
            row=row, column=0, sticky='w', pady=3)
        self.algo_var = tk.StringVar(value=self._saved['algorithm'])
        for i, choice in enumerate(ALGORITHM_CHOICES):
            ttk.Radiobutton(self, text=choice, variable=self.algo_var,
                            value=choice).grid(row=row + i, column=1, sticky='w')
        row += len(ALGORITHM_CHOICES)

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Difficulty
        ttk.Label(self, text='Difficulty:').grid(
            row=row, column=0, sticky='w', pady=3)
        self.diff_var = tk.StringVar(value=self._saved['difficulty'])
        diff_box = ttk.Combobox(self, textvariable=self.diff_var,
                                values=DIFFICULTY_OPTIONS,
                                state='readonly', width=12)
        diff_box.grid(row=row, column=1, sticky='w')
        row += 1

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Number of questions
        ttk.Label(self, text='Questions:').grid(
            row=row, column=0, sticky='w', pady=3)
        self.num_var = tk.IntVar(value=self._saved['num_questions'])
        ttk.Spinbox(self, from_=1, to=20, textvariable=self.num_var,
                    width=5).grid(row=row, column=1, sticky='w')
        row += 1

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Seed
        ttk.Label(self, text='Seed:').grid(
            row=row, column=0, sticky='w', pady=3)
        seed_frame = ttk.Frame(self)
        seed_frame.grid(row=row, column=1, sticky='w')
        self.seed_var = tk.StringVar(value=self._saved['seed'])
        ttk.Entry(seed_frame, textvariable=self.seed_var, width=7).pack(side='left')
        ttk.Button(seed_frame, text='🎲', width=3,
                   command=self._randomise_seed).pack(side='left', padx=2)
        row += 1

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Output folder
        ttk.Label(self, text='Output folder:', font=('Arial', 8, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky='w')
        row += 1
        self.folder_var = tk.StringVar(value=self._saved['output_folder'])
        folder_entry = ttk.Entry(self, textvariable=self.folder_var, width=20)
        folder_entry.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0, 2))
        row += 1
        ttk.Button(self, text='Browse…',
                   command=self._browse_folder).grid(
            row=row, column=0, columnspan=2, sticky='ew')
        row += 1

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Student info
        ttk.Label(self, text='Student info:', font=('Arial', 8, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky='w')
        row += 1
        for label, attr in [('Name:', 'name'), ('Class:', 'class_'), ('Date:', 'date')]:
            ttk.Label(self, text=label).grid(row=row, column=0, sticky='w', pady=2)
            key = f'student_{attr.rstrip("_")}'
            var = tk.StringVar(value=self._saved.get(key, ''))
            setattr(self, f'_{attr.rstrip("_")}_var', var)
            ttk.Entry(self, textvariable=var, width=14).grid(
                row=row, column=1, sticky='ew', pady=2)
            row += 1

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Show working (Dijkstra only)
        self.show_working_var = tk.BooleanVar(value=self._saved.get('show_working', False))
        ttk.Checkbutton(self, text='Show working (Dijkstra)',
                        variable=self.show_working_var).grid(
            row=row, column=0, columnspan=2, sticky='w', pady=2)
        row += 1

        self.title_page_var = tk.BooleanVar(
            value=self._saved.get('include_title_page', True))
        ttk.Checkbutton(self, text='Include title page',
                        variable=self.title_page_var).grid(
            row=row, column=0, columnspan=2, sticky='w', pady=2)
        row += 1

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Generate
        ttk.Button(self, text='Generate Questions',
                   command=self._fire_generate).grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=4)
        row += 1

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Export buttons
        ttk.Label(self, text='Export PDF:', font=('Arial', 8, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky='w')
        row += 1

        self._exp_blank_btn = ttk.Button(
            self, text='Worksheet (blank)',
            command=lambda: self._fire_export(answers=False),
            state='disabled')
        self._exp_blank_btn.grid(row=row, column=0, columnspan=2,
                                 sticky='ew', pady=2)
        row += 1

        self._exp_ans_btn = ttk.Button(
            self, text='Worksheet + Answer Key',
            command=lambda: self._fire_export(answers=True),
            state='disabled')
        self._exp_ans_btn.grid(row=row, column=0, columnspan=2,
                               sticky='ew', pady=2)
        row += 1

        ttk.Separator(self, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=6)
        row += 1

        # Open buttons
        ttk.Label(self, text='Open PDF:', font=('Arial', 8, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky='w')
        row += 1

        ttk.Button(self, text='Open Worksheet',
                   command=lambda: self._open_pdf('_blank')).grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=2)
        row += 1

        ttk.Button(self, text='Open Answer Key',
                   command=lambda: self._open_pdf('_with_answers')).grid(
            row=row, column=0, columnspan=2, sticky='ew', pady=2)
        row += 1

        # Status
        self.status_var = tk.StringVar(value='')
        self._status_label = ttk.Label(self, textvariable=self.status_var,
                                       wraplength=170, font=('Arial', 8))
        self._status_label.grid(row=row, column=0, columnspan=2,
                                sticky='w', pady=(4, 0))

    # ------------------------------------------------------------------
    def _randomise_seed(self):
        self.seed_var.set(str(random.randint(1, 9999)))

    def _browse_folder(self):
        folder = filedialog.askdirectory(
            title='Choose output folder',
            initialdir=self.folder_var.get(),
        )
        if folder:
            self.folder_var.set(folder)

    def _fire_generate(self):
        seed_text = self.seed_var.get().strip()
        try:
            seed = int(seed_text)
        except ValueError:
            self.set_status('Seed must be an integer.', error=True)
            return
        self.set_status('')
        self._on_generate(
            algorithm=self.algo_var.get(),
            difficulty=self.diff_var.get(),
            num_questions=self.num_var.get(),
            seed=seed,
        )

    def _fire_export(self, answers: bool):
        self._on_export(
            include_answers=answers,
            output_folder=self.folder_var.get(),
        )

    def _open_pdf(self, suffix: str):
        filepath = os.path.join(self.folder_var.get(), f'worksheet{suffix}.pdf')
        if not os.path.exists(filepath):
            messagebox.showwarning(
                'File not found',
                f'No PDF found at:\n{filepath}\n\nExport it first.')
            return
        os.startfile(filepath)

    def enable_export(self):
        self._exp_blank_btn.config(state='normal')
        self._exp_ans_btn.config(state='normal')

    def collect(self) -> dict:
        """Return current widget values as a dict suitable for settings_store.save()."""
        return {
            'algorithm':     self.algo_var.get(),
            'difficulty':    self.diff_var.get(),
            'num_questions': self.num_var.get(),
            'seed':          self.seed_var.get(),
            'output_folder': self.folder_var.get(),
            'student_name':  self._name_var.get(),
            'student_class': self._class_var.get(),
            'student_date':  self._date_var.get(),
            'show_working':       self.show_working_var.get(),
            'include_title_page': self.title_page_var.get(),
        }

    def set_status(self, msg: str, error: bool = False):
        self.status_var.set(msg)
        self._status_label.config(foreground='#c0392b' if error else '#27ae60')
