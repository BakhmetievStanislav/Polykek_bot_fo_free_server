import http.client
import json
from time_functions import get_next_week_date, get_today_date, get_next_day_date


def get_group_id_by_name(group_number: str) -> int:
    server_address = 'ruz.spbstu.ru'
    request = f'/api/v1/ruz/search/groups?&q={group_number}'

    try:
        connection = http.client.HTTPSConnection(server_address)
        connection.request('GET', request)
        response = connection.getresponse()
        ans = response.read()
        connection.close()

        ans_dict = json.loads(ans)

        if ans_dict['groups'][0]['name'] == group_number:
            return ans_dict['groups'][0]['id']
        else:
            return ans_dict['groups'][1]['id']
    except:
        return -1


def get_schedule_dict_by_id_and_date(group_id: int, date: str):
    date = date.replace('.', '-')
    server_address = 'ruz.spbstu.ru'
    request = f'https://ruz.spbstu.ru/api/v1/ruz/scheduler/{group_id}?date={date}'

    try:
        connection = http.client.HTTPSConnection(server_address)
        connection.request('GET', request)
        response = connection.getresponse()
        ans = response.read()
        connection.close()

        ans_dict = json.loads(ans)

        return ans_dict
    except:
        return -1


class Lesson:
    def __init__(
            self,
            subject: str,
            time_start: str,
            time_end: str,
            typeObj: str,
            teacher: str,
            place: str
    ):
        self.subject = subject
        self.time_start = time_start
        self.time_end = time_end
        self.typeObj = typeObj
        self.teacher = teacher
        self.place = place

    def __str__(self):
        subject_line = f'{self.subject} ({self.typeObj})'
        time_line = f'\U000023F0 {self.time_start}-{self.time_end}'
        teacher_line = f'\U0001F9D1 {self.teacher}'
        place_line = f'\U0001F3EB {self.place}'

        lesson = f'{time_line} {subject_line}\n{teacher_line}\n{place_line}\n\n'

        return lesson


def lesson_from_dict(dict: dict, date: str) -> str:
    schedule = 'В этот день вам не нужно идти на пары!'
    try:
        for day in dict["days"]:
            if date.split('.')[2] in day["date"].split('-')[2]:
                schedule = f'\U0001F4C6 {day["date"]} \U0001F4C6\n\n'
                for lesson in day["lessons"]:
                    try:
                        subject = lesson["subject"]
                    except:
                        subject = f"Изучение темной стороны силы \U0001F608"
                    try:
                        time_start = lesson["time_start"]
                        time_end = lesson["time_end"]
                    except:
                        time_start = f"\U0001F608 00:00"
                        time_end = f"23:59 \U0001F608"
                    try:
                        typeObj = lesson["typeObj"]["name"]
                    except:
                        typeObj = f"Что-то очень интересное \U0001F608"
                    try:
                        teacher = lesson["teachers"][0]["full_name"]
                    except:
                        teacher = f"Дарт-Вейдер \U0001F608"
                    try:
                        place = f'{lesson["auditories"][0]["building"]["name"]}, ауд. {lesson["auditories"][0]["name"]}'
                    except:
                        place = f"Звезда смерти \U0001F608"

                    lesson_str = Lesson(
                        subject=subject,
                        time_start=time_start,
                        time_end=time_end,
                        typeObj=typeObj,
                        teacher=teacher,
                        place=place
                    )

                    schedule += str(lesson_str)

                break
    except:
        schedule = 'В это день вам не нужно идти на пары!'

    return schedule


def get_lessons_for_two_weeks(group_number: str) -> dict:
    group_id = get_group_id_by_name(group_number)
    if group_id == -1:
        return -1
    current_week = get_today_date()
    next_week = get_next_week_date()
    lessons = {}
    current_week_lessons = get_schedule_dict_by_id_and_date(
        group_id, current_week)
    if current_week_lessons == -1:
        return -1
    lessons['current_week'] = current_week_lessons
    next_week_lessons = get_schedule_dict_by_id_and_date(
        group_id, next_week)
    if next_week_lessons == -1:
        return -1
    lessons['next_week'] = next_week_lessons
    return lessons


def list_of_lessons(dict: dict, user_subjects: dict) -> list:
    lessons_list = []
    current_day = dict["week"]["date_start"].replace('.', '-')
    for day in dict["days"]:
        if current_day == day["date"]:
            lessons_in_day = {"date": current_day, "lessons": []}
            for lesson in day["lessons"]:
                for element in user_subjects:
                    if (lesson["subject"] == element[0]) and (lesson["typeObj"]["name"] == element[1]):
                        subject = lesson["subject"]
                        try:
                            time_start = lesson["time_start"]
                            time_end = lesson["time_end"]
                        except:
                            time_start = f"\U0001F608 00:00"
                            time_end = f"23:59 \U0001F608"
                        typeObj = lesson["typeObj"]["name"]
                        try:
                            teacher = lesson["teachers"][0]["full_name"]
                        except:
                            teacher = f"Дарт-Вейдер \U0001F608"
                        try:
                            place = f'{lesson["auditories"][0]["building"]["name"]}, ауд. {lesson["auditories"][0]["name"]}'
                        except:
                            place = f"Звезда смерти \U0001F608"

                        lesson_str = Lesson(subject=subject,
                                            time_start=time_start,
                                            time_end=time_end,
                                            typeObj=typeObj,
                                            teacher=teacher,
                                            place=place)
                        lessons_in_day["lessons"].append(
                            {"days": element[2], "lesson": str(lesson_str)})

            lessons_list.append(lessons_in_day)
            current_day = get_next_day_date(current_day)
        else:
            while current_day != day["date"]:
                lessons_in_day = {"date": current_day, "lessons": []}
                current_day = get_next_day_date(current_day)
                lessons_list.append(lessons_in_day)

    for i in range(7 - len(lessons_list)):
        lessons_in_day = {"date": current_day, "lessons": []}
        current_day = get_next_day_date(current_day)
        lessons_list.append(lessons_in_day)

    return lessons_list

