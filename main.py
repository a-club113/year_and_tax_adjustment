import locale
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import fitz
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

from config import *

# set Japanese locale for curency formating
locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')

class TaxCalculator:
    """
        initialize the tax calculator window
    """
    def __init__(self, root) -> None:
        self.root = root
        self.root.title(UI_CONFIG['APP_TITLE'])
        root.grid_columnconfigure(2, weight=3)
        # binding for auto calculation
        self.root.bind('<Return>', lambda event: self.calculate())
        self.root.bind('<KP_Enter>', lambda event: self.calculate())
        self.root.bind('<BackSpace>', lambda event: self.calculate())
        for key in range(10):
            self.root.bind(f'<Key-{key}>', lambda event: self.calculate())

        # create and set up the main window
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.grid_columnconfigure(2, weight=3)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.salary_mode = tk.StringVar(value='single')
        self.monthly_salaries = [tk.StringVar() for _ in range(12)]

        self.create_salary_mode_selection()
        self.create_input_fields()          # create input fields
        self.create_buttons()               # create buttons
        self.create_result_labels()         # create result labels

        self.monthly_salary_frame.grid_remove()

        self.create_pdf_viewer()    # frame for pdf viewer

        # variables for pdf viewer
        self.current_pdf = None
        self.current_page = 0
        self.pdf_zoom = 1.0

    def create_salary_mode_selection(self):
        """
            create radio buttons to select salary input mode
        """
        mode_frame = ttk.Frame(self.main_frame)
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Radiobutton(mode_frame, text=RADIO_BUTTON_TEXTS['SINGLE'], variable=self.salary_mode, value='single', command=self.toggle_salary_mode_input).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(mode_frame, text=RADIO_BUTTON_TEXTS['MONTHLY'], variable=self.salary_mode, value='monthly', command=self.toggle_salary_mode_input).grid(row=0, column=1, padx=5)

    def create_input_fields(self):
        """
            create and arrange input fields for single and monthly salary modes
        """
        vcmd = (self.root.register(self.validate_entry), '%P')      # register validate command

        # single monthly salary
        self.single_salary_frame = ttk.Frame(self.main_frame)
        self.single_salary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.single_salary_frame, text=LABEL_TEXTS['MONTHLY_SALARY']).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.monthly_var = tk.StringVar()
        self.month_entry = ttk.Entry(self.single_salary_frame, textvariable=self.monthly_var, validate='key', validatecommand=vcmd)
        self.month_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # month salary inputs
        self.monthly_salary_frame = ttk.Frame(self.main_frame)
        self.monthly_salary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        for i in range(12):
            ttk.Label(self.monthly_salary_frame, text=f'{i + 1}月', anchor=tk.E).grid(row=i//2, column=(i%2)*2, sticky=(tk.E, tk.W), pady=2)
            entry = ttk.Entry(self.monthly_salary_frame, textvariable=self.monthly_salaries[i], width=10, validate='key', validatecommand=vcmd)
            entry.grid(row=i//2, column=(i%2)*2+1, sticky=(tk.W ,tk.E), pady=2)

        # bonus 1
        ttk.Label(self.main_frame, text=LABEL_TEXTS['BONUS1']).grid(row=2, column=0 ,sticky=tk.W, pady=5)
        self.bonus1_var = tk.StringVar()
        self.bonus1_entry = ttk.Entry(self.main_frame, textvariable=self.bonus1_var, validate='key', validatecommand=vcmd)
        self.bonus1_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # bonus 2
        ttk.Label(self.main_frame, text=LABEL_TEXTS['BONUS2']).grid(row=3, column=0 ,sticky=tk.W, pady=5)
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

        ttk.Button(button_frame, text=BUTTON_TEXTS['CALCULATE'], command=self.calculate).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text=BUTTON_TEXTS['CLEAR'], command=self.clear).grid(row=0, column=1, padx=5)

    def create_result_labels(self):
        """
            create and arrange result labels
        """
        # separator
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # total yearly salary
        ttk.Label(self.main_frame, text=LABEL_TEXTS['TOTAL_YEARLY_SALARY']).grid(row=6, column=0, sticky=tk.W)
        self.total_label = ttk.Label(self.main_frame, text='')
        self.total_label.grid(row=6, column=1, sticky=tk.W)

        # income amount
        ttk.Label(self.main_frame, text=LABEL_TEXTS['INCOME_AMOUNT']).grid(row=7, column=0, sticky=tk.W)
        self.income_label = ttk.Label(self.main_frame, text='')
        self.income_label.grid(row=7, column=1, sticky=tk.W)

    def create_pdf_viewer(self):
        """
            create frame and button for pdf viewer
        """
        # frame for pdf viewer
        self.pdf_frame = ttk.LabelFrame(self.main_frame, text=UI_CONFIG['PDF_VIEWER_TITLE'])
        self.pdf_frame.grid(row=0, column=2, rowspan=8, padx=10, sticky=(tk.N, tk.S, tk.E, tk.W))

        # button frame
        button_frame = ttk.Frame(self.pdf_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X)

        # select pdf button
        self.select_pdf_button = ttk.Button(button_frame, text=BUTTON_TEXTS['SELECT_PDF'], command=self.open_pdf_file)
        self.select_pdf_button.pack(side=tk.LEFT, padx=5, pady=5)

        # button for moving to previous page
        self.prev_page_button = ttk.Button(button_frame, text=BUTTON_TEXTS['PREV_PAGE'], command=self.prev_page, state=tk.DISABLED)
        self.prev_page_button.pack(side=tk.LEFT, padx=2)

        # label for display page
        self.page_label = ttk.Label(button_frame, text='0 / 0 ページ', width=10)
        self.page_label.pack(side=tk.LEFT, padx=5)

        # button for moving to next page
        self.next_page_button = ttk.Button(button_frame, text=BUTTON_TEXTS['NEXT_PAGE'], command=self.next_page, state=tk.DISABLED)
        self.next_page_button.pack(side=tk.LEFT, padx=2)

        # button for zoom in
        self.zoom_in_button = ttk.Button(button_frame, text=BUTTON_TEXTS['ZOOM_IN'], command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.LEFT, padx=2)

        # label for display zoom level
        self.zoom_label = ttk.Label(button_frame, text='100 %', width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=2)

        # button for zoom out
        self.zoom_out_button = ttk.Button(button_frame, text=BUTTON_TEXTS['ZOOM_OUT'], command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.LEFT, padx=2)

        self.pdf_canvas = tk.Canvas(self.pdf_frame, background='gray', width=600, height=800)
        self.pdf_canvas.pack(fill=tk.BOTH, expand=True)

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
            messagebox.showerror('Error', ERROR_MESSAGES['PDF_DROP_ERROR'])

    def load_pdf(self, filename):
        """
            load pdf and view
        """
        try:
            if self.current_pdf:
                self.current_pdf.close()

            if not os.path.exists(filename):
                messagebox.showerror('Error', ERROR_MESSAGES['FILE_NOT_FOUND'])

                return

            # open file
            self.current_pdf = fitz.open(filename)
            self.current_page = 0
            self.pdf_zoom = 1.0
            self.update_zoom_display()

            self.page_label['text'] = f'{self.current_page + 1} / {len(self.current_pdf)} ページ'
            self.prev_page_button['state'] = tk.DISABLED
            self.next_page_button['state'] = tk.NORMAL if len(self.current_pdf) > 1 else tk.DISABLED

            self.display_page()
        except PermissionError:
            messagebox.showerror('Error', ERROR_MESSAGES['PERMISSION_DENIED'])
        except FileNotFoundError:
            messagebox.showerror('Error', ERROR_MESSAGES['FILE_NOT_FOUND'])
        except Exception as e:
            messagebox.showerror('Error', f'{ERROR_MESSAGES['UNEXPECTED_ERROR']}\n{e}')

    def display_page(self):
        """
            display current page
        """
        if not self.current_pdf:
            return

        page = self.current_pdf[self.current_page]

        zoom = self.pdf_zoom
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        photo = ImageTk.PhotoImage(img)

        self.pdf_canvas.delete('all')
        self.pdf_canvas.config(scrollregion=(0, 0, pix.width, pix.height))
        self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.pdf_canvas.image = photo

    def prev_page(self):
        """
            move to previous page
        """
        if self.current_page > 0:
            self.current_page -= 1
            self.display_page()

            self.page_label['text'] = f'{self.current_page + 1} / {len(self.current_pdf)} ページ'
            self.next_page_button['state'] = tk.NORMAL

            if self.current_page == 0:
                self.prev_page_button['state'] = tk.DISABLED

    def next_page(self):
        """
            move to next page
        """
        if self.current_page < len (self.current_pdf) - 1:
            self.current_page += 1
            self.display_page()

            self.page_label['text'] = f'{self.current_page + 1} / {len(self.current_pdf)} ページ'
            self.prev_page_button['state'] = tk.NORMAL

            if self.current_page == len(self.current_pdf) - 1:
                self.next_page_button['state'] = tk.DISABLED

    def zoom_in(self):
        """
            zoom in, limited to configured maximum (x3.0)
        """
        if self.pdf_zoom * UI_CONFIG['ZOOM_FACTOR'] <= UI_CONFIG['MAX_ZOOM']:
            self.pdf_zoom *= UI_CONFIG['ZOOM_FACTOR']
            self.update_zoom_display()
            self.display_page()

    def zoom_out(self):
        """
            zoom out, limited to configured minimum (x0.25)
        """
        if self.pdf_zoom / UI_CONFIG['ZOOM_FACTOR'] >= UI_CONFIG['MIN_ZOOM']:
            self.pdf_zoom /= UI_CONFIG['ZOOM_FACTOR']
            self.update_zoom_display()
            self.display_page()

    def update_zoom_display(self):
        """
            update zoom level display
        """
        zoom_percentage = int(self.pdf_zoom * 100)
        self.zoom_label['text'] = f'{zoom_percentage} %'

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
            using external configuration for income rules
        """
        if isinstance(monthly_saralies, int):
            yearly_salary = (monthly_saralies * 12) + bonus1 + bonus2   # if a single monthly salary is used
        else:
            yearly_salary = sum(monthly_saralies) + bonus1 + bonus2     # if monthly salaries are provided

        # calculate income using imported INCOME_RULES
        for threshold, calculation in INCOME_RULES:
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
            messagebox.showerror('Error', ERROR_MESSAGES['INVALID_INPUT'])

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
