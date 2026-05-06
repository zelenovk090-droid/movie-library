"""
Movie Library (Личная кинотека)
GUI-приложение для хранения информации о фильмах с фильтрацией и сохранением в JSON.
Автор: [Ваше Имя Фамилия]
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class MovieLibrary:
    """Основной класс приложения Movie Library."""

    DATA_FILE = "movies.json"
    GENRES = [
        "Боевик", "Комедия", "Драма", "Фантастика", "Ужасы",
        "Триллер", "Мелодрама", "Приключения", "Мультфильм",
        "Документальный", "Детектив", "Фэнтези", "Исторический"
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Movie Library (Личная кинотека)")
        self.root.geometry("850x600")
        self.root.resizable(True, True)

        self.movies = []
        self.load_data()

        self.create_widgets()
        self.update_table()

    def create_widgets(self):
        """Создание всех элементов интерфейса."""

        input_frame = ttk.LabelFrame(self.root, text="Добавление фильма", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Жанр:").grid(row=0, column=2, sticky="w", pady=2, padx=(20, 0))
        self.genre_combo = ttk.Combobox(input_frame, values=self.GENRES, width=18, state="readonly")
        self.genre_combo.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        self.genre_combo.set(self.GENRES[0])

        ttk.Label(input_frame, text="Год выпуска:").grid(row=1, column=0, sticky="w", pady=2)
        self.year_entry = ttk.Entry(input_frame, width=10)
        self.year_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Рейтинг (0-10):").grid(row=1, column=2, sticky="w", pady=2, padx=(20, 0))
        self.rating_entry = ttk.Entry(input_frame, width=10)
        self.rating_entry.grid(row=1, column=3, padx=5, pady=2, sticky="w")

        add_btn = ttk.Button(input_frame, text="Добавить фильм", command=self.add_movie)
        add_btn.grid(row=1, column=4, padx=10, pady=2)

        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="По жанру:").grid(row=0, column=0, sticky="w", pady=2)
        self.filter_genre_combo = ttk.Combobox(
            filter_frame,
            values=["Все"] + self.GENRES,
            width=18,
            state="readonly"
        )
        self.filter_genre_combo.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.filter_genre_combo.set("Все")
        self.filter_genre_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_movies())

        ttk.Label(filter_frame, text="По году:").grid(row=0, column=2, sticky="w", pady=2, padx=(20, 0))
        self.filter_year_entry = ttk.Entry(filter_frame, width=10)
        self.filter_year_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        self.filter_year_entry.bind("<KeyRelease>", lambda e: self.filter_movies())

        reset_btn = ttk.Button(filter_frame, text="Сбросить фильтры", command=self.reset_filters)
        reset_btn.grid(row=0, column=4, padx=10, pady=2)

        delete_btn = ttk.Button(filter_frame, text="Удалить выбранный", command=self.delete_movie)
        delete_btn.grid(row=0, column=5, padx=10, pady=2)

        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год выпуска")
        self.tree.heading("rating", text="Рейтинг")

        self.tree.column("title", width=300)
        self.tree.column("genre", width=150)
        self.tree.column("year", width=100)
        self.tree.column("rating", width=100)

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ttk.Label(self.root, text=f"Всего фильмов: {len(self.movies)}")
        self.status_label.pack(anchor="w", padx=10, pady=2)

    def add_movie(self):
        """Добавление нового фильма."""
        title = self.title_entry.get().strip()
        genre = self.genre_combo.get()
        year_str = self.year_entry.get().strip()
        rating_str = self.rating_entry.get().strip()

        if not title:
            messagebox.showerror("Ошибка", "Название фильма не может быть пустым!")
            return

        if not year_str:
            messagebox.showerror("Ошибка", "Укажите год выпуска!")
            return

        if not rating_str:
            messagebox.showerror("Ошибка", "Укажите рейтинг!")
            return

        try:
            year = int(year_str)
            current_year = datetime.now().year
            if year < 1888 or year > current_year + 5:
                messagebox.showerror("Ошибка",
                    f"Год выпуска должен быть от 1888 до {current_year + 5}!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Год выпуска должен быть целым числом!")
            return

        try:
            rating = float(rating_str.replace(",", "."))
            if rating < 0 or rating > 10:
                messagebox.showerror("Ошибка", "Рейтинг должен быть от 0 до 10!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть числом!")
            return

        for movie in self.movies:
            if movie["title"].lower() == title.lower() and movie["year"] == year:
                if not messagebox.askyesno("Предупреждение",
                    f"Фильм '{title}' ({year}) уже существует в библиотеке.\nДобавить ещё раз?"):
                    return

        self.movies.append({
            "title": title,
            "genre": genre,
            "year": year,
            "rating": round(rating, 1)
        })

        self.save_data()
        self.update_table()
        self.clear_inputs()
        messagebox.showinfo("Успех", f"Фильм '{title}' добавлен!")

    def delete_movie(self):
        """Удаление выбранного фильма."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите фильм для удаления!")
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        title = values[0]
        year = int(values[2])

        if messagebox.askyesno("Подтверждение", f"Удалить фильм '{title}' ({year})?"):
            self.movies = [m for m in self.movies
                          if not (m["title"] == title and m["year"] == year)]
            self.save_data()
            self.update_table()
            messagebox.showinfo("Успех", f"Фильм '{title}' удалён!")

    def filter_movies(self):
        """Фильтрация по жанру и году."""
        self.update_table()

    def reset_filters(self):
        """Сброс фильтров."""
        self.filter_genre_combo.set("Все")
        self.filter_year_entry.delete(0, tk.END)
        self.update_table()

    def clear_inputs(self):
        """Очистка полей ввода."""
        self.title_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.rating_entry.delete(0, tk.END)
        self.genre_combo.set(self.GENRES[0])

    def get_filtered_movies(self):
        """Получение отфильтрованного списка фильмов."""
        filtered = self.movies.copy()

        genre_filter = self.filter_genre_combo.get()
        if genre_filter and genre_filter != "Все":
            filtered = [m for m in filtered if m["genre"] == genre_filter]

        year_filter = self.filter_year_entry.get().strip()
        if year_filter:
            try:
                year = int(year_filter)
                filtered = [m for m in filtered if m["year"] == year]
            except ValueError:
                pass

        return filtered

    def update_table(self):
        """Обновление таблицы."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered = self.get_filtered_movies()
        for movie in filtered:
            self.tree.insert("", "end", values=(
                movie["title"],
                movie["genre"],
                movie["year"],
                movie["rating"]
            ))

        self.status_label.config(text=f"Всего фильмов: {len(self.movies)}")

    def load_data(self):
        """Загрузка данных из JSON."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                    self.movies = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.movies = []
                messagebox.showwarning("Предупреждение",
                    "Не удалось загрузить данные. Создана новая библиотека.")
        else:
            self.movies = []

    def save_data(self):
        """Сохранение данных в JSON."""
        try:
            with open(self.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.movies, f, ensure_ascii=False, indent=4)
        except IOError:
            messagebox.showerror("Ошибка", "Не удалось сохранить данные!")


if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibrary(root)
    root.mainloop()
