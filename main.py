from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, MDList, OneLineAvatarIconListItem, IRightBodyTouch, IconLeftWidget, \
    TwoLineListItem, TwoLineAvatarIconListItem
from kivy.properties import ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.selectioncontrol import MDCheckbox
import os
import glob

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from models import Base, TasksTerms, OverdueTasks, Users
from libraries import DataBases, ThisApp
import validate_email

engine = create_engine('sqlite:///ToDoList.db')
Session = sessionmaker(bind=engine)


"""
Финальные тесты закончили:
Андержанов Олег
Гуцуляк артём
05.12.2021(1:05 по мск)
"""


class ListItemWithCheckbox(OneLineAvatarIconListItem):
    """
    Это класс новых OneListItem с чекбоксом и иконкой удаления
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(IconLeftWidget(icon='delete', on_press=self.delete))

    def active(self, checkbox, value):
        ThisApp.Methods.activate_checkbox(self, checkbox, value)

    def delete(self, instance, activated=False):
        main_menu_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        ThisApp.Methods.delete_task(self, main_menu_screen, instance, activated)


class RightCheckbox(IRightBodyTouch, MDCheckbox):
    """
    Это класс чекбокса, который будет стоять справа
    """


class TwoListitemsWithCheckBox(TwoLineAvatarIconListItem):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(IconLeftWidget(icon='delete', on_press=self.delete))

    def active(self, checkbox, value):
        ThisApp.Methods.activate_checkbox(self, checkbox, value)

    def delete(self, instance, activated=False):
        main_menu_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        ThisApp.Methods.delete_task(self, main_menu_screen, instance, activated)


class MainMenuScreen(Screen):
    listBox = ObjectProperty()
    theme_changer = ObjectProperty()
    search_task = ObjectProperty()
    all_tasks = ObjectProperty()
    important_tasks = ObjectProperty()
    create_list = ObjectProperty()
    completed_tasks = ObjectProperty()
    list_name = ObjectProperty()
    sort = ObjectProperty()
    rename = ObjectProperty()
    add_button = ObjectProperty()
    scroll = ScrollView()
    list_view = MDList()

    def __init__(self, **kw):
        super().__init__(**kw)
        # self.all_tasks.line_color = 0.5, 0.5, 0.5
        self.all_tasks.text_color = 0.5, 0.5, 0.5
        self.current_profile = None
        self.taskRead()

    def shovNavBar(self):
        nav_bar = MDNavigationDrawer()
        nav_bar.set_state('open')

    def goToAddingTaskScreen(self):
        if self.list_name.text == 'All':
            ToDoListApp.get_running_app().root.current = 'adding_newTask_screen_for_all'
            print(DataBases.Methods.get_date(TasksTerms, 'hello'))
        else:
            ToDoListApp.get_running_app().root.current = 'adding_newTask_screen'

    def taskRead(self):

        ThisApp.Methods.add_to_list_view(self, self, readable=True)
        self.listBox.add_widget(self.list_view)

    def main_tasks(self):
        ThisApp.Methods.add_to_list_view(self, self, is_main=True)

    def scr(self, value):
        # self.manager.transition = FadeTransition()
        self.manager.current = 'goodbye_screen'
        check = 'not'
        goodbye_screen = ToDoListApp.get_running_app().root.get_screen('goodbye_screen')
        goodbye_screen.current_task = value
        with open('important.txt', 'r', encoding='utf-8') as important:
            arr = important.read().split('\n')
        if value.text in arr:
            goodbye_screen.check = check
            goodbye_screen.important.active = True
        else:
            goodbye_screen.check = 'non'
            goodbye_screen.important.active = False

    def binary_search(self, data: list,
                      letter: str) -> list:  # It's not a binary search function anymore. It was a couple updates ago, but no not :( Press F
        list_size = len(letter)
        res = list()
        for word in data:
            arr = list(word)
            arr = arr[0:list_size]
            check = list(letter)
            if arr == check:
                res.append(word)

        return res

    def search(self):
        if self.list_name.text == 'All':
            with open('tasks.txt', 'r', encoding='utf-8') as file:
                tasks = file.read().split('\n')

        elif self.list_name.text == 'Lists':
            with open('lists/lists.txt', 'r', encoding='utf-8') as file:
                tasks = file.read().split('\n')

        elif self.list_name.text == 'Completed':
            with open('completed.txt', 'r', encoding='utf-8') as file:
                tasks = file.read().split('\n')

        else:
            with open(f'lists/{self.list_name.text}.txt', 'r', encoding='utf-8') as file:
                tasks = file.read().split('\n')

        tasks.sort()
        tasks_lower = [string.lower() for string in tasks]

        find_task = self.binary_search(tasks_lower, self.search_task.text)
        print(find_task)

        if not find_task:
            self.search_task.text = 'No such task!'
        else:
            self.list_view.clear_widgets()
            ThisApp.Methods.add_to_list_view(self, arr=find_task, screen_name=self)

    def task_sort(self):
        main_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        with open('tasks.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')
        tasks = ThisApp.Methods.tasks_sort(arr)
        ThisApp.Methods.add_to_list_view(self, main_screen, arr=tasks)


class CreateNewList(Screen):
    newList = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

    def createList(self):
        if self.newList.text == '' or self.newList.text == ' ':
            self.newList.hint_text = 'Write the name of list'
        else:
            with open(f'lists/{self.newList.text}.txt', 'w+', encoding='utf-8') as file:
                pass
            with open(f'lists/lists.txt', 'a', encoding='utf-8') as lists:
                lists.writelines(f'{self.newList.text}\n')
            adding_task = ToDoListApp.get_running_app().root.get_screen('adding_newTask_screen_for_all')
            adding_task.reload()
            lists_of_lists = ToDoListApp.get_running_app().root.get_screen('lists_of_lists_screen')
            lists_of_lists.list_view.add_widget(OneLineListItem(text=self.newList.text, on_press=self.change))
            self.newList.text = ''
            ToDoListApp.get_running_app().root.current = 'lists_of_lists_screen'

    def change(self, instance):  # метод, который должен отрабатываться по нажатию на конкретный элемент

        main_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        main_screen.list_name.text = instance.text
        arr = list()
        ThisApp.Methods.enter_delete(f'lists/{instance.text}.txt')
        with open(f'lists/{instance.text}.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')
        main_screen.list_view.clear_widgets()
        for i in arr:
            main_screen.list_view.add_widget(ListItemWithCheckbox(text=i))
        ToDoListApp.get_running_app().root.current = 'main_menu_screen'


class ListOfListsScreen(Screen):
    listBox = ObjectProperty()
    scroll = ScrollView()
    list_view = MDList()
    search_task = ObjectProperty()
    list_name = ObjectProperty()
    all_lists = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.listRead()
        self.list_name.text = 'Lists'
        self.all_lists.line_color = 0.5, 0.5, 0.5
        self.all_lists.text_color = 0.5, 0.5, 0.5

    def change(self, instance):  # метод, который должен отрабатываться по нажатию на конкретный элемент

        main_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        main_screen.list_name.text = instance.text
        arr = list()
        ThisApp.Methods.enter_delete(f'lists/{instance.text}.txt')
        with open(f'lists/{instance.text}.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')
        if arr == ['']:
            arr = [' ']
        ThisApp.Methods.add_to_list_view(self, main_screen, arr)
        ToDoListApp.get_running_app().root.current = 'main_menu_screen'

    def listRead(self):
        """Удаление enter'ов из файла"""
        ThisApp.Methods.enter_delete('lists/lists.txt')

        sv = open('lists/lists.txt', 'r', encoding='utf-8')
        arr = sv.read().split('\n')
        sv.close()
        for i in range(1, len(arr)):
            self.list_view.add_widget(OneLineListItem(text=arr[i], on_press=self.change))

        self.scroll.add_widget(self.list_view)
        self.listBox.add_widget(self.scroll)

    def main_tasks(self):
        main_menu_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        main_menu_screen.list_name.text = 'All'
        ToDoListApp.get_running_app().root.current = 'main_menu_screen'

    def search(self):
        mainScreen = MainMenuScreen()
        # mainScreen.search()
        with open('tasks.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')
        tasks = ThisApp.Methods.tasks_sort(arr)
        ThisApp.Methods.add_to_list_view(self, self, arr=tasks, is_scr=True)

    def task_sort(self):
        main_screen = MainMenuScreen()
        main_screen.task_sort()

class AddingNewTaskScreenForAll(Screen):
    taskToTxt = ObjectProperty()
    listToTxt = ObjectProperty()
    dropdown = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload()

    def menu_callback(self, text_item):
        arr = text_item.split()[1]

        if(arr == "+CREATELIST"):
            ToDoListApp.get_running_app().root.current = "adding_new_list_for_all"
            self.menu.dismiss()
        else:
            self.listToTxt.text = arr
            self.menu.dismiss()
            self.listToTxt.text = arr

    def reload(self):
        with open('lists/lists.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')
        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"Item {i}": self.menu_callback(x)
            } for i in arr
        ]
        self.menu = MDDropdownMenu(
            caller=self.listToTxt,
            items=menu_items,
            width_mult=4,
        )

    def addTask(self):
        if not self.listToTxt.text:
            self.listToTxt.hint_text = 'Type a list name!'
        else:
            main_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
            lists_of_lists = ToDoListApp.get_running_app().root.get_screen('lists_of_lists_screen')
            task_text = str(self.taskToTxt.text)
            sv = open('tasks.txt', 'a', encoding='utf-8')
            sv.writelines(str(task_text) + '\n')
            sv.close()

            with open('lists/lists.txt', 'r', encoding='utf-8') as file:
                files = file.read().split('\n')

            """Если название списка уже присутствует в списке списков, то"""
            if self.listToTxt.text not in files:
                print('йохохо')
                file = open(f'lists/{self.listToTxt.text}.txt', 'a', encoding='utf-8')
                file.writelines(f'{self.taskToTxt.text}\n')
                file.close()

                with open(f'lists/lists.txt', 'a', encoding='utf-8') as lists:
                    lists.writelines(f'{self.listToTxt.text}\n')

                ThisApp.Methods.add_to_list_view(self, main_screen)

                self.taskToTxt.text = ''
                self.listToTxt.text = ''
                self.check_the_terms_button.active = False

                lists_of_lists.list_view.clear_widgets()

                with open(f'lists/lists.txt', 'r', encoding='utf-8') as file:
                    new_arr = file.read().split('\n')

                for i in new_arr[1:]:
                    lists_of_lists.list_view.add_widget(OneLineListItem(text=i, on_press=lists_of_lists.change))

                ToDoListApp.get_running_app().root.current = "main_menu_screen"

            # Если нет названия списка в файле списка, то
            else:
                file = open(f'lists/{self.listToTxt.text}.txt', 'a', encoding='utf-8')
                file.writelines(f'{self.taskToTxt.text}\n')
                file.close()

                ThisApp.Methods.add_to_list_view(self, main_screen)  # Добавление в ListView, если есть

                self.taskToTxt.text = ''
                self.listToTxt.text = ''
                self.check_the_terms_button.active = False

                with open(f'lists/lists.txt', 'r', encoding='utf-8') as file:
                    new_arr = file.read().split('\n')

                lists_of_lists.list_view.clear_widgets()

                for i in new_arr[1:]:
                    lists_of_lists.list_view.add_widget(OneLineListItem(text=i, on_press=lists_of_lists.change))

                ToDoListApp.get_running_app().root.current = "main_menu_screen"



    def change(self, instance):  # метод, который должен отрабатываться по нажатию на конкретный элемент

        main_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        main_screen.list_name.text = instance.text
        with open(f'lists/{instance.text}.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')
        main_screen.list_view.clear_widgets()
        for i in arr:
            main_screen.list_view.add_widget(ListItemWithCheckbox(text=i))
        ToDoListApp.get_running_app().root.current = 'main_menu_screen'

    """Реализация добавления сроков по нажатию на чекбокс"""

    def on_checkbox_active(self, checkbox, value):
        if value:  # Если чекбокс нажат
            picker = MDDatePicker()  # Создаем выборку даты
            picker.bind(on_save=self.get_date, on_cancel=self.on_cancel)  # Добавляем методы по нажатию кнопок(По
            # нажатию на Ок, вызывается метод get_date, по нажатю на cancel, вызывается метод on_cancel)
            picker.open()  # Показываем окно
        else:
            print('cancel')

    """Метод добавления данных в Бд"""

    def get_date(self, instance, value, date_range):
        print(value)
        date = str(value).split('-')  # конвертируем дату в массив
        date = [int(i) for i in date]  # Переделываем элемиенты в int
        print(date)

        """Добавление в БД"""

        DataBases.Methods.add(
            self, base_name=TasksTerms,
            task_name=self.taskToTxt.text,
            year=date[0],
            month=date[1], day=date[2]
        )

    def on_cancel(self, instance, value):
        self.check_the_terms_button.active = False
        print(value)


class AddingNewListForAll(Screen):
    newlists = ObjectProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def addlist(self):
        if self.newLists.text == '' or self.newLists.text == ' ':
            self.newLists.hint_text = 'Write the name of list'
        else:
            with open(f'lists/{self.newLists.text}.txt', 'w+', encoding='utf-8') as file:
                pass
            with open(f'lists/lists.txt', 'a', encoding='utf-8') as lists:
                lists.writelines(f'{self.newLists.text}\n')
            lists_of_lists = ToDoListApp.get_running_app().root.get_screen('lists_of_lists_screen')
            lists_of_lists.list_view.add_widget(OneLineListItem(text=self.newLists.text, on_press=self.change))
            adding_new_task = ToDoListApp.get_running_app().root.get_screen('adding_newTask_screen_for_all')
            adding_new_task.listToTxt.text = self.newLists.text
            ToDoListApp.get_running_app().root.current = 'adding_newTask_screen_for_all'
            ToDoListApp.get_running_app().root.current_screen.reload()
            ThisApp.Methods.enter_delete('lists/lists.txt')
            self.newLists.text = ''

    def change(self, instance):  # метод, который должен отрабатываться по нажатию на конкретный элемент

        main_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        main_screen.list_name.text = instance.text
        arr = list()
        with open(f'lists/{instance.text}.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')
        main_screen.list_view.clear_widgets()
        for i in arr:
            main_screen.list_view.add_widget(ListItemWithCheckbox(text=i))
        ToDoListApp.get_running_app().root.current = 'main_menu_screen'

class AddingNewTaskScreen(Screen):
    taskToTxt = ObjectProperty()
    addTaskButton = ObjectProperty()
    check_the_terms_button = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)

    def addTask(self):
        main_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')

        task_text = str(self.taskToTxt.text)
        sv = open('tasks.txt', 'a', encoding='utf-8')
        sv.writelines(str(task_text) + '\n')
        sv.close()
        file = open(f'lists/{main_screen.list_name.text}.txt', 'a', encoding='utf-8')
        file.writelines(str(task_text) + '\n')
        file.close()
        main_screen.list_view.clear_widgets()
        with open(f'lists/{main_screen.list_name.text}.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')
        main_screen.list_view.clear_widgets()
        # for i in arr:
        #     main_screen.list_view.add_widget(ListItemWithCheckbox(text=i, on_press=main_screen.scr))
        ThisApp.Methods.add_to_list_view(self, main_screen, arr=arr)  # Добавление в ListView, если есть

        self.check_the_terms_button.active = False
        self.taskToTxt.text = ''

        ToDoListApp.get_running_app().root.current = "main_menu_screen"

    def on_checkbox_active(self, checkbox, value):
        if value:  # Если чекбокс нажат
            picker = MDDatePicker()  # Создаем выборку даты
            picker.bind(on_save=self.get_date, on_cancel=self.on_cancel)  # Добавляем методы по нажатию кнопок(По
            # нажатию на Ок, вызывается метод get_date, по нажатю на cancel, вызывается метод on_cancel)
            picker.open()  # Показываем окно
        else:
            print('cancel')

    def get_date(self, instance, value, date_range):
        print(value)
        date = str(value).split('-')  # конвертируем дату в массив
        date = [int(i) for i in date]  # Переделываем элемиенты в int
        print(date)

        """Добавление в БД"""

        DataBases.Methods.add(
            self, base_name=TasksTerms,
            task_name=self.taskToTxt.text,
            year=date[0],
            month=date[1], day=date[2]
        )

    def on_cancel(self, instance, value):
        self.check_the_terms_button.active = False
        print(value)


class ImportantTaskScreen(Screen):
    listBox = ObjectProperty()
    theme_changer = ObjectProperty()
    search_task = ObjectProperty()
    all_tasks = ObjectProperty()
    important_tasks = ObjectProperty()
    create_list = ObjectProperty()
    completed_tasks = ObjectProperty()
    list_name = ObjectProperty()
    sort = ObjectProperty()
    rename = ObjectProperty()
    add_button = ObjectProperty()
    scroll = ScrollView()
    list_view = MDList()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.Important()

    def Important(self):
        """Удаление enter'ов из файла"""
        ThisApp.Methods.enter_delete('important.txt')

        sv = open('important.txt', 'r', encoding='utf-8')
        arr = sv.read().split('\n')
        sv.close()
        for i in range(len(arr)):
            self.list_view.add_widget(ListItemWithCheckbox(text=arr[i]))
        self.scroll.add_widget(self.list_view)
        self.listBox.add_widget(self.scroll)

    def binary_search(self, data: list,
                      letter: str) -> list:  # It's not a binary search function anymore. It was a couple updates ago, but no not :( Press F
        list_size = len(letter)
        res = list()
        for word in data:
            arr = list(word)
            arr = arr[0:list_size]
            check = list(letter)
            if arr == check:
                res.append(word)

        return res

    def search(self):
        ThisApp.Methods.enter_delete('important.txt')

        with open('important.txt', 'r', encoding='utf-8') as important:
            tasks = important.read().split('\n')
        tasks.sort()
        tasks_lower = [string.lower() for string in tasks]
        find_task = self.binary_search(tasks_lower, self.search_task.text)

        if not find_task:
            self.search_task.text = 'No such task!'
        else:
            self.list_view.clear_widgets()
            for i in find_task:
                self.list_view.add_widget(ListItemWithCheckbox(text=i))

    def scr(self):
        print('hey')

    def main_tasks(self):
        main = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        main.list_name.text = 'All'
        ToDoListApp.get_running_app().root.current = 'main_menu_screen'

    def task_sort(self):

        with open('important.txt', 'r', encoding='utf-8') as file:
            arr = file.read().split('\n')

        tasks = ThisApp.Methods.tasks_sort(arr)
        ThisApp.Methods.add_to_list_view(self, self, arr=tasks)


class ImportantOrCompletedTaskCheckScreen(Screen):
    important = ObjectProperty()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.current_task = None
        self.check = None

    def press(self):
        pass

    def checking(self):
        if self.important.active:
            with open('important.txt', 'r', encoding='utf-8') as important:
                arr = important.read().split('\n')
            if self.current_task.text in arr:
                print('Элемент в файле!')
                self.manager.current = 'main_menu_screen'
            else:
                self.manager.current = 'main_menu_screen'
                with open('important.txt', 'a', encoding='utf-8') as important:
                    important.writelines(f'{self.current_task.text}\n')
                important_screen = ToDoListApp.get_running_app().root.get_screen('important_tasks_screen')
                important_screen.list_view.clear_widgets()
                sv = open('important.txt', 'r', encoding='utf-8')
                arr = sv.read().split('\n')
                sv.close()
                ThisApp.Methods.add_to_list_view(self, screen_name=important_screen, arr=arr, list_item_only=True)
                self.important.active = False
        else:
            with open('important.txt', 'r', encoding='utf-8') as important:
                arr = important.read().split('\n')
            if self.current_task.text in arr:
                self.manager.current = 'main_menu_screen'
                important_screen = ToDoListApp.get_running_app().root.get_screen('important_tasks_screen')
                with open('important.txt', 'r', encoding='utf-8') as important:
                    arr = important.read().split('\n')
                arr.remove(self.current_task.text)
                with open('important.txt', 'w', encoding='utf-8') as important:
                    for i in arr:
                        important.writelines(i + '\n')
                important_screen.list_view.clear_widgets()

                with open('important.txt', 'r', encoding='utf-8') as important:
                    arr = important.read().split('\n')
                if arr == ['']:
                    arr = [' ']
                ThisApp.Methods.add_to_list_view(self, screen_name=important_screen, arr=arr, list_item_only=True)
            else:
                self.manager.current = 'main_menu_screen'


class ToDoListApp(MDApp):

    def __init__(self, **kw):
        super().__init__(**kw)
        Base.metadata.create_all(engine)
        self.session_one = list()
        self.session_two = list()
        self.flag = False

    def callback(self, *args):
        main_menu_screen = self.get_running_app().root.get_screen('main_menu_screen')
        with open('tasks.txt', 'r', encoding='utf-8') as tasks:
            arr = tasks.read().split('\n')

        with open('important.txt', 'r', encoding='utf-8') as importants:
            important = importants.read().split('\n')

        for i in arr:
            days_left = ThisApp.Methods.days_left(i)
            if days_left == '2' and not self.flag and main_menu_screen.current_profile is not None:
                if i in self.session_two:
                    pass
                elif i in self.session_one:
                    self.session_two.remove(i)
                else:
                    ThisApp.Methods.send_email(main_menu_screen.current_profile,
                                               f'Task "{i}" will be overdue in 2 days!')
                    self.session_two.append(i)
            elif days_left == '1' and not self.flag and main_menu_screen.current_profile is not None:
                if i in self.session_one:
                    pass
                elif i in self.session_two:
                    self.session_two.remove(i)
                else:
                    ThisApp.Methods.send_email(main_menu_screen.current_profile,
                                               f'Task "{i}" will be overdue tommorow!')
                    self.session_one.append(i)
            elif ThisApp.Methods.check_date(i):
                main_menu_screen.list_view.clear_widgets()
                ThisApp.Methods.delete(self, i)
                ThisApp.Methods.add_to_list_view(self, main_menu_screen)
                ThisApp.Methods.send_email(main_menu_screen.current_profile,
                                           f'You did not completed task "{i}" in time!')
                if i in self.session_two:
                    self.session_two.remove(i)
                elif i in self.session_one:
                    self.session_one.remove(i)
                if i in important:
                    important.remove(i)
                    with open('important.txt', 'w', encoding='utf-8') as importants:
                        for element in important:
                            importants.writelines(element + '\n')
                    important_screen = ToDoListApp.get_running_app().root.get_screen('important_tasks_screen')
                    important_screen.list_view.clear_widgets()
                    ThisApp.Methods.add_to_list_view(self, important_screen, arr=important)

            else:
                print('werjewf')

    def build(self):
        self.theme_cls.theme_style = "Dark"
        Window.size = (1300, 700)
        sm = ScreenManager()
        sm.add_widget(Registration(name='registration'))
        sm.add_widget(MainMenuScreen(name='main_menu_screen'))
        sm.add_widget(ImportantOrCompletedTaskCheckScreen(name='goodbye_screen'))
        sm.add_widget(AddingNewTaskScreen(name='adding_newTask_screen'))
        sm.add_widget(AddingNewTaskScreenForAll(name='adding_newTask_screen_for_all'))
        sm.add_widget(CreateNewList(name='create_new_list_screen'))
        sm.add_widget(ListOfListsScreen(name='lists_of_lists_screen'))
        sm.add_widget(RenameTaskScreen(name='1'))
        sm.add_widget(CompletedTaskScreen(name='completed_screen'))
        sm.add_widget(ImportantTaskScreen(name='important_tasks_screen'))
        sm.add_widget(AddingNewListForAll(name='adding_new_list_for_all'))
        Clock.schedule_interval(self.callback, 0.5)
        return sm


class RenameTaskScreen(Screen):
    new_name = ObjectProperty()

    def change_text(self):
        main_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
        list_of_lists = ToDoListApp.get_running_app().root.get_screen('lists_of_lists_screen')
        current = main_screen.list_name.text
        if os.path.exists("lists/" + main_screen.list_name.text + '.txt'):
            src = os.path.realpath("lists/" + main_screen.list_name.text + '.txt')
            os.rename('lists/' + main_screen.list_name.text + '.txt', 'lists/' + self.new_name.text + ".txt")

        with open('lists/lists.txt', 'r', encoding='utf-8') as lists:
            arr = lists.read().split('\n')

        for list_name in range(len(arr)):
            if arr[list_name] == current:
                arr[list_name] = self.new_name.text
        with open('lists/lists.txt', 'w', encoding='utf-8') as lists:
            for i in arr:
                lists.writelines(i + '\n')
        list_of_lists.list_view.clear_widgets()
        #ThisApp.Methods.add_to_list_view(self, list_of_lists, arr=arr, is_ren=True)
        for i in arr[1:]:
            list_of_lists.list_view.add_widget(OneLineListItem(text=i))
        self.manager.current = 'main_menu_screen'
        main_screen.list_name.text = f'{self.new_name.text}'
        self.new_name.text = ''
        adding_task = ToDoListApp.get_running_app().root.get_screen('adding_newTask_screen_for_all')
        adding_task.reload()


class CompletedTaskScreen(Screen):
    listBox = ObjectProperty()
    theme_changer = ObjectProperty()
    search_task = ObjectProperty()
    all_tasks = ObjectProperty()
    important_tasks = ObjectProperty()
    create_list = ObjectProperty()
    completed_tasks = ObjectProperty()
    list_name = ObjectProperty()
    sort = ObjectProperty()
    rename = ObjectProperty()
    add_button = ObjectProperty()
    scroll = ScrollView()
    list_view = MDList()

    def __init__(self, **kw):
        super().__init__(**kw)
        self.read_important()

    def read_important(self):
        sv = open('completed.txt', 'r', encoding='utf-8')
        arr = sv.read().split('\n')
        sv.close()
        for i in range(len(arr)):
            if DataBases.Methods.is_element_exists(self, OverdueTasks, arr[i]):
                self.list_view.add_widget(OneLineListItem(text=arr[i], theme_text_color="Custom", text_color=(1, 0, 0)))
            else:
                self.list_view.add_widget(OneLineListItem(text=arr[i]))
        self.listBox.add_widget(self.list_view)

    def search(self):

        main_screen = MainMenuScreen()
        with open(f'important.txt', 'r', encoding='utf-8') as file:
            tasks = file.read().split('\n')

        tasks.sort()
        find_task = main_screen.binary_search(tasks, self.search_task.text)
        print(find_task)

        if not find_task:
            self.search_task.text = 'No such task!'
        else:
            self.list_view.clear_widgets()
            #ThisApp.Methods.add_to_list_view(self, arr=find_task, screen_name=self)
            for i in find_task:
                self.list_view.add_widget(i)


    def switch(self):
        self.manager.current = ''


class Registration(Screen):
    login = ObjectProperty()
    pswrd = ObjectProperty()
    warning = ObjectProperty()

    # Метод вхождения в систему
    def sign_in(self):

        new_password = ThisApp.Methods.to_hash(self.pswrd.text)
        if not DataBases.Methods.is_user_exists(Users, self.login.text,
                                                new_password):  # Если пользователь не опеределен, то
            self.warning.text = 'Incorrect email or password'  # выводим надпись о неверных данных
        else:
            main_menu_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
            main_menu_screen.current_profile = self.login.text
            self.manager.current = 'main_menu_screen'  # Иначе переходим на начальный экран

    # Метод регистрации
    def register(self):

        if self.login.text == '' or self.pswrd.text == '' or not validate_email.validate_email(
                self.login.text):  # Если поля пустые, то выводим надпись о просьбе
            self.warning.text = 'Enter correct email/password'

        else:
            new_password = ThisApp.Methods.to_hash(self.pswrd.text)
            main_menu_screen = ToDoListApp.get_running_app().root.get_screen('main_menu_screen')
            main_menu_screen.current_profile = self.login.text
            DataBases.Methods.add_user(Users, self.login.text, new_password,
                                       self.pswrd.text)  # Иначе добавляем пользователя в бд
            ToDoListApp.get_running_app().root.current = 'main_menu_screen'  # Переходим на главный экран


if __name__ == '__main__':
    ToDoListApp().run()
