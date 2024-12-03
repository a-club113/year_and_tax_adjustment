import locale
import os
import re
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import filedialog, messagebox, ttk

import PyPDF2
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

# set Japanese locale for curency formating
locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')

class TaxCalculator:
    """
        initialize the tax calculator window
    """
    def __init__(self, root) -> None:
        self.root = root
        self.root.title('年末調整計算ツール')

        # create and set up the main window
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.salary_mode = tk.StringVar(value='single')
        self.monthly_salaries = [tk.StringVar() for _ in range(12)]

        self.create_salary_mode_selection()
        self.create_input_fields()          # create input fields
        self.create_buttons()               # create buttons
        self.create_result_labels()         # create result labels

        self.monthly_salary_frame.grid_remove()

        # binding for auto calculation
        self.root.bind('<Return>', lambda event: self.calculate())
        self.root.bind('<KP_Enter>', lambda event: self.calculate())
        self.root.bind('<BackSpace>', lambda event: self.calculate())
        for key in range(10):
            self.root.bind(f'<Key-{key}>', lambda event: self.calculate())

        self.create_pdf_viewer()    # frame for pdf viewer

    def create_salary_mode_selection(self):
        """
            create radio buttons to select salary input mode
        """
        mode_frame = ttk.Frame(self.main_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Radiobutton(mode_frame, text='1年同一月給', variable=self.salary_mode, value='single', command=self.toggle_salary_mode_input).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(mode_frame, text='月ごとに月給を入力する', variable=self.salary_mode, value='monthly', command=self.toggle_salary_mode_input).grid(row=0, column=1, padx=5)

    def create_input_fields(self):
        """
            create and arrange input fields for single and monthly salary modes
        """
        vcmd = (self.root.register(self.validate_entry), '%P')      # register validate command

        # single monthly salary
        self.single_salary_frame = ttk.Frame(self.main_frame)
        self.single_salary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.single_salary_frame, text='月額給与 (円)').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.monthly_var = tk.StringVar()
        self.month_entry = ttk.Entry(self.single_salary_frame, textvariable=self.monthly_var, validate='key', validatecommand=vcmd)
        self.month_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # month salary inputs
        self.monthly_salary_frame = ttk.Frame(self.main_frame)
        self.monthly_salary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        for i in range(12):
            ttk.Label(self.monthly_salary_frame, text=f'{i + 1}月', anchor='e').grid(row=i//2, column=(i%2)*2, sticky=(tk.E, tk.W), pady=2)
            entry = ttk.Entry(self.monthly_salary_frame, textvariable=self.monthly_salaries[i], width=10, validate='key', validatecommand=vcmd)
            entry.grid(row=i//2, column=(i%2)*2+1, sticky=(tk.W ,tk.E), pady=2)

        # bonus 1
        ttk.Label(self.main_frame, text='賞与1 (円)').grid(row=2, column=0 ,sticky=tk.W, pady=5)
        self.bonus1_var = tk.StringVar()
        self.bonus1_entry = ttk.Entry(self.main_frame, textvariable=self.bonus1_var, validate='key', validatecommand=vcmd)
        self.bonus1_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # bonus 2
        ttk.Label(self.main_frame, text='賞与2 (円)').grid(row=3, column=0 ,sticky=tk.W, pady=5)
        self.bonus2_var = tk.StringVar()
        self.bonus2_entry = ttk.Entry(self.main_frame, textvariable=self.bonus2_var, validate='key', validatecommand=vcmd)
        self.bonus2_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

    def toggle_salary_mode_input(self):
        """
            toggle between single monthly and monthly salary inputs
        """
        if self.salary_mode.get() == 'single':
            self.single_salary_frame.grid(row=1, column=0, columnspan=2)
            self.monthly_salary_frame.grid_remove()
        else:
            self.single_salary_frame.grid_remove()
            self.monthly_salary_frame.grid(row=1, column=0, columnspan=2)

    def create_buttons(self):
        """
            create and arrange buttons
        """
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text='計算', command=self.calculate).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text='クリア', command=self.clear).grid(row=0, column=1, padx=5)

    def create_result_labels(self):
        """
            create and arrange result labels
        """
        # separator
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # total yearly salary
        ttk.Label(self.main_frame, text='年間給与金額:').grid(row=6, column=0, sticky=tk.W)
        self.total_label = ttk.Label(self.main_frame, text='')
        self.total_label.grid(row=6, column=1, sticky=tk.W)

        # income amount
        ttk.Label(self.main_frame, text='給与所得金額:').grid(row=7, column=0, sticky=tk.W)
        self.income_label = ttk.Label(self.main_frame, text='')
        self.income_label.grid(row=7, column=1, sticky=tk.W)

    def create_pdf_viewer(self):
        """
            create frame and button for pdf viewer
        """
        # frame for pdf viewer
        self.pdf_frame = ttk.LabelFrame(self.main_frame, text='PDF ビューワー')
        self.pdf_frame.grid(row=0, column=2, rowspan=8, padx=10, sticky=(tk.N, tk.S, tk.E, tk.W))

        # select pdf button
        self.select_pdf_button = ttk.Button(self.pdf_frame, text='PDF を選択', command=self.open_pdf_file)
        self.select_pdf_button.pack(pady=5)

        # scroll text for view pdf
        self.pdf_text = scrolledtext.ScrolledText(self.pdf_frame, wrap=tk.WORD, width=40, height=20)
        self.pdf_text.pack(padx=5, pady=5, expand=True, fill=tk.BOTH)

        # binding for drag & drop
        self.pdf_frame.drop_target_register(DND_FILES)
        self.pdf_frame.dnd_bind('<<Drop>>', self.handle_drop)

    def open_pdf_file(self):
        """
            open pdf file using dialog
        """
        filetypes = [('PDF ファイル', '*.pdf')]
        filename = filedialog.askopenfilename(title='PDF ファイルを選択', filetypes=filetypes)

        if filename:
            self.load_pdf(filename)

    def handle_drop(self, event):
        """
            handle drop event
        """
        filenames = re.findall(r'{([^}]*)}', event.data)

        if not filenames:
            filenames = event.data.split()

        pdf_files = [f.strip('\'\"') for f in filenames if f.lower().strip('\'\"').endswith('.pdf')]

        if pdf_files:
            self.load_pdf(pdf_files[0])
        else:
            messagebox.showerror('Error' ,'PDF ファイルをドロップしてください')

    def load_pdf(self, filename):
        """
            load pdf and view
        """
        try:
            if not os.path.exists(filename):
                messagebox.showerror('Error', 'ファイルが見つかりません')

                return

            # open file
            with open(filename, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                self.pdf_text.delete(1.0, tk.END)

                for page in pdf_reader.pages:
                    text = page.extract_text()
                    self.pdf_text.insert(tk.END, text + '\n\n')
        except PermissionError:
            messagebox.showerror('Error', 'PDF ファイルにアクセスする権限がありません')
        except FileNotFoundError:
            messagebox.showerror('Error', 'PDF ファイルが見つかりません')
        except Exception as e:
            messagebox.showerror('Error', f'PDF ファイルを読み込むときにエラーが発生しました\n{e}')

    def format_currency(self, amount):
        """
            format amount as currency with thousands separator
        """
        return locale.currency(amount, grouping=True, symbol=False)

    def validate_entry(self, text):
        """
            validate the entry to allow only numeric characters, commas, and spaces
        """
        return re.fullmatch(r'[\d, \s]*', text) is not None

    def calculate_income(self, monthly_saralies, bonus1=0, bonus2=0):
        """
            calculate income after employment income deduction
            support both single monthly salary and monthly variations
        """
        if isinstance(monthly_saralies, int):
            yearly_salary = (monthly_saralies * 12) + bonus1 + bonus2   # if a single monthly salary is used
        else:
            yearly_salary = sum(monthly_saralies) + bonus1 + bonus2     # if monthly salaries are provided

        # calculate income (As of 2024)
        income_rules = [
            (550_999, lambda s: 0),
            (1_618_999, lambda s: s - 550_000),
            (1_619_999, lambda s: 1_069_000),
            (1_621_999, lambda s: 1_070_000),
            (1_623_999, lambda s: 1_072_000),
            (1_627_999, lambda s: 1_074_000),
            (1_799_999, lambda s: ((s // 4_000) * 1000) * 2.4 - 100_000),
            (3_599_999, lambda s: ((s // 4_000) * 1000) * 2.8 - 80_000),
            (6_599_999, lambda s: ((s // 4_000) * 1000) * 3.2 - 440_000),
            (8_499_999, lambda s: s * 0.9 - 1_100_000),
            (float('inf'), lambda s: s - 1_950_000)
        ]

        for threshold, calculation in income_rules:
            if yearly_salary <= threshold:
                income = calculation(yearly_salary)

                break

        return yearly_salary, income

    def calculate(self):
        """
            calculate and display results
        """
        try:
            clean_input = lambda x: int(re.sub(r'[^\d]', '', x) or 0)

            # get bonus values
            bonus1 = clean_input(self.bonus1_var.get())
            bonus2 = clean_input(self.bonus2_var.get())

            # determine salary calcuation mode
            if self.salary_mode.get() == 'single':
                monthly = clean_input(self.monthly_var.get())
                total, income = self.calculate_income(monthly, bonus1, bonus2)
            else:
                monthly_salaries = [clean_input(salary.get()) for salary in self.monthly_salaries]
                total, income = self.calculate_income(monthly_salaries, bonus1, bonus2)

            # display results
            self.total_label['text'] = f'¥ {self.format_currency(total)}'
            self.income_label['text'] = f'¥ {self.format_currency(income)}'
        except ValueError:
            # show error for invalid input
            messagebox.showerror('Error', '数値を正しく入力してください (例: 250000)')

    def clear(self):
        """
            clear all inputs and outputs
        """
        self.monthly_var.set('')

        for monthly_var in self.monthly_salaries:
            monthly_var.set('')

        self.bonus1_var.set('')
        self.bonus2_var.set('')
        self.total_label['text'] = ''
        self.income_label['text'] = ''

def main():
    """
        main function to run the application
    """
    root = TkinterDnD.Tk()
    app = TaxCalculator(root)

    root.mainloop()

if __name__ == '__main__':
    main()
