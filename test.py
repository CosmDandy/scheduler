from service import NylasService
from config import LoadSchedule

import pytz
from datetime import datetime, timedelta, date, time


class Scheduler:
    """
    Класс для управления событиями в календаре
    """

    def __init__(self, service: NylasService, schedule: LoadSchedule):
        self.service = service
        self.schedule = schedule
        tz_info = pytz.timezone("Europe/Moscow")
        self.wake_up = datetime.now(tz=tz_info).replace(second=0) + timedelta(minutes=5)

    def calc_time(self, routine_title, event_time, event_duration, duration_offset):
        start_time, end_time = None, None
        edge_to_run = 10
        if routine_title == "Morning":
            start_time = self.wake_up + duration_offset
            end_time = start_time + event_duration
        elif self.wake_up.hour > edge_to_run and routine_title == "Day":
            # TODO: это просто заглушка которая ничего не меняет
            start_time = event_time
            end_time = start_time + event_duration
        elif self.wake_up.hour > edge_to_run and routine_title == "Evening":
            # TODO: это просто заглушка которая ничего не меняет
            start_time = event_time
            end_time = start_time + event_duration
        return [int(start_time.timestamp()), int(end_time.timestamp())]

    def create_routine(self):
        for calendar in self.schedule:
            # calendar_title = calendar["calendar_title"]
            calendar_id = calendar["calendar_id"]
            for routine in calendar["calendar_routine"]:
                routine_title = routine["title"]
                recurrence = routine["recurrence"]
                duration_offset = timedelta(minutes=0)
                for event in routine["schedule"]:
                    event_title = event["title"]
                    hour, minute = map(int, event["time"].split(":"))
                    event_time = datetime.combine(
                        date.today(), time(hour=hour, minute=minute)
                    )
                    event_duration = timedelta(minutes=event["duration"])
                    event_reminders = event["reminders"]
                    self.service.create_event(
                        {
                            "title": event_title,
                            "when": {
                                "start_time": int(event_time.timestamp()),
                                "end_time": int(
                                    (event_time + event_duration).timestamp()
                                ),
                            },
                            "recurrence": [recurrence],
                        },
                        event_reminders,
                        calendar_id,
                    )
