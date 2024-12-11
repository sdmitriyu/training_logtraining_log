import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
from tkcalendar import DateEntry
import json
from datetime import datetime
from function import (date_search, exercises_search, export_to_csv, import_from_csv, edit_entry, delete_record,
                      show_statistics, show_progress)

# Файл для сохранения данных
data_file = 'training_log.json'


def load_data():
    """Загрузка данных о тренировках из файла в формате JSON."""
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    """Сохранение данных о тренировках в файл в формате JSON."""
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


class TrainingLogApp:
    def __init__(self, root):
        self.root = root
        root.title("Дневник тренировок")
        self.create_widgets()
        self.tree = None

    def create_widgets(self):
        # Виджеты для ввода данных
        self.exercise_label = ttk.Label(self.root, text="Упражнение:")
        self.exercise_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
        self.exercise_entry = ttk.Entry(self.root)
        self.exercise_entry.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5)

        self.weight_label = ttk.Label(self.root, text="Вес:")
        self.weight_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)
        self.weight_entry = ttk.Entry(self.root, validate="key",
                                      validatecommand=(self.root.register(self.validate_positive_number), '%P'))
        self.weight_entry.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)

        # Поле ввода для повторений
        self.repetitions_label = ttk.Label(self.root, text="Повторения:")
        self.repetitions_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)
        self.repetitions_entry = ttk.Entry(self.root, validate="key",
                                           validatecommand=(self.root.register(self.validate_positive_number), '%P'))
        self.repetitions_entry.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)

        self.add_button = ttk.Button(self.root, text="Добавить запись", command=self.add_entry)
        self.add_button.grid(column=0, row=3, columnspan=2, pady=10)

        self.view_button = ttk.Button(self.root, text="Просмотреть записи", command=self.view_records)
        self.view_button.grid(column=0, row=4, columnspan=2, pady=10)

        self.csv_export_btn = ttk.Button(self.root, text='Экспорт в CSV', command=lambda: export_to_csv(self.tree))
        self.csv_export_btn.grid(column=2, row=4, columnspan=2, sticky='e')

        self.csv_import_btn = ttk.Button(self.root, text='Импорт в CSV', command=lambda: import_from_csv(self.tree))
        self.csv_import_btn.grid(column=2, row=3, columnspan=2, sticky='e')

    def validate_positive_number(self, value):
        """
        Проверяем, чтобы значение было числом больше или равным нулю.
        """
        if value == "":
            return True  # Разрешаем пустое значение (при удалении текста)
        try:
            number = float(value)
            return number >= 0
        except ValueError:
            return False  # Если значение не число

    def add_entry(self):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exercise = self.exercise_entry.get()
        weight = self.weight_entry.get()
        repetitions = self.repetitions_entry.get()

        if not (exercise and weight and repetitions):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        entry = {
            'date': date,
            'exercise': exercise,
            'weight': weight,
            'repetitions': repetitions
        }

        data = load_data()
        data.append(entry)
        save_data(data)

        # Очистка полей ввода после добавления
        self.exercise_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.repetitions_entry.delete(0, tk.END)

        messagebox.showinfo("Успешно", "Запись успешно добавлена!")

    def view_records(self):
        data = load_data()

        # Создаем окно для отображения записей
        records_window = Toplevel(self.root)
        records_window.title("Записи тренировок")

        # Виджеты для поиска по дате
        date_label = ttk.Label(records_window, text="Поиск по дате:")
        date_label.grid(row=0, column=0)

        self.date_entry = DateEntry(records_window, width=10, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=1, column=0)

        date_search_btn = ttk.Button(records_window, text='Поиск по дате',
                                     command=lambda: date_search(self.tree, self.date_entry.get(), load_data()))
        date_search_btn.grid(row=2, column=0)

        self.search_exercises_label = ttk.Label(records_window, text='Поиск по упражнениям:')
        self.search_exercises_label.grid(row=0, column=1, sticky='w')

        self.search_exercises_entry = ttk.Entry(records_window)
        self.search_exercises_entry.grid(row=1, column=1, sticky='w')

        search_exercises_btn = ttk.Button(records_window, text='Поиск по упражнениям',
                                          command=lambda: exercises_search(self.tree, self.search_exercises_entry.get(),
                                                                           load_data()))
        search_exercises_btn.grid(row=2, column=1, sticky='w')

        edit_entry_btn = ttk.Button(records_window, text='Редактировать запись', command=lambda: edit_entry(self.tree))
        edit_entry_btn.grid(row=0, column=2)

        delete_entry_btn = ttk.Button(records_window, text='Удалить запись', command=lambda: delete_record(self.tree))
        delete_entry_btn.grid(row=1, column=2)

        statistics_btn = ttk.Button(records_window, text='Статистика',
                                         command=lambda: show_statistics(self.tree))
        statistics_btn.grid(row=0, column=4)

        # Кнопка для визуализации прогресса
        visualization_btn = ttk.Button(records_window, text='Визуализация прогресса',
                                            command=lambda: show_progress(self.tree))
        visualization_btn.grid(row=1, column=4)

        # Виджет Treeview для отображения записей
        self.tree = ttk.Treeview(records_window, columns=("Дата", "Упражнение", "Вес", "Повторения"), show="headings")
        self.tree.heading('Дата', text="Дата")
        self.tree.heading('Упражнение', text="Упражнение")
        self.tree.heading('Вес', text="Вес")
        self.tree.heading('Повторения', text="Повторения")

        self.tree.grid(row=4, column=0, columnspan=4)

        # Добавляем записи в Treeview
        for entry in data:
            self.tree.insert('', tk.END,
                             values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions']))

        if self.tree is None:
            pass
        else:
            self.csv_export_btn

        if self.tree is None:
            pass
        else:
            self.csv_import_btn



# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingLogApp(root)
    root.mainloop()
