import flet as ft
import asyncio
import threading
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from scanner import scan_ports, validate_host, get_common_ports, banner_grab
from utils import (
    parse_ports, validate_ip_or_domain, resolve_hostname, 
    save_results_txt, save_results_json, get_port_description,
    format_time, get_status_color, create_summary
)


class PortScannerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Port Scanner X"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 900
        self.page.window_height = 900
        self.page.window_resizable = True
        
        # Состояние приложения
        self.is_scanning = False
        self.scan_results: List[Dict[str, Any]] = []
        self.current_host = ""
        self.total_ports = 0
        self.scanned_ports = 0
        
        # Элементы интерфейса
        self.host_input = None
        self.ports_input = None
        self.concurrency_slider = None
        self.timeout_input = None
        self.scan_button = None
        self.stop_button = None
        self.progress_bar = None
        self.progress_text = None
        self.results_table = None
        self.status_text = None
        self.save_txt_button = None
        self.save_json_button = None
        self.theme_button = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        # Заголовок
        title = ft.Text(
            "Port Scanner X",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.colors.PRIMARY
        )
        
        # Поле ввода хоста
        self.host_input = ft.TextField(
            label="IP-адрес или домен",
            hint_text="Например: 192.168.1.1 или google.com",
            width=300,
            value="127.0.0.1"
        )
        
        # Поле ввода портов
        self.ports_input = ft.TextField(
            label="Порты для сканирования",
            hint_text="Например: 20-80,443,8080 или 1-1024",
            width=300,
            value="20-80,443,8080"
        )
        
        # Кнопки быстрого выбора портов
        common_ports_button = ft.ElevatedButton(
            "Популярные порты",
            on_click=self.set_common_ports,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        all_ports_button = ft.ElevatedButton(
            "Все порты (1-65535)",
            on_click=self.set_all_ports,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        # Ползунок для одновременных соединений
        self.concurrency_slider = ft.Slider(
            min=50,
            max=1000,
            value=500,
            divisions=19,
            label="Одновременных соединений: {value}",
            width=300
        )
        
        # Поле таймаута
        self.timeout_input = ft.TextField(
            label="Таймаут (сек)",
            hint_text="10.0",
            width=120,
            value="10.0"
        )
        
        # Кнопки сканирования
        self.scan_button = ft.ElevatedButton(
            "Сканировать",
            icon=ft.icons.SEARCH,
            on_click=self.start_scan,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.colors.WHITE
            )
        )
        
        self.stop_button = ft.ElevatedButton(
            "Остановить",
            icon=ft.icons.STOP,
            on_click=self.stop_scan,
            disabled=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.colors.ERROR
            )
        )
        
        # Кнопка переключения темы
        self.theme_button = ft.IconButton(
            icon=ft.icons.DARK_MODE,
            on_click=self.toggle_theme,
            tooltip="Переключить тему"
        )
        
        # Прогресс-бар
        self.progress_bar = ft.ProgressBar(
            width=600,
            visible=False
        )
        
        self.progress_text = ft.Text(
            "",
            size=14,
            color=ft.colors.SECONDARY
        )
        
        # Таблица результатов
        self.results_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Порт")),
                ft.DataColumn(ft.Text("Статус")),
                ft.DataColumn(ft.Text("Время")),
                ft.DataColumn(ft.Text("Описание"))
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.OUTLINE),
            vertical_lines=ft.border.BorderSide(1, ft.colors.OUTLINE),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.OUTLINE)
        )
        
        # Кнопки сохранения
        self.save_txt_button = ft.ElevatedButton(
            "Сохранить TXT",
            icon=ft.icons.SAVE,
            on_click=self.save_txt,
            disabled=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        self.save_json_button = ft.ElevatedButton(
            "Сохранить JSON",
            icon=ft.icons.SAVE,
            on_click=self.save_json,
            disabled=True,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
        # Статус-строка
        self.status_text = ft.Text(
            "Готов к сканированию",
            size=12,
            color=ft.colors.SECONDARY
        )
        
        # Компоновка интерфейса
        self.page.add(
            ft.Container(
                content=ft.Column([
                    # Заголовок
                    ft.Row([
                        title,
                        ft.Container(expand=True),
                        self.theme_button
                    ]),
                    
                    ft.Divider(),
                    
                    # Форма ввода
                    ft.Row([
                        ft.Column([
                            self.host_input,
                            self.ports_input,
                            ft.Row([
                                common_ports_button,
                                all_ports_button
                            ])
                        ]),
                        ft.Container(width=20),
                        ft.Column([
                            ft.Text("Настройки сканирования:", 
                                   size=16, weight=ft.FontWeight.BOLD),
                            self.concurrency_slider,
                            self.timeout_input,
                            ft.Row([
                                self.scan_button,
                                self.stop_button
                            ])
                        ])
                    ]),
                    
                    ft.Divider(),
                    
                    # Прогресс
                    ft.Column([
                        self.progress_bar,
                        self.progress_text
                    ]),
                    
                    ft.Divider(),
                    
                    # Результаты
                    ft.Text("Результаты:", size=16, weight=ft.FontWeight.BOLD),
                    
                    ft.Container(
                        content=ft.Column([
                            self.results_table
                        ], scroll=ft.ScrollMode.ALWAYS),
                        height=300,
                        border=ft.border.all(1, ft.colors.OUTLINE)
                    ),
                    
                    # Кнопки сохранения
                    ft.Row([
                        self.save_txt_button,
                        self.save_json_button
                    ]),
                    
                    ft.Divider(),
                    
                    # Статус
                    self.status_text
                ]),
                padding=20
            )
        )
    
    def set_common_ports(self, e):
        """Установка популярных портов"""
        common_ports = get_common_ports()
        self.ports_input.value = ",".join(map(str, common_ports))
        self.page.update()
    
    def set_all_ports(self, e):
        """Установка всех портов"""
        self.ports_input.value = "1-65535"
        self.page.update()
    
    def toggle_theme(self, e):
        """Переключение темы"""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.icons.DARK_MODE
        self.page.update()
    
    def start_scan(self, e):
        """Начало сканирования"""
        # Валидация ввода
        host = self.host_input.value.strip()
        if not host:
            self.show_error("Введите IP-адрес или домен")
            return
        
        if not validate_ip_or_domain(host):
            self.show_error("Некорректный IP-адрес или домен")
            return
        
        try:
            ports = parse_ports(self.ports_input.value)
            if not ports:
                self.show_error("Не указаны порты для сканирования")
                return
        except ValueError as e:
            self.show_error(f"Ошибка в формате портов: {e}")
            return
        
        try:
            timeout = float(self.timeout_input.value)
            if timeout <= 0:
                raise ValueError("Таймаут должен быть положительным")
        except ValueError:
            self.show_error("Некорректный таймаут")
            return
        
        # Настройка интерфейса для сканирования
        self.is_scanning = True
        self.scan_results = []
        self.current_host = host
        self.total_ports = len(ports)
        self.scanned_ports = 0
        
        self.scan_button.disabled = True
        self.stop_button.disabled = False
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.save_txt_button.disabled = True
        self.save_json_button.disabled = True
        
        self.results_table.rows = []
        
        self.update_status("Начинаю сканирование...")
        self.page.update()
        
        # Запуск сканирования в отдельном потоке
        threading.Thread(
            target=self.run_scan_thread,
            args=(host, ports, int(self.concurrency_slider.value), timeout),
            daemon=True
        ).start()
    
    def run_scan_thread(self, host: str, ports: List[int], concurrency: int, timeout: float):
        """Запуск сканирования в отдельном потоке"""
        try:
            # Создаем новый event loop для потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем асинхронное сканирование
            results = loop.run_until_complete(
                scan_ports(
                    host, ports, concurrency, timeout,
                    progress_callback=self.update_progress
                )
            )
            
            # Обработка результатов
            self.process_results(results)
            
        except Exception as e:
            self.show_error(f"Ошибка при сканировании: {e}")
        finally:
            self.finish_scan()
    
    def update_progress(self):
        """Обновление прогресса"""
        if not self.is_scanning:
            return
        
        self.scanned_ports += 1
        progress = self.scanned_ports / self.total_ports
        
        if self.is_scanning:
            self.progress_bar.value = progress
            self.progress_text.value = f"Просканировано: {self.scanned_ports}/{self.total_ports}"
            self.page.update()
    
    def process_results(self, results: List[tuple]):
        """Обработка результатов сканирования"""
        self.scan_results = []
        
        for port, status, time_ms in results:
            result = {
                "port": port,
                "status": status,
                "time_ms": time_ms,
                "description": get_port_description(port)
            }
            self.scan_results.append(result)
        
        self.scan_results.sort(key=lambda x: x["port"])
        
        self.results_table.rows = []
        
        for result in self.scan_results:
            color = get_status_color(result["status"])
            time_str = format_time(result["time_ms"]) if result["time_ms"] else "N/A"
            
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(result["port"]))),
                    ft.DataCell(ft.Text(result["status"], color=color)),
                    ft.DataCell(ft.Text(time_str)),
                    ft.DataCell(ft.Text(result["description"]))
                ]
            )
            self.results_table.rows.append(row)
        
        self.page.update()
    
    def finish_scan(self):
        """Завершение сканирования"""
        self.is_scanning = False
        self.scan_button.disabled = False
        self.stop_button.disabled = True
        self.progress_bar.visible = False
        self.progress_text.value = ""

        if self.scan_results:
            self.save_txt_button.disabled = False
            self.save_json_button.disabled = False

            summary = create_summary(self.scan_results)
            self.update_status(
                f"Сканирование завершено. Открыто: {summary['open']}, "
                f"Закрыто: {summary['closed']}, Всего: {summary['total']}"
            )
        else:
            self.update_status("Сканирование завершено без результатов")

        self.page.update()

    
    def stop_scan(self, e):
        """Остановка сканирования"""
        self.is_scanning = False
        self.update_status("Сканирование остановлено пользователем")
        self.finish_scan()
    
    def save_txt(self, e):
        """Сохранение результатов в TXT"""
        if not self.scan_results:
            return
        
        filename = f"scan_results_{self.current_host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            save_results_txt(self.scan_results, filename, self.current_host)
            self.update_status(f"Результаты сохранены в {filename}")
        except Exception as e:
            self.show_error(f"Ошибка при сохранении: {e}")
    
    def save_json(self, e):
        """Сохранение результатов в JSON"""
        if not self.scan_results:
            return
        
        filename = f"scan_results_{self.current_host}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            save_results_json(self.scan_results, filename, self.current_host)
            self.update_status(f"Результаты сохранены в {filename}")
        except Exception as e:
            self.show_error(f"Ошибка при сохранении: {e}")
    
    def show_error(self, message: str):
        """Показать сообщение об ошибке"""
        def show_dialog():
            dialog = ft.AlertDialog(
                title=ft.Text("Ошибка"),
                content=ft.Text(message),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.close_dialog())
                ]
            )
            self.page.dialog = dialog
            self.page.open_dialog(dialog)
        
        self.page.run_thread_safe(show_dialog)
    
    def update_status(self, message: str):
        """Обновление статуса"""
        self.status_text.value = f"{datetime.now().strftime('%H:%M:%S')} - {message}"
        self.page.update()


def main(page: ft.Page):
    """Главная функция приложения"""
    app = PortScannerApp(page)


if __name__ == "__main__":
    ft.app(target=main)