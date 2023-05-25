import http.client
import json
from urllib.parse import quote


def get_teacher_id_by_name(teacher_name: str) -> int:
    encoded_teacher_name = quote(teacher_name).replace(' ', '%20')
    server_address = 'ruz.spbstu.ru'
    request = f'https://ruz.spbstu.ru/api/v1/ruz/search/teachers?&q={encoded_teacher_name}'
    try:
        connection = http.client.HTTPSConnection(server_address)
        connection.request('GET', request)
        response = connection.getresponse()
        ans = response.read()
        connection.close()

        ans_dict = json.loads(ans)
        if ans_dict['teachers'][0]['full_name'].lower() == teacher_name.lower():
            return ans_dict['teachers'][0]['id']
        else:
            return -1
    except Exception as _ex:
        print(_ex)
        return -1


def get_teacher_schedule_dict(teacher_id: int, date: str):
    date = date.replace('.', '-')
    server_address = 'ruz.spbstu.ru'
    request = f'https://ruz.spbstu.ru/api/v1/ruz/teachers/{teacher_id}/scheduler?date={date}'

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


class Teacher__lesson:
    def __init__(
            self,
            subject: str,
            time_start: str,
            time_end: str,
            typeObj: str,
            teacher: str,
            groups: list,
            place: str
    ):
        self.subject = subject
        self.time_start = time_start
        self.time_end = time_end
        self.typeObj = typeObj
        self.teacher = teacher
        self.groups = groups
        self.place = place

    def __str__(self):
        subject_line = f'{self.subject} ({self.typeObj})'
        time_line = f'\U000023F0 {self.time_start}-{self.time_end}'
        teacher_line = f'\U0001F9D1 {self.teacher}'
        groups_line = f'\U0001F393 Группы: '
        for group in self.groups:
            groups_line += f'{group}, '
        groups_line = groups_line[:-2] + '.'
        place_line = f'\U0001F3EB {self.place}'

        lesson = f'{time_line} {subject_line}\n{teacher_line}\n{place_line}\n{groups_line}\n\n'

        return lesson


def teacher_lesson_from_dict(dict: dict, date: str) -> str:
    schedule = 'В этот день у преподавателя нет пар!'
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
                        groups = []
                        for group in lesson["groups"]:
                            groups.append(group["name"])
                    except:
                        groups = ["Юнлинги \U0001F608"]
                    try:
                        place = f'{lesson["auditories"][0]["building"]["name"]}, ауд. {lesson["auditories"][0]["name"]}'
                    except:
                        place = f"Звезда смерти \U0001F608"

                    lesson_str = Teacher__lesson(
                        subject=subject,
                        time_start=time_start,
                        time_end=time_end,
                        typeObj=typeObj,
                        teacher=teacher,
                        groups=groups,
                        place=place
                    )

                    schedule += str(lesson_str)

                break
    except:
        schedule = 'В этот день у преподавателя нет пар!'

    return schedule

