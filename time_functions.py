import datetime


# Получение сегодняшней и завтрашней даты
def get_tomorrow_date() -> str:
    tomorrow = (datetime.datetime.now() +
                datetime.timedelta(days=1)).strftime("%Y.%m.%d")
    return tomorrow


def get_today_date() -> str:
    today = datetime.datetime.now().strftime("%Y.%m.%d")
    return today


# Напоминалка
def delta_time(reminder_time: str) -> float:
    try:
        [year, month, day, hour, minute] = map(int, reminder_time.split('.'))
        delta = datetime.datetime(
            year, month, day, hour, minute) - datetime.datetime.now()
        return delta.total_seconds() - 10800
    except:
        return -1


# Получение даты через день и через неделю
def get_next_day_date(some_day: str) -> str:
    [year, month, day] = map(int, some_day.split('-'))
    next_day = (datetime.datetime(year, month, day) +
                datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    return next_day


def get_next_week_date() -> str:
    next_week = (datetime.datetime.now() +
                 datetime.timedelta(days=7)).strftime("%Y.%m.%d")
    return next_week


# Номер дня в неделе
def number_of_day_in_week(date_str: str) -> int:
    [year, month, day] = map(int, date_str.split('.'))
    date = datetime.date(year, month, day)
    return date.weekday() + 1


# Получение времени до 18:00
# Считаем относительно сервера
def get_six_oclock() -> int:
    today = datetime.datetime.now().strftime("%Y.%m.%d.%H.%M")
    [year, month, day, hour, minute] = map(int, today.split('.'))
    delta = datetime.datetime(year, month, day, 15, 0) - \
        datetime.datetime(year, month, day, hour, minute)
    if delta.total_seconds() >= 0:
        return delta.total_seconds()
    else:
        return 86400 + delta.total_seconds()
