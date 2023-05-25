import telebot
from telebot import types
from Tokens import open_weather_token, telebot_token
from threading import Timer
from schedule_functions import get_group_id_by_name, get_schedule_dict_by_id_and_date, lesson_from_dict
from teacher_schedule_function import get_teacher_id_by_name, get_teacher_schedule_dict, teacher_lesson_from_dict
from weather_functions import get_weather
from time_functions import get_tomorrow_date, get_today_date, delta_time, get_six_oclock
from bot_phrases import phrases, content_types_phrases
from data_base import create_tables_in_db, add_new_user, change_group, change_city, is_user_in_db
from data_base import get_user_data, add_new_note, delete_note, get_all_notes
from data_base import marked_new_subgect, delete_marked_subgect, get_marked_subgects, get_all_users
from general_functions import marked_subjects_in_two_weeks, remind_about_lessons


def lessons_by_date(group_number, date):
    group_id = get_group_id_by_name(group_number)
    if group_id == -1:
        return f'Номер группы указан неверно \U0001F614!!!'
    else:
        schedule_dict = get_schedule_dict_by_id_and_date(group_id, date)
    if schedule_dict == -1:
        return f'Дата указана неверно \U0001F614!!!'
    else:
        schedule = lesson_from_dict(schedule_dict, date)

    return schedule


def lessons_reminder(user_name):
    delta_reminder_time = 86400
    timer = Timer(delta_reminder_time, send_remind_lessons, [user_name])
    timer.start()


def send_remind_message(user_name, reminder_time, reminder_text, flag=0):
    if flag == 1:
        remind_text = f"Напоминаю \U0001F99D\n{phrases['late']}\n({reminder_time})\n{reminder_text}"
    else:
        remind_text = f"Напоминаю \U0001F99D\n{reminder_text}"
    bot.send_message(user_name, remind_text, parse_mode='html')
    delete_note(user_name, reminder_time, reminder_text)


def send_remind_lessons(user_name):
    lessons_list = marked_subjects_in_two_weeks(user_name)
    message = remind_about_lessons(lessons_list)
    if message == -1:
        bot.send_message(user_name, phrases["сервер"], parse_mode='html')
    else:
        bot.send_message(user_name, message, parse_mode='html')
    lessons_reminder(user_name)


def remind_notes_after_server_shutdown(notes_data: list):
    for note in notes_data:
        delta_reminder_time = delta_time(note[0])
        reminder_text = note[1]
        user_name = note[2]
        if delta_reminder_time < 0:
            send_remind_message(user_name, note[0], reminder_text, 1)
        else:
            timer = Timer(delta_reminder_time,
                          send_remind_message, [user_name, note[0], reminder_text])
            timer.start()


def remind_subjects_after_server_shutdown(all_users: list):
    for user in all_users:
        user_name = user[0]
        delta_reminder_time = get_six_oclock()
        timer = Timer(delta_reminder_time, send_remind_lessons, [user_name])
        timer.start()


def message_about_restart(all_users: list):
    for user in all_users:
        user_name = user[0]
        bot.send_message(user_name, phrases["restart"], parse_mode='html')


def remind_all_after_server_shutdown():
    notes_data = get_all_notes()
    all_users = get_all_users()
    message_about_restart(all_users)
    remind_notes_after_server_shutdown(notes_data)
    remind_subjects_after_server_shutdown(all_users)


# Сам бот
if __name__ == '__main__':
    bot = telebot.TeleBot(telebot_token)

    create_tables_in_db()
    remind_all_after_server_shutdown()

    @bot.message_handler(commands=['start'])
    def start(message):
        if not is_user_in_db(message.chat.id):
            mess = f"Привет, <i>{message.from_user.first_name}</i>! {phrases['register']}"
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True, row_width=1)
            reg = types.KeyboardButton('Регистрация')
            markup.add(reg)
            bot.send_message(message.chat.id, mess,
                             parse_mode='html', reply_markup=markup)
        else:
            bot.send_message(
                message.chat.id, f"{phrases['registered']}", parse_mode='html')
            main_menu(message)

    @bot.message_handler(commands=['help'])
    def help(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        start = types.KeyboardButton('/start')
        markup.add(start)
        bot.send_message(message.chat.id, phrases['help'], reply_markup=markup)

    @bot.message_handler(commands=['menu'])
    def menu(message):
        main_menu(message)

    @bot.message_handler(content_types=['text'])
    def get_user_text(message):
        message_text = message.text.lower()
        if message_text == 'привет':
            bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
        elif message_text == 'доброе утро':
            bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
            user_data = get_user_data(message.chat.id)
            if user_data:
                weather = get_weather(user_data[2], open_weather_token)
                bot.send_message(message.chat.id, weather, parse_mode='html')
                date = get_today_date()
                timetable = lessons_by_date(user_data[1], date)
                bot.send_message(message.chat.id, timetable, parse_mode='html')
            else:
                bot.send_message(
                    message.chat.id, phrases["сервер"], parse_mode='html')
        elif message_text == 'что ждет меня завтра':
            bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
            user_data = get_user_data(message.chat.id)
            if user_data:
                date = get_tomorrow_date()
                timetable = lessons_by_date(user_data[1], date)
                bot.send_message(message.chat.id, timetable, parse_mode='html')
            else:
                bot.send_message(
                    message.chat.id, phrases["сервер"], parse_mode='html')
        elif message_text == 'расписание':
            schedule(message)
        elif message_text == 'расписание по группе':
            msg = bot.send_message(
                message.chat.id, phrases['сменить группу'], parse_mode='html')
            bot.register_next_step_handler(msg, show_group_schedule)
        elif message_text == 'расписание преподавателя':
            msg = bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
            bot.register_next_step_handler(msg, show_teacher_schedule)
        elif message_text == 'мое расписание':
            msg = bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
            bot.register_next_step_handler(msg, bot_schedule)
        elif message_text == 'погода':
            bot_weather(message)
        elif message_text == 'погода в другом городе':
            msg = bot.send_message(
                message.chat.id, phrases['погода'], parse_mode='html')
            bot.register_next_step_handler(msg, other_city_weather)
        elif message_text == 'напоминание':
            msg = bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
            bot.register_next_step_handler(msg, remind)
        elif message_text == 'сменить группу':
            msg = bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
            bot.register_next_step_handler(msg, ch_group)
        elif message_text == 'creators':
            bot.send_message(
                message.chat.id, phrases['creators'], parse_mode='html')
        elif message_text == 'создатели':
            bot.send_message(
                message.chat.id, phrases['creators'], parse_mode='html')
        elif message_text == 'кто тебя создал?':
            bot.send_message(
                message.chat.id, phrases['creators'], parse_mode='html')
        elif message_text == 'еще':
            open_more_btns(message)
        elif message_text == 'помеченные предметы':
            open_marked_subjects_btns(message)
        elif message_text == 'пометить предмет':
            msg = bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
            bot.register_next_step_handler(msg, marking_subject)
        elif message_text == 'удалить предмет':
            msg = bot.send_message(
                message.chat.id, phrases[f"{message_text}"], parse_mode='html')
            bot.register_next_step_handler(msg, del_subject)
        elif message_text == 'ваш профиль':
            show_profile(message)
        elif message_text == 'сменить город':
            msg = bot.send_message(
                message.chat.id, phrases['погода'], parse_mode='html')
            bot.register_next_step_handler(msg, change_city_bot)
        elif message_text == 'показать отмеченные предметы':
            show_marked_subjects(message)
        elif message_text == 'назад':
            main_menu(message)
        elif message_text == 'регистрация':
            msg = bot.send_message(
                message.chat.id, phrases['моя группа'], parse_mode='html')
            bot.register_next_step_handler(msg, registration)
        elif message_text == '\U0001F99D':
            bot.send_sticker(
                message.chat.id, content_types_phrases['raccoon'])
        else:
            bot.send_message(
                message.chat.id, phrases["not understand"], parse_mode='html')

    def ch_group(message):
        group_number = message.text
        response = change_group(group_number, message.chat.id)
        if response:
            bot.send_message(
                message.chat.id, f'\U0001F393 Номер группы успешно изменен на {group_number}', parse_mode='html')
        else:
            bot.send_message(
                message.chat.id, phrases["сервер"], parse_mode='html')

    def bot_weather(message):
        bot.send_message(
            message.chat.id, phrases['weather wait'], parse_mode='html')
        city = get_user_data(message.chat.id)
        if city:
            weather = get_weather(city[2], open_weather_token)
            bot.send_message(message.chat.id, weather, parse_mode='html')
        else:
            bot.send_message(
                message.chat.id, phrases["сервер"], parse_mode='html')

    @bot.message_handler(func=lambda message: True)
    def remind(msg):
        reminder_text = msg.text.strip()
        user_name = msg.chat.id
        message = bot.send_message(
            msg.chat.id, phrases['when remind'], parse_mode='html')
        bot.register_next_step_handler(
            message, lambda message: reminder_by_time(message, user_name, reminder_text))

    def reminder_by_time(message, user_name, reminder_text):
        reminder_time = message.text.strip()
        delta_reminder_time = delta_time(reminder_time)
        if delta_reminder_time != -1:
            if delta_reminder_time < 0:
                reminder_text = f"{phrases['date passed']}Напоминаю \U0001F99D\n{reminder_text}"
            timer = Timer(delta_reminder_time,
                          send_remind_message, [user_name, reminder_time, reminder_text])
            timer.start()
            note = add_new_note(user_name, reminder_time, reminder_text)
            if note:
                bot.send_message(
                    user_name, phrases['will remind'], parse_mode='html')
            else:
                bot.send_message(
                    user_name, phrases["сервер"], parse_mode='html')
        else:
            bot.send_message(
                message.chat.id, phrases['date err'], parse_mode='html')

    def main_menu(message):
        mess = f'\U00002B07 Выбери необходимое действие \U00002B07'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        schedule_btn = types.KeyboardButton('Расписание')
        weather = types.KeyboardButton('Погода')
        reminder = types.KeyboardButton('Напоминание')
        morning = types.KeyboardButton('Доброе утро')
        tomorrow = types.KeyboardButton(
            'Что ждет меня завтра')
        more = types.KeyboardButton('Еще')
        markup.add(morning, weather, tomorrow, schedule_btn, reminder, more)
        bot.send_message(message.chat.id, mess, reply_markup=markup)

    def open_marked_subjects_btns(message):
        msg = '\U00002B07 Выберите необходимое действие \U00002B07'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        mark_subject = types.KeyboardButton('Пометить предмет')
        delete_subject = types.KeyboardButton('Удалить предмет')
        back = types.KeyboardButton('Назад')
        marked_subjects = types.KeyboardButton(
            'Показать отмеченные предметы')
        markup.add(mark_subject, delete_subject, back, marked_subjects)
        bot.send_message(message.chat.id, msg, reply_markup=markup)

    @bot.message_handler(func=lambda message: True)
    def marking_subject(msg):
        lesson_name = msg.text
        bot.send_message(
            msg.chat.id, f'\U0001F4CC Вы ввели предмет: {lesson_name}', parse_mode='html')
        message = bot.send_message(
            msg.chat.id, phrases['typeObj'], parse_mode='html')
        bot.register_next_step_handler(
            message, lambda message: marking_subject_type(message, lesson_name))

    @bot.message_handler(func=lambda message: True)
    def marking_subject_type(msg, lesson_name):
        lesson_type = msg.text
        bot.send_message(
            msg.chat.id, f'\U0001F4CC Вы ввели тип предмета: {lesson_type}', parse_mode='html')
        message = bot.send_message(
            msg.chat.id, phrases['mark day'], parse_mode='html')
        bot.register_next_step_handler(
            message, lambda message: marking_subject_days(message, lesson_name, lesson_type))

    def marking_subject_days(message, lesson_name, lesson_type):
        days = message.text
        user_name = message.chat.id
        response = marked_new_subgect(
            user_name, lesson_name, lesson_type, days)
        if response:
            bot.send_message(
                message.chat.id, phrases['marked'], parse_mode='html')
        else:
            bot.send_message(
                message.chat.id, phrases["сервер"], parse_mode='html')

    @bot.message_handler(func=lambda message: True)
    def del_subject(msg):
        lesson_name = msg.text
        bot.send_message(
            msg.chat.id, f'\U0001F4CC Вы ввели предмет: {lesson_name}', parse_mode='html')
        message = bot.send_message(
            msg.chat.id, phrases['typeObj'], parse_mode='html')
        bot.register_next_step_handler(
            message, lambda message: del_subject_type(message, lesson_name))

    def del_subject_type(message, lesson_name):
        user_name = message.chat.id
        lesson_type = message.text
        response = delete_marked_subgect(user_name, lesson_name, lesson_type)
        if response:
            bot.send_message(message.chat.id, f'\U0001F5D1 Предмет: {lesson_name} ({lesson_type}) - был успешно удален',
                             parse_mode='html')
        else:
            bot.send_message(message.chat.id, phrases["сервер"] + " или данные были указаны неверно",
                             parse_mode='html')

    def schedule(message):
        msg = '\U00002B07 Выберите необходимый тип расписания \U00002B07'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        my_schedule = types.KeyboardButton('Мое расписание')
        group_schedule = types.KeyboardButton(
            'Расписание по группе')
        back = types.KeyboardButton(
            'Назад')
        teacher_schedule = types.KeyboardButton(
            'Расписание преподавателя')
        markup.add(my_schedule, group_schedule, back, teacher_schedule)
        bot.send_message(message.chat.id, msg, reply_markup=markup)

    def bot_schedule(message):
        bot.send_message(
            message.chat.id, phrases['schedule wait'], parse_mode='html')
        date = message.text
        group_number = get_user_data(message.chat.id)
        if group_number:
            timetable = lessons_by_date(group_number[1], date)
            bot.send_message(message.chat.id, timetable, parse_mode='html')
        else:
            bot.send_message(
                message.chat.id, phrases["сервер"], parse_mode='html')

    @bot.message_handler(func=lambda message: True)
    def show_group_schedule(msg):
        group_number = msg.text
        message = bot.send_message(
            msg.chat.id, phrases['мое расписание'], parse_mode='html')
        bot.register_next_step_handler(
            message, lambda message: show_group_schedule_by_date(message, group_number))

    def show_group_schedule_by_date(message, group_number):
        bot.send_message(
            message.chat.id, phrases['schedule wait'], parse_mode='html')
        date = message.text
        timetable = lessons_by_date(group_number, date)
        bot.send_message(message.chat.id, timetable, parse_mode='html')

    @bot.message_handler(func=lambda message: True)
    def show_teacher_schedule(msg):
        teacher = msg.text.strip()
        teacher_id = get_teacher_id_by_name(teacher)
        if teacher_id == -1:
            msg1 = bot.send_message(
                msg.chat.id, phrases['name err'], parse_mode='html')

        message = bot.send_message(
            msg.chat.id, phrases['мое расписание'], parse_mode='html')
        bot.register_next_step_handler(
            message, lambda message: show_teacher_schedule_by_date(message, teacher_id))

    def show_teacher_schedule_by_date(message, teacher_id):
        bot.send_message(
            message.chat.id, phrases['schedule wait'], parse_mode='html')
        date = message.text
        schedule_dict = get_teacher_schedule_dict(teacher_id, date)
        if schedule_dict == -1:
            schedule = f'Дата указана неверно \U0001F614!!!'
        else:
            schedule = teacher_lesson_from_dict(schedule_dict, date)

        bot.send_message(message.chat.id, schedule, parse_mode='html')

    def open_more_btns(message):
        mess = f'\U00002B07 Выбери необходимое действие \U00002B07'
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        weather_other_city = types.KeyboardButton(
            'Погода в другом городе')
        choose_group = types.KeyboardButton('Сменить группу')
        marked_subjects_btn = types.KeyboardButton(
            'Помеченные предметы')
        profile = types.KeyboardButton('Ваш профиль')
        changing_city = types.KeyboardButton('Сменить город')
        back = types.KeyboardButton(
            'Назад')
        markup.add(weather_other_city, profile, marked_subjects_btn,
                   choose_group, changing_city, back)
        bot.send_message(message.chat.id, mess, reply_markup=markup)

    def show_profile(message):
        user_data = get_user_data(message.chat.id)
        if user_data:
            mess = f"Привет, <i>{message.from_user.first_name}</i>!\n\U0001F3D9 Ваш город: {user_data[2]}\n\U0001F393 Ваша группа: {user_data[1]}"
            bot.send_message(message.chat.id, mess, parse_mode='html')
        else:
            bot.send_message(
                message.chat.id, phrases["сервер"], parse_mode='html')

    def change_city_bot(message):
        city = message.text
        response = change_city(city, message.chat.id)
        if response:
            bot.send_message(
                message.chat.id, f'\U00002714 Город успешно изменен на {city}', parse_mode='html')
        else:
            bot.send_message(
                message.chat.id, phrases["сервер"], parse_mode='html')

    def show_marked_subjects(message):
        user_name = message.chat.id
        marked_subgects = get_marked_subgects(user_name)
        if not marked_subgects:
            lessons = "\U0001F4D1 У вас нет отмеченных предметов или произошла ошибка на сервере"
            bot.send_message(
                message.chat.id, lessons, parse_mode='html')
        else:
            lessons = "\U0001F4D1 Вот ваши отмеченные предметы:\n"
            for subgect in marked_subgects:
                lessons += f"\U0001F4CC {subgect[0]} ({subgect[1]}) -> {subgect[2]}\n"
            bot.send_message(message.chat.id, lessons, parse_mode='html')

    def other_city_weather(message):
        city = message.text
        bot.send_message(
            message.chat.id, f'\U00002714 Вы ввели город {city}, скоро будет погода для него...', parse_mode='html')
        # bot_weather(message)
        weather = get_weather(city, open_weather_token)
        bot.send_message(message.chat.id, weather, parse_mode='html')

    @bot.message_handler(func=lambda message: True)
    def registration(msg):
        group_number = msg.text
        message = bot.send_message(
            msg.chat.id, f'\U00002714 Введите свой город', parse_mode='html')
        bot.register_next_step_handler(
            message, lambda message: registration_next_step(message, group_number))

    def registration_next_step(message, group_number):
        city = message.text
        user_id = message.chat.id
        add = add_new_user(user_id, group_number, city)
        if add:
            bot.send_message(
                message.chat.id, phrases['succ reg'], parse_mode='html')
            delta_reminder_time = get_six_oclock()
            timer = Timer(delta_reminder_time, send_remind_lessons, [user_id])
            timer.start()
        else:
            bot.send_message(
                message.chat.id, phrases["сервер"], parse_mode='html')

        main_menu(message)

    @bot.message_handler(content_types=['photo'])
    def get_user_photo(message):
        bot.send_message(
            message.chat.id, content_types_phrases["photo"], parse_mode='html')

    @bot.message_handler(content_types=['audio'])
    def get_user_photo(message):
        bot.send_message(
            message.chat.id, content_types_phrases["audio"], parse_mode='html')

    @bot.message_handler(content_types=['document'])
    def get_user_photo(message):
        bot.send_message(
            message.chat.id, content_types_phrases["document"], parse_mode='html')

    @bot.message_handler(content_types=['sticker'])
    def get_user_photo(message):
        bot.send_sticker(
            message.chat.id, content_types_phrases["sticker"])

    @bot.message_handler(content_types=['video'])
    def get_user_photo(message):
        bot.send_message(
            message.chat.id, content_types_phrases["video"], parse_mode='html')

    @bot.message_handler(content_types=['voice'])
    def get_user_photo(message):
        bot.send_message(
            message.chat.id, content_types_phrases["voice"], parse_mode='html')

    @bot.message_handler(content_types=['video_note'])
    def get_user_photo(message):
        bot.send_message(
            message.chat.id, content_types_phrases["video_note"], parse_mode='html')

    @bot.message_handler(content_types=['poll'])
    def get_user_photo(message):
        bot.send_message(
            message.chat.id, content_types_phrases["poll"], parse_mode='html')

    @bot.message_handler(content_types=['location'])
    def get_user_photo(message):
        bot.send_message(
            message.chat.id, content_types_phrases["location"], parse_mode='html')

    bot.polling(none_stop=True)
