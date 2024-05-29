import os
import glob
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from kivy.core.audio import SoundLoader
from kivymd.uix.list import OneLineListItem, MDList, OneLineAvatarIconListItem, IRightBodyTouch, IconLeftWidget, \
    TwoLineListItem
from models import Base, TasksTerms, OverdueTasks
from libraries import DataBases, bot_config
import datetime
import main
import hashlib


class Methods:

    @staticmethod
    def to_hash(string):
        hash_object = hashlib.md5(string.encode())
        return str(hash_object.hexdigest())

    def add_to_list_view(
            self, screen_name, arr=None,
            task_name='', readable=False, is_scr=False,
            is_ren=False, is_main=False, list_item_only=False,
    ):

        if is_main:
            screen_name.list_name.text = 'All'
        if arr is None:
            arr = ['']
        if task_name != '':
            if DataBases.Methods.is_element_exists(self, base_name=TasksTerms, task_name=task_name):
                days_left = Methods.days_left(task_name)
                screen_name.list_view.add_widget(
                    main.TwoListitemsWithCheckBox(text=task_name, secondary_text=f'{days_left} days left',
                                                  on_press=screen_name.scr))
            else:
                screen_name.list_view.add_widget(main.ListItemWithCheckbox(text=task_name, on_press=screen_name.scr))
        else:
            if arr == ['']:
                with open(f'tasks.txt', 'r', encoding='utf-8') as file:
                    arr = file.read().split('\n')

            screen_name.list_view.clear_widgets()

            """Добавляем в list_view Задачу без подтекста если ее нет в базе данных и с подтекстом если есть"""
            for i in arr:
                if DataBases.Methods.is_element_exists(self, base_name=TasksTerms, task_name=str(i)):
                    days_left = Methods.days_left(i)
                    if Methods.check_date(i):
                        if readable:
                            Methods.delete(self, i, readable=True)
                        else:
                            Methods.delete(self, i)
                    else:
                        if is_scr:
                            screen_name.list_view.add_widget(main.OneLineListItem(text=i))
                        elif is_ren:
                            screen_name.list_view.add_widget(main.OneLineListItem(text=i, on_press=screen_name.change))
                        elif list_item_only:
                            screen_name.list_view.add_widget(main.ListItemWithCheckbox(text=i))
                        else:
                            screen_name.list_view.add_widget(main.TwoListitemsWithCheckBox(text=i, secondary_text=f'{days_left} days left', on_press=screen_name.scr))
                else:
                    if is_scr:
                        screen_name.list_view.add_widget(main.OneLineListItem(text=i))
                    elif is_ren:
                        screen_name.list_view.add_widget(main.OneLineListItem(text=i, on_press=screen_name.change))
                    elif list_item_only:
                        screen_name.list_view.add_widget(main.ListItemWithCheckbox(text=i))
                    else:
                        screen_name.list_view.add_widget(main.ListItemWithCheckbox(text=i, on_press=screen_name.scr))

    def delete(self, task_name, readable=False):

        DataBases.Methods.add(self, task_name, OverdueTasks)

        with open('completed.txt', 'a', encoding='utf-8') as file:
            file.writelines(task_name + '\n')

        with open('tasks.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')  # Добавление заданий в список

        # Удаляем текст элемента, в котором находится иконка
        for element in range(0, len(arr) - 1):
            try:
                if arr[element] == task_name:
                    arr.pop(element)
            except IndexError:
                print('index error')

        """Перезапись файла с заданиями новым списком"""
        with open('tasks.txt', 'w', encoding='utf-8') as file:
            for element in arr:
                file.write(f'{element}\n')

        """Удаление enter'ов из файла"""
        f = open('tasks.txt', 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()
        f = open("tasks.txt", "w", encoding='utf-8')
        for line in lines:
            if line != '\n':
                f.write(line)  # Записываем все значения файла, но без enter
        f.close()

        path_to_folder = os.path.abspath('lists/')  # Получаем абсолютный путь до папки lists
        matching_files = glob.glob(path_to_folder + "/*.txt")  # Получаем список элементов с форматом .txt
        txt_files = list()  # список, где будут хранится все списки
        for matching_file in matching_files:  # проходим циклом по списку с путями файлов
            txt_files.append(matching_file.split('\\')[-1])  # добавлям в список последний элемент(Название файла)
        print(txt_files)

        for txt_file in txt_files:  # Проходим по названию файлов
            with open(f'lists/{txt_file}', 'r', encoding='utf-8') as file:  # открываем файл
                arr = file.read().split('\n')
                try:
                    arr.remove(task_name)  # удаляем элемент, который нужно удалить из списка
                except ValueError:
                    print('Объект не в списке')
            print(arr)

            with open(f'lists/{txt_file}', 'w', encoding='utf-8') as file:
                for element in arr:
                    file.write(element + '\n')

        if DataBases.Methods.is_element_exists(self, OverdueTasks, task_name):
            DataBases.Methods.remove_element(self, TasksTerms, task_name)

        if not readable:
            completed_tasks = main.ToDoListApp.get_running_app().root.get_screen('completed_screen')
            completed_tasks.list_view.add_widget(OneLineListItem(text=task_name, theme_text_color="Custom", text_color=(1, 0, 0)))


    def delete_task(self, screen_name, instance, activated=False):
        # print(instance.parent.parent.text)
        if not activated:
            sound = SoundLoader.load('statics/sounds/Remove.wav')
            sound.play()  # Звук удаления задачи
        print(self.text)

        """Считывание данных с файла tasks. txt, чтобы получить список всех заданий"""

        with open('tasks.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')  # Добавление заданий в список

        # Удаляем текст элемента, в котором находится иконка
        for element in range(0, len(arr) - 1):
            try:
                if arr[element] == self.text:
                    arr.pop(element)
            except IndexError:
                print('index error')

        """Перезапись файла с заданиями новым списком"""
        with open('tasks.txt', 'w', encoding='utf-8') as file:
            for element in arr:
                file.write(f'{element}\n')

        """Удаление enter'ов из файла"""
        f = open('tasks.txt', 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()
        f = open("tasks.txt", "w", encoding='utf-8')
        for line in lines:
            if line != '\n':
                f.write(line)  # Записываем все значения файла, но без enter
        f.close()

        """Отображение """
        sv = open('tasks.txt', 'r', encoding='utf-8')
        arr = sv.read().split('\n')
        sv.close()
        screen_name.list_view.clear_widgets()  # Очищаем list_view у главного меню
        for i in range(len(arr)):
            # Добавляем элементы в list_view у главного меню
            screen_name.list_view.add_widget(main.ListItemWithCheckbox(text=arr[i], on_press=screen_name.scr))


        """Удаление задачи из списков"""
        path_to_folder = os.path.abspath('lists/')  # Получаем абсолютный путь до папки lists
        matching_files = glob.glob(path_to_folder + "/*.txt")  # Получаем список элементов с форматом .txt
        txt_files = list()  # список, где будут хранится все списки
        for matching_file in matching_files:  # проходим циклом по списку с путями файлов
            txt_files.append(matching_file.split('\\')[-1])  # добавлям в список последний элемент(Название файла)
        print(txt_files)

        for txt_file in txt_files:  # Проходим по названию файлов
            with open(f'lists/{txt_file}', 'r', encoding='utf-8') as file:  # открываем файл
                arr = file.read().split('\n')
                try:
                    arr.remove(self.text)  # удаляем элемент, который нужно удалить из списка
                except ValueError:
                    print('Объект не в списке')
            print(arr)

            with open(f'lists/{txt_file}', 'w', encoding='utf-8') as file:
                for element in arr:
                    file.write(element + '\n')  # Перезаписываем файл, но уже без элемента

        with open('important.txt', 'r', encoding='utf-8') as importants:
            important = importants.read().split('\n')
        if self.text in important:
            important.remove(self.text)
        with open('important.txt', 'w', encoding='utf-8') as importants:
            for i in important:
                importants.writelines(i + '\n')
        important_screen = main.ToDoListApp.get_running_app().root.get_screen('important_tasks_screen')
        important_screen.list_view.clear_widgets()
        Methods.add_to_list_view(self, important_screen, arr=important)

    def activate_checkbox(self, checkbox, value):
        completed_tasks = main.ToDoListApp.get_running_app().root.get_screen('completed_screen')
        sound = SoundLoader.load('statics/sounds/Completed.wav')
        sound.play()  # Звук выполнения задачи
        print(self.text)
        if value:
            print("activated")
            with open('completed.txt', 'a', encoding='utf-8') as file:
                file.writelines(self.text + '\n')
            self.delete(instance=self.text, activated=True)
            DataBases.Methods.remove_element(self, TasksTerms, self.text)
            with open('completed.txt', 'r', encoding='utf-8') as file:
                arr = file.read().split('\n')

            completed_tasks.list_view.clear_widgets()
            for i in arr:
                if DataBases.Methods.is_element_exists(self, OverdueTasks, i):
                    completed_tasks.list_view.add_widget(
                        OneLineListItem(text=i, theme_text_color="Custom", text_color=(1, 0, 0)))
                else:
                    completed_tasks.list_view.add_widget(OneLineListItem(text=i))

        else:
            print("noneactivated")

    @staticmethod
    def days_left(base_info):
        if base_info == '':
            pass
        else:
            date = DataBases.Methods.get_date(TasksTerms, base_info)
            if date is None:
                pass
            else:
                date_now = datetime.datetime.now().date()
                appointed_date = [str(date.year), str(date.month), str(date.day)]
                appointed_date = datetime.date(int(appointed_date[0]), int(appointed_date[1]), int(appointed_date[2]))
                final_result = appointed_date - date_now
                return str(final_result).split()[0]

    @staticmethod
    def check_date(task_name):
        days_left = Methods.days_left(task_name)
        if days_left is None:
            pass
        else:
            if task_name == '':
                pass
            else:
                try:
                    if int(days_left) < 1:
                        return True
                    else:
                        print('heh')
                except ValueError:
                    if int(str(days_left).split(':')[0]) < 1:
                        return True

    @staticmethod
    def tasks_sort(tasks):
        return sorted(tasks)



    @staticmethod
    async def send_email(to_email, message):
        try:
            msg = MIMEMultipart()
            msg.attach(MIMEText(message, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com: 587')
            server.starttls()
            server.login(bot_config.from_email, bot_config.password)
            await server.sendmail(bot_config.from_email, to_email, msg.as_string())
            server.quit()
        except TypeError:
            pass

    @staticmethod
    def enter_delete(path: str) -> None:
        f = open(path, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()
        f = open(path, "w", encoding='utf-8')
        for line in lines:
            if line != '\n':
                f.write(line)  # Записываем все значения файла, но без enter
        f.close()