import tkinter as tk
from tkinter import ttk, Toplevel, messagebox
from datetime import datetime
import csv
from tkinter.filedialog import asksaveasfilename, askopenfilename
import matplotlib.pyplot as plt
from collections import defaultdict


def date_search(tree, search_date, data):
    # Используем переданный аргумент search_date
    # Удаляем строки из Treeview
    for child in tree.get_children():
        tree.delete(child)

    # Фильтруем записи по выбранной дате
    filtered_data = [entry for entry in data if entry['date'].startswith(search_date)]

    # Добавляем в Treeview только записи с выбранной датой
    if filtered_data:
        for entry in filtered_data:
            tree.insert(
                parent='',
                index=tk.END,
                values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions'])
            )
    else:
        messagebox.showinfo(title="Результаты поиска", message="Записи с выбранной датой не найдены.")


def exercises_search(tree, search_exercises, data):
    # Используем переданный аргумент search_date
    # Удаляем строки из Treeview
    for child in tree.get_children():
        tree.delete(child)

    # Фильтруем записи по выбранной дате
    filtered_exercises = [entry for entry in data if entry['exercise'].startswith(search_exercises)]

    # Добавляем в Treeview только записи с выбранной датой
    if filtered_exercises:
        for entry in filtered_exercises:
            tree.insert(
                parent='',
                index=tk.END,
                values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions'])
            )
    else:
        messagebox.showinfo(title="Результаты поиска", message="Записи с выбранным упражнением не найдены.")


data_CSV = 'training_log.csv'


def export_to_csv(tree):
    file_path = asksaveasfilename(defaultextension=".csv",
                                  filetypes=[("CSV файлы", "*.csv")],
                                  title="Сохранить как")
    if not file_path:
        return

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Упражнение", "Вес", "Повторения", "Дата"])
        for entry in tree:
            writer.writerow([entry['exercise'], entry['weight'], entry['reps'], entry['date']])
    messagebox.showinfo("Успех", f"Записи экспортированы в {file_path}")


def import_from_csv(tree):
    file_path = askopenfilename(filetypes=[("CSV файлы", "*.csv")], title="Открыть файл CSV")
    if not file_path:
        return
    with open(file_path, newline='') as f:
        reader = csv.DictReader(f)
        for entry in reader:
            entry = {
                'exercise': entry['Упражнение'],
                'weight': float(entry['Вес']),
                'reps': int(entry['Повторения']),
                'date': entry['Дата']
            }
            tree.append(entry)
    save_data(tree)

    messagebox.showinfo("Успех", "Данные импортированы из CSV!")


def edit_entry(tree):
    """Редактирование выбранной записи в Treeview."""
    # Получение выделенной строки
    selected_item = tree.selection()
    if not selected_item:
        tk.messagebox.showwarning("Ошибка", "Выберите запись для редактирования!")
        return

    # Получаем значение текущей строки
    item = tree.item(selected_item[0])
    current_values = item['values']  # Список значений строки

    # Создаем новое окно редактирования
    edit_window = tk.Toplevel()
    edit_window.title("Редактирование записи")

    # Виджеты для ввода новых данных
    tk.Label(edit_window, text="Дата:").grid(row=0, column=0, padx=10, pady=5, sticky='w')
    date_entry = ttk.Entry(edit_window)
    date_entry.insert(0, current_values[0])  # Заполняем текущее значение
    date_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(edit_window, text="Упражнение:").grid(row=1, column=0, padx=10, pady=5, sticky='w')
    exercise_entry = ttk.Entry(edit_window)
    exercise_entry.insert(0, current_values[1])
    exercise_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(edit_window, text="Вес:").grid(row=2, column=0, padx=10, pady=5, sticky='w')
    weight_entry = ttk.Entry(edit_window)
    weight_entry.insert(0, current_values[2])
    weight_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(edit_window, text="Повторения:").grid(row=3, column=0, padx=10, pady=5, sticky='w')
    repetitions_entry = ttk.Entry(edit_window)
    repetitions_entry.insert(0, current_values[3])
    repetitions_entry.grid(row=3, column=1, padx=10, pady=5)


    save_data = 'training_log.json'

    # Кнопка сохранения изменений
    def save_changes():
        # Считываем новые значения из текстовых полей
        new_values = {
            'date': date_entry.get(),
            'exercise': exercise_entry.get(),
            'weight': weight_entry.get(),
            'repetitions': repetitions_entry.get()
        }

        # Обновляем данные в Treeview
        tree.item(selected_item[0], values=tuple(new_values.values()))

        # Открываем файл и загружаем данные
        with open(save_data, 'r+', encoding='utf8') as f:
            data = json.load(f)

            # Находим нужную запись (пример: ищем по атрибуту date)
            for record in data:
                if record['date'] and record['repetitions'] and record['exercise'] and record['date']:
                    record['repetitions'] = new_values['repetitions']
                    record['weight'] = new_values['weight']
                    record['exercise'] = new_values['exercise']
                    record['date'] = new_values['date']
                    break
            else:
                # Если запись не найдена, вы можете выдать сообщение об ошибке
                tk.messagebox.showerror("Ошибка", "Запись для обновления не найдена!")
                return

            # Сохраняем изменения в файл
            f.seek(0)  # Перемещаемся в начало файла
            json.dump(data, f, indent=4, ensure_ascii=False)
            f.truncate()  # Удаляем остатки старых данных

        # Уведомление об успешном обновлении
        tk.messagebox.showinfo("Успех", "Запись успешно обновлена!")
        edit_window.destroy()

    save_btn = ttk.Button(edit_window, text="Сохранить", command=save_changes)
    save_btn.grid(row=4, column=0, columnspan=2, pady=10)

    # Кнопка закрытия окна
    cancel_btn = ttk.Button(edit_window, text="Отмена", command=edit_window.destroy)
    cancel_btn.grid(row=5, column=0, columnspan=2, pady=10)

    edit_window.grab_set()


def delete_record(tree):
    """Удаляет выбранную запись или записи из Treeview."""

    # Получение выделенных элементов
    selected_items = tree.selection()

    if not selected_items:
        tk.messagebox.showwarning("Ошибка", "Выберите запись для удаления!")
        return

    # Подтверждение удаления
    confirm = tk.messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную запись?")
    if not confirm:
        return

    # Удаляем выбранные записи
    for item in selected_items:
        tree.delete(item)

    tk.messagebox.showinfo("Успех", "Запись успешно удалена!")


def show_statistics(tree):
    # Считаем статистику по суммарному весу упражнений за месяц
    stats = defaultdict(lambda: defaultdict(int))

    # Извлекаем данные из Treeview
    tree_data = []
    for child in tree.get_children():
        item = tree.item(child)['values']  # Получаем значения
        tree_data.append({
            "date": item[0],  # Дата
            "exercise": item[1],  # Упражнение
            "weight": int(item[2]),  # Вес
            "repetitions": int(item[3]),  # Повторения
        })

    # Считаем статистику
    for entry in tree_data:
        try:
            date_only = entry['date'].split(' ')[0]  # Убираем время, если оно есть
            date_obj = datetime.strptime(date_only, '%Y-%m-%d')  # Преобразуем только дату
            month = date_obj.strftime('%Y-%m')  # Извлекаем данные за месяц
            stats[month][entry["exercise"]] += entry["weight"] * entry["repetitions"]
        except Exception as e:
            print(f"Ошибка обработки записи {entry}: {e}")

    # Формируем строку для отображения
    info = ""
    for month, exercises in stats.items():
        info += f"**Месяц {month}:**\n"
        for exercise, total_weight in exercises.items():
            info += f"  - {exercise}: {total_weight} кг.\n"

    # Отображаем статистику
    messagebox.showinfo("Статистика по упражнениям", info)


def show_progress(tree):
    # Графики изменений веса и повторений
    exercise_data = defaultdict(lambda: {'dates': [], 'weights': [], 'repetitions': []})

    # Извлечение всех записей из Treeview
    for row_id in tree.get_children():  # Получаем все элементы в Treeview
        entry = tree.item(row_id)['values']  # Извлекаем данные строки
        # Убедитесь, что формат данных в Treeview совпадает с вашими ожиданиями
        date = datetime.strptime(entry[0].split(' ')[0], '%Y-%m-%d')  # Первый столбец - дата
        exercise = entry[1]  # Второй столбец - упражнение
        weight = float(entry[2])  # Третий столбец - вес
        repetitions = int(entry[3])  # Четвёртый столбец - количество повторений

        # Добавляем данные в график
        exercise_data[exercise]['dates'].append(date)
        exercise_data[exercise]['weights'].append(weight)
        exercise_data[exercise]['repetitions'].append(repetitions)

    # Построение графиков
    for exercise, values in exercise_data.items():
        plt.figure(figsize=(10, 5))

        # График изменения веса
        plt.subplot(2, 1, 1)
        plt.plot(values['dates'], values['weights'], marker='o', label='Вес (кг)')
        plt.title(f"{exercise}: Изменение веса")
        plt.xlabel('Дата')
        plt.ylabel('Вес (кг)')
        plt.grid(True)
        plt.legend()

        # График изменения повторений
        plt.subplot(2, 1, 2)
        plt.plot(values['dates'], values['repetitions'], marker='o', color='orange', label='Повторения')
        plt.title(f"{exercise}: Изменение повторений")
        plt.xlabel('Дата')
        plt.ylabel('Повторения')
        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        plt.show()
