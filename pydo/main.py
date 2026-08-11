import os
from datetime import date, datetime, time

import flet as ft

from model import Task
from reminders import ReminderLoop
from storage import load_tasks, save_tasks

APP_BG = "#2C2C2C"
APP_PANEL = "#612D53"
APP_ACCENT = "#853953"
APP_ACCENT_SOFT = "#A86576"
APP_TEXT = "#F3F4F4"
APP_MUTED = "#D7D4D2"
APP_CARD = "#3B2F35"
APP_CARD_DONE = "#2F2F2F"
APP_OVERDUE = "#B23A48"

TASKS_FILE = "tasks.json"

tasks: list[Task] = load_tasks(TASKS_FILE)


def task_border() -> ft.Border:
    side = ft.BorderSide(width=1, color="#5b3f4b")
    return ft.Border(left=side, top=side, right=side, bottom=side)


def register_fonts(page: ft.Page) -> None:
    base = os.path.dirname(__file__)
    regular = os.path.join(base, "Cream Cake.otf")
    bold = os.path.join(base, "Cream Cake Bold.otf")
    fonts = {}
    # missing font files used to render a blank grey page in v1 — guard against that here
    if os.path.exists(regular):
        fonts["Cream Cake"] = regular
    if os.path.exists(bold):
        fonts["Cream Cake Bold"] = bold
    page.fonts = fonts


def font(bold: bool = False) -> str | None:
    return "Cream Cake Bold" if bold else "Cream Cake"


def persist_tasks() -> None:
    save_tasks(tasks, filename=TASKS_FILE)


def as_date(value: datetime | date) -> date:
    return value.date() if isinstance(value, datetime) else value


def format_due(due: datetime) -> str:
    today = datetime.now().date()
    due_date = due.date()
    if due_date == today:
        return f"Сьогодні, {due.strftime('%H:%M')}"
    if due_date == date.fromordinal(today.toordinal() + 1):
        return f"Завтра, {due.strftime('%H:%M')}"
    return due.strftime("%d.%m.%Y, %H:%M")


class TodoApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.search_query = ""

        self.task_list = ft.Column(spacing=12, expand=True)
        self.search_field = ft.TextField(
            hint_text="Пошук завдань...",
            border_radius=14,
            filled=True,
            fill_color="#2F2F2F",
            border_color="#5b3f4b",
            text_size=14,
            color=APP_TEXT,
            text_style=ft.TextStyle(font_family=font()),
            hint_style=ft.TextStyle(color=APP_MUTED, font_family=font()),
            prefix_icon=ft.Icons.SEARCH,
            on_change=self.on_search_change,
            dense=True,
        )

        self.new_task_field = ft.TextField(
            hint_text="Що потрібно зробити?",
            border_radius=18,
            filled=True,
            fill_color="#2F2F2F",
            border_color="#5b3f4b",
            text_size=16,
            color=APP_TEXT,
            text_style=ft.TextStyle(font_family=font(), color=APP_TEXT),
            hint_style=ft.TextStyle(color=APP_MUTED, font_family=font()),
            on_submit=self.on_add_task,
        )

        self.pending_due: datetime | None = None
        self.due_label = ft.Text("Без нагадування", size=12, color=APP_MUTED, font_family=font())

        self.date_picker = ft.DatePicker(on_change=self.on_date_picked)
        self.time_picker = ft.TimePicker(on_change=self.on_time_picked)

        self.reminders_enabled = True
        self.reminder_interval = 20.0
        self.reminder_loop = ReminderLoop(tasks, on_fire=self.on_reminder_fired, interval=self.reminder_interval)

    # -- reminder callback (may run on a background thread) --
    def on_reminder_fired(self, task: Task) -> None:
        persist_tasks()
        self.render()
        self.page.show_dialog(
            ft.SnackBar(ft.Text(f"Нагадування: {task.desc}", font_family=font()), bgcolor=APP_ACCENT)
        )

    # -- due date/time picking --
    def open_date_picker(self, e: ft.ControlEvent) -> None:
        self.page.show_dialog(self.date_picker)

    def on_date_picked(self, e: ft.ControlEvent) -> None:
        if self.date_picker.value:
            picked = as_date(self.date_picker.value)
            existing_time = self.pending_due.time() if self.pending_due else time(9, 0)
            self.pending_due = datetime.combine(picked, existing_time)
            self.page.show_dialog(self.time_picker)

    def on_time_picked(self, e: ft.ControlEvent) -> None:
        if self.time_picker.value and self.pending_due:
            picked_time: time = self.time_picker.value
            self.pending_due = datetime.combine(self.pending_due.date(), picked_time)
            self.due_label.value = format_due(self.pending_due)
            self.due_label.color = APP_TEXT
            self.page.update()

    def clear_due(self, e: ft.ControlEvent) -> None:
        self.pending_due = None
        self.due_label.value = "Без нагадування"
        self.due_label.color = APP_MUTED
        self.page.update()

    # -- task CRUD --
    def on_add_task(self, e: ft.ControlEvent) -> None:
        text = self.new_task_field.value.strip() if self.new_task_field.value else ""
        if not text:
            self.new_task_field.error = "Спочатку напишіть щось"
            self.page.update()
            return

        self.new_task_field.error = None
        tasks.append(Task(desc=text, due=self.pending_due, status=False))
        self.new_task_field.value = ""
        self.pending_due = None
        self.due_label.value = "Без нагадування"
        self.due_label.color = APP_MUTED
        persist_tasks()
        self.render()

    def toggle_task(self, task: Task) -> None:
        task.toggle_completed()
        persist_tasks()
        self.render()

    def remove_task(self, task: Task) -> None:
        tasks.remove(task)
        persist_tasks()
        self.render()

    def on_search_change(self, e: ft.ControlEvent) -> None:
        self.search_query = (self.search_field.value or "").strip().lower()
        self.render()

    # -- settings --
    def open_settings(self, e: ft.ControlEvent) -> None:
        completed_count = sum(1 for t in tasks if t.status)

        reminders_switch = ft.Switch(
            label="Нагадування увімкнено",
            label_text_style=ft.TextStyle(color=APP_TEXT, font_family=font()),
            value=self.reminders_enabled,
            active_color=APP_ACCENT,
            on_change=self.on_toggle_reminders,
        )

        interval_dropdown = ft.Dropdown(
            label="Як часто перевіряти",
            value=str(int(self.reminder_interval)),
            options=[
                ft.DropdownOption(key="10", text="Кожні 10 сек"),
                ft.DropdownOption(key="20", text="Кожні 20 сек"),
                ft.DropdownOption(key="60", text="Кожну хвилину"),
                ft.DropdownOption(key="300", text="Кожні 5 хвилин"),
            ],
            border_color="#5b3f4b",
            color=APP_TEXT,
            bgcolor="#2F2F2F",
            on_select=self.on_change_interval,
        )

        clear_button = ft.TextButton(
            content=ft.Text(
                f"Очистити виконані ({completed_count})",
                color=APP_ACCENT_SOFT,
                font_family=font(),
            ),
            on_click=self.on_clear_completed,
        )

        dialog = ft.AlertDialog(
            bgcolor=APP_PANEL,
            title=ft.Text("Налаштування", color=APP_TEXT, font_family=font(bold=True), size=22),
            content=ft.Column(
                [reminders_switch, interval_dropdown, ft.Divider(color="#5b3f4b"), clear_button],
                tight=True,
                spacing=16,
            ),
            actions=[
                ft.TextButton(
                    content=ft.Text("Закрити", color=APP_TEXT, font_family=font()),
                    on_click=self.close_settings,
                )
            ],
        )
        self.page.show_dialog(dialog)

    def close_settings(self, e: ft.ControlEvent) -> None:
        self.page.pop_dialog()

    def on_toggle_reminders(self, e: ft.ControlEvent) -> None:
        self.reminders_enabled = e.control.value
        if self.reminders_enabled:
            self.reminder_loop.start()
        else:
            self.reminder_loop.stop()

    def on_change_interval(self, e: ft.ControlEvent) -> None:
        self.reminder_interval = float(e.control.value)
        self.reminder_loop.stop()
        self.reminder_loop.interval = self.reminder_interval
        if self.reminders_enabled:
            self.reminder_loop.start()

    def on_clear_completed(self, e: ft.ControlEvent) -> None:
        tasks[:] = [t for t in tasks if not t.status]
        persist_tasks()
        self.render()
        self.page.pop_dialog()

    # -- rendering --
    def build_task_card(self, task: Task) -> ft.Container:
        is_done = task.status
        overdue = task.is_overdue()

        label = ft.Text(
            task.desc,
            size=18,
            weight=ft.FontWeight.W_500,
            color=APP_TEXT if not is_done else APP_MUTED,
            no_wrap=False,
            text_align=ft.TextAlign.LEFT,
            font_family=font(),
            style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH if is_done else None),
        )

        due_row = None
        if task.due:
            due_row = ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.NOTIFICATIONS_ACTIVE if overdue else ft.Icons.SCHEDULE,
                        size=14,
                        color=APP_OVERDUE if overdue else APP_MUTED,
                    ),
                    ft.Text(
                        format_due(task.due),
                        size=12,
                        color=APP_OVERDUE if overdue else APP_MUTED,
                        font_family=font(),
                    ),
                ],
                spacing=4,
            )

        status_button = ft.Container(
            content=ft.Text(
                "○" if not is_done else "✓",
                size=24,
                color=APP_TEXT if not is_done else APP_ACCENT_SOFT,
                font_family=font(bold=True),
            ),
            on_click=lambda e, t=task: self.toggle_task(t),
            padding=0,
            alignment=ft.Alignment(0, 0),
            bgcolor="transparent",
        )

        delete_button = ft.Container(
            content=ft.Text("✕", size=18, color=APP_TEXT, font_family=font(bold=True)),
            on_click=lambda e, t=task: self.remove_task(t),
            padding=0,
            alignment=ft.Alignment(0, 0),
            bgcolor="transparent",
        )

        text_col = ft.Column([label] + ([due_row] if due_row else []), expand=True, spacing=4)

        row = ft.Row(
            controls=[status_button, text_col, delete_button],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            expand=True,
        )

        return ft.Container(
            content=row,
            padding=18,
            border_radius=18,
            bgcolor=APP_CARD if not is_done else APP_CARD_DONE,
            border=ft.Border(left=ft.BorderSide(3, APP_OVERDUE)) if overdue else None,
            animate_opacity=200,
        )

    def visible_tasks(self) -> list[Task]:
        if not self.search_query:
            return tasks
        return [t for t in tasks if self.search_query in t.desc.lower()]

    def render(self) -> None:
        self.task_list.controls.clear()
        visible = self.visible_tasks()

        if not tasks:
            self.task_list.controls.append(self.empty_state("Все виконано", "Додайте своє перше завдання і починайте."))
        elif not visible:
            self.task_list.controls.append(self.empty_state("Нічого не знайдено", "Спробуйте інший запит пошуку."))
        else:
            for task in visible:
                self.task_list.controls.append(self.build_task_card(task))

        self.page.update()

    def empty_state(self, title: str, subtitle: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon=ft.Icons.CHECK_CIRCLE_OUTLINE, color=APP_ACCENT, size=36),
                    ft.Text(title, size=22, weight=ft.FontWeight.NORMAL, color=APP_TEXT, font_family=font(bold=True)),
                    ft.Text(subtitle, color=APP_MUTED, font_family=font()),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=30,
            border_radius=20,
            bgcolor=APP_PANEL,
            border=task_border(),
        )

    def build(self) -> None:
        add_button = ft.Container(
            content=ft.Text("+", size=30, color=APP_TEXT, font_family=font(bold=True)),
            width=52,
            height=52,
            bgcolor=APP_ACCENT,
            border_radius=26,
            alignment=ft.Alignment(0, 0),
            on_click=self.on_add_task,
        )

        reminder_button = ft.Container(
            content=ft.Icon(ft.Icons.ALARM_ADD, color=APP_TEXT, size=22),
            width=52,
            height=52,
            bgcolor=APP_ACCENT_SOFT,
            border_radius=26,
            alignment=ft.Alignment(0, 0),
            on_click=self.open_date_picker,
        )

        due_chip = ft.Row(
            controls=[
                self.due_label,
                ft.Container(
                    content=ft.Text("очистити", size=12, color=APP_ACCENT_SOFT, font_family=font()),
                    on_click=self.clear_due,
                ),
            ],
            spacing=10,
        )

        settings_button = ft.Container(
            content=ft.Icon(ft.Icons.SETTINGS, color=APP_MUTED, size=22),
            width=40,
            height=40,
            border_radius=20,
            alignment=ft.Alignment(0, 0),
            on_click=self.open_settings,
        )

        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Text(
                                "ToRedo",
                                size=42,
                                weight=ft.FontWeight.NORMAL,
                                color=APP_TEXT,
                                font_family=font(bold=True),
                            ),
                            ft.Text("Маленькі кроки. Великі перемоги.", size=18, color=APP_MUTED, font_family=font()),
                        ],
                        spacing=2,
                    ),
                    settings_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=ft.Padding(0, 8, 0, 18),
        )

        input_row = ft.Row(
            controls=[
                ft.Container(content=self.new_task_field, expand=True),
                reminder_button,
                add_button,
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.END,
        )

        self.page.add(
            header,
            input_row,
            due_chip,
            ft.Container(content=self.search_field, padding=ft.Padding(0, 14, 0, 6)),
            self.task_list,
        )
        self.render()
        self.reminder_loop.start()


def main(page: ft.Page):
    register_fonts(page)
    page.title = "ToRedo"
    page.bgcolor = APP_BG
    page.padding = 24
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    app = TodoApp(page)
    app.build()


ft.run(main)