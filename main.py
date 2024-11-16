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

        self.create_input_fields()  # create input fields
        self.create_buttons()       # create buttons
        self.create_result_labels() # create result labels

    def create_input_fields(self):
        """
            create and arrange input fields
        """
        # monthly salary
        ttk.Label(self.main_frame, text='月額給与 (円)').grid(row=0, column=0 ,sticky=tk.W, pady=5)
        self.monthly_var = tk.StringVar()
        self.month_entry = ttk.Entry(self.main_frame, textvariable=self.monthly_var)
        self.month_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # bonus 1
        ttk.Label(self.main_frame, text='賞与1 (円)').grid(row=1, column=0 ,sticky=tk.W, pady=5)
        self.bonus1_var = tk.StringVar()
        self.bonus1_entry = ttk.Entry(self.main_frame, textvariable=self.bonus1_var)
        self.bonus1_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # bonus 2
        ttk.Label(self.main_frame, text='賞与2 (円)').grid(row=2, column=0 ,sticky=tk.W, pady=5)
        self.bonus2_var = tk.StringVar()
        self.bonus2_entry = ttk.Entry(self.main_frame, textvariable=self.bonus2_var)
        self.bonus2_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

    def create_buttons(self):
        """
            create and arrange buttons
        """
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text='計算', command=self.calculate).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text='クリア', command=self.clear).grid(row=0, column=1, padx=5)

    def create_result_labels(self):
        """
            create and arrange result labels
        """
        # separator
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        # total yearly salary
        ttk.Label(self.main_frame, text='年間給与金額:').grid(row=5, column=0, sticky=tk.W)
        self.total_label = ttk.Label(self.main_frame, text='')
        self.total_label.grid(row=5, column=1, sticky=tk.W)

        # income amount
        ttk.Label(self.main_frame, text='給与所得金額:').grid(row=6, column=0, sticky=tk.W)
        self.income_label = ttk.Label(self.main_frame, text='')
        self.income_label.grid(row=6, column=1, sticky=tk.W)

    def format_currency(self, amount):
        """
            format amount as currency with thousands separator
        """
        return locale.currency(amount, grouping=True, symbol=False)

    def calculate_income(self, monthly_saraly, bonus1=0, bonus2=0):
        """
            calculate income after employment income deduction
        """
        yearly_salary = (monthly_saraly * 12) + bonus1 + bonus2

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
            # get input values
            monthly = int(self.monthly_var.get() or 0)
            bonus1 = int(self.bonus1_var.get() or 0)
            bonus2 = int(self.bonus2_var.get() or 0)

            total, income = self.calculate_income(monthly, bonus1, bonus2)  # calculate results

            # display results
            self.total_label['text'] = f'\ {self.format_currency(total)}'
            self.income_label['text'] = f'\ {self.format_currency(income)}'
        except ValueError:
            # show error for invalid input
            messagebox.showerror('Error', '数値を正しく入力してください (例: 250000)')

    def clear(self):
        """
            clear all inputs and outputs
        """
        self.monthly_var.set('')
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
