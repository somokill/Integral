import flet as ft
import g4f
import googletrans
import logging

logging.basicConfig(level=logging.WARNING, filename='integral_log.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s')
logging.getLogger("flet_core").setLevel(logging.WARNING)

tr = googletrans.Translator()
path = ''

def timemater(func):
    """Декоратор для измерения длительности выполнения функции"""
    def wrapper():
        t0 = __import__('time').perf_counter()
        func()
        t1 = __import__('time').perf_counter()
        took = t1 - t0
        print(took)
    return wrapper

def main(page: ft.Page):
    """Базовая функция окна
       page: объект страницы"""
    page.title = 'Integral'
    page.theme_mode = 'dark'
    page.theme = ft.theme.Theme(color_scheme_seed=ft.colors.BLUE)
    page.window_width = 1270
    page.window_height = 680
    page.window_resizable = True
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    def translate(e):
        """Перевод текста с русского на английский при нажатии на кнопку tr_button"""
        res = tr.translate(tr_text.value, src='ru', dest='en')
        tred_text.value = res.text
        page.update()

    def retranslate(e):
        """Перевод текста с английского на русский при нажатии на кнопку retr_button"""
        res = tr.translate(tred_text.value, src='en', dest='ru')
        tr_text.value = res.text
        page.update()

    def get_chatgpt_response(e):
        """Получение ответа от ChatGPT при нажатии на кнопку g4f_button"""
        g4f_answer.value = 'Please, wait...'
        page.update()

        response = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": g4f_prompt.value}],
        )

        g4f_answer.value = response
        page.update()

    def change_theme(e):
        """Изменение темы страницы с темной на светлую и обратно при нажатии на кнопку theme_button"""
        page.theme_mode = 'dark' if page.theme_mode == 'light' else 'light'
        theme_button.icon = ft.icons.WB_SUNNY_ROUNDED if page.theme_mode == 'light' else ft.icons.DARK_MODE_ROUNDED
        page.update()

    def change_colorscheme(e):
        """Изменение цветовой схемы страницы в соответствии с выбранной из списка color_drop"""
        color = ft.colors.BLUE
        match color_drop.value:
            case 'Deep purple':
                color = ft.colors.DEEP_PURPLE
            case 'Indigo':
                color = ft.colors.INDIGO
            case 'Blue (default)':
                color = ft.colors.BLUE
            case 'Teal':
                color = ft.colors.TEAL
            case 'Green':
                color = ft.colors.GREEN
            case 'Yellow':
                color = ft.colors.YELLOW
            case 'Orange':
                color = ft.colors.ORANGE
            case 'Deep orange':
                color = ft.colors.DEEP_ORANGE
            case 'Pink':
                color = ft.colors.PINK
        page.theme = ft.theme.Theme(color_scheme_seed=color)
        page.update()

    text_field = ft.TextField(label='File text', width=800, height=600, multiline=True, autofocus=True, min_lines=23, text_size=20) # Основное тесктовое поле для редактирования файла
    
    g4f_prompt = ft.TextField(label='ChatGPT', width=260)  # Поле для ввода промпта ChatGPT
    g4f_button = ft.ElevatedButton('Send', icon=ft.icons.SEND_ROUNDED, on_click=get_chatgpt_response) # Кнопка получения ответа от ChatGPT
    g4f_answer = ft.Text('This is ChatGPT answer...', width=380) # Текстовое поле с ответом ChatGPT

    tr_text = ft.TextField(label='ru', width=260) # Поле для ввода текста для перевода на русском
    tred_text = ft.TextField(label='eng', width=260)  # Поле для ввода текста для перевода на английском
    tr_button = ft.ElevatedButton('Translate', icon=ft.icons.G_TRANSLATE_ROUNDED, on_click=translate) # Кнопка перевода русский -> английский
    retr_button = ft.ElevatedButton('Retranslation', icon=ft.icons.COMPARE_ARROWS_ROUNDED, on_click=retranslate) # Кнопка перевода английский -> русский

    theme_button = ft.ElevatedButton('Change theme', icon=ft.icons.DARK_MODE_ROUNDED, on_click=change_theme) # Кнопка смены темы
    color_drop = ft.Dropdown(width=250, icon=ft.icons.COLOR_LENS_ROUNDED, options=[
        ft.dropdown.Option('Deep purple'),
        ft.dropdown.Option('Indigo'),
        ft.dropdown.Option('Blue (default)'),
        ft.dropdown.Option('Teal'),
        ft.dropdown.Option('Green'),
        ft.dropdown.Option('Yellow'),
        ft.dropdown.Option('Orange'),
        ft.dropdown.Option('Deep orange'),
        ft.dropdown.Option('Pink'),
    ], on_change=change_colorscheme) # Выпадающий список изменения цветовой схемы
    color_drop.value = 'Blue (default)'

    def pick_result(e: ft.FilePickerResultEvent):
        """Открытие FilePicker для выбора файлов по нажатию на кнопку Select file"""
        if not e.files:
            selected_files.value = 'Nothing selected'
            text_field.value = ''
        else:
            save_button.text = 'Save file'
            selected_files.value = ''
            global path
            for el in e.files:
                path = el.path

            selected_files.value = path
            f = open(path, 'r')
            text_field.value = f.read()
            f.close()

        page.update()

    def save_file(e):
        """Сохранение файла по нажатию на кнопку save_button"""
        global path
        f = open(path, 'w')
        f.write(text_field.value)
        f.close()

        save_button.text = 'File saved'
        page.update()

    pick_dialog = ft.FilePicker(on_result=pick_result) # FilePicker меню
    page.overlay.append(pick_dialog)
    selected_files = ft.Text() # путь к выбранному файлу
    save_button = ft.ElevatedButton('Save file', icon=ft.icons.SAVE_ROUNDED, on_click=save_file) # Кнопка сохранения файла

    page.add(
        ft.Row(
            [
                ft.ElevatedButton('Select file', icon=ft.icons.FILE_UPLOAD_ROUNDED,
                                  on_click=lambda _: pick_dialog.pick_files(allow_multiple=False)),
                save_button,
                selected_files
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND
        ),
        ft.Row(
            [
                text_field,
                ft.Column([
                    ft.Column([
                        ft.Row([theme_button, color_drop]),
                        ft.Row([tr_text, tr_button]),
                        ft.Row([tred_text, retr_button]), ]),
                    ft.Row([g4f_prompt, g4f_button]),
                    g4f_answer])
            ]
        )
    )


ft.app(target=main) # Запуск программы
