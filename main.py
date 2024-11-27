import locale
import tkinter as tk
from tkinter import messagebox, ttk

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
        # single monthly salary
        self.single_salary_frame = ttk.Frame(self.main_frame)
        self.single_salary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.single_salary_frame, text='月額給与 (円)').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.monthly_var = tk.StringVar()
        self.month_entry = ttk.Entry(self.single_salary_frame, textvariable=self.monthly_var)
        self.month_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # month salary inputs
        self.monthly_salary_frame = ttk.Frame(self.main_frame)
        self.monthly_salary_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        for i in range(12):
            ttk.Label(self.monthly_salary_frame, text=f'{i + 1}月').grid(row=i//2, column=(i%2)*2, sticky=tk.W, pady=2)
            entry = ttk.Entry(self.monthly_salary_frame, textvariable=self.monthly_salaries[i], width=10)
            entry.grid(row=i//2, column=(i%2)*2+1, sticky=(tk.W ,tk.E), pady=2)

        # bonus 1
        ttk.Label(self.main_frame, text='賞与1 (円)').grid(row=2, column=0 ,sticky=tk.W, pady=5)
        self.bonus1_var = tk.StringVar()
        self.bonus1_entry = ttk.Entry(self.main_frame, textvariable=self.bonus1_var)
        self.bonus1_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # bonus 2
        ttk.Label(self.main_frame, text='賞与2 (円)').grid(row=3, column=0 ,sticky=tk.W, pady=5)
        self.bonus2_var = tk.StringVar()
        self.bonus2_entry = ttk.Entry(self.main_frame, textvariable=self.bonus2_var)
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

    def format_currency(self, amount):
        """
            format amount as currency with thousands separator
        """
        return locale.currency(amount, grouping=True, symbol=False)

    def calculate_income(self, monthly_saralies, bonus1=0, bonus2=0):
        """
            calculate income after employment income deduction
            support both single monthly salary and monthly variations
        """
        if isinstance(monthly_saralies, int):
            yearly_salary = (monthly_saralies * 12) + bonus1 + bonus2   # if a single monthly salary is used
        else:
            yearly_salary = sum(monthly_saralies) + bonus1 + bonus2     # if monthly salaries are provided

        # emplyment income deduction calculation (As of 2024)
        if yearly_salary <= 1_625_000:
            deduction = 550_000
        elif yearly_salary <= 1_800_000:
            deduction = (yearly_salary * 0.4) - 100_000
        elif yearly_salary <= 3_600_000:
            deduction = (yearly_salary * 0.3) - 80_000
        elif yearly_salary <= 6_600_000:
            deduction = (yearly_salary * 0.2) - 440_000
        elif yearly_salary <= 8_500_000:
            deduction = (yearly_salary * 0.1) - 1_100_000
        else:
            deduction = 1_950_000

        return yearly_salary, (yearly_salary - deduction)

    def calculate(self):
        """
            calculate and display results
        """
        try:
            # get bonus values
            bonus1 = int(self.bonus1_var.get() or 0)
            bonus2 = int(self.bonus2_var.get() or 0)

            # determine salary calcuation mode
            if self.salary_mode.get() == 'single':
                monthly = int(self.monthly_var.get() or 0)
                total, income = self.calculate_income(monthly, bonus1, bonus2)
            else:
                monthly_salaries = [int(salary.get() or 0) for salary in self.monthly_salaries]
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
    root = tk.Tk()
    app = TaxCalculator(root)

    root.mainloop()

if __name__ == '__main__':
    main()
