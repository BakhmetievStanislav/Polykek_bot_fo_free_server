from data_base import get_marked_subgects, get_user_data
from time_functions import number_of_day_in_week, get_today_date
from schedule_functions import get_lessons_for_two_weeks, list_of_lessons


def marked_subjects_in_two_weeks(user_name: str) -> list:
    group_number = get_user_data(user_name)[1]
    user_subjects = get_marked_subgects(user_name)
    dict = get_lessons_for_two_weeks(group_number)
    if dict == -1:
        return -1
    list1 = list_of_lessons(dict["current_week"], user_subjects)
    list2 = list_of_lessons(dict["next_week"], user_subjects)
    return (list1 + list2)


def remind_about_lessons(lessons: list) -> str:
    if lessons == -1:
        return -1
    message = f"Напоминаю \U0001F99D\n\n"
    today = number_of_day_in_week(get_today_date())
    for i, element in enumerate(lessons[today: today + 7]):
        if not element['lessons']:
            continue
        for lesson in element['lessons']:
            if lesson['days'] >= (i + 1):
                message += f"\U0001F4C6 {element['date']} \U0001F4C6\n{lesson['lesson']}"

    if message == f"Напоминаю \U0001F99D\n\n":
        return -1

    return message
