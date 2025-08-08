import logging
import os
from datetime import timedelta

from scheduler import Scheduler, logger

API_KEY = "nyk_v0_kegVjjGDumB1mOrLe5cVqaL83GUrUWoDrQeKYIe3dGh6CdZNSb7QHyuFVXace5ou"
GRANT_ID = "01a0f7ec-6556-4e3b-9f12-4698a449f291"
cals = {
    "cal_schedule": "48F1FF95-FCD9-4EF1-B76E-58BEA8C5C551",
    "cal_health": "F7626466-4AF9-4131-BB23-84A02F1DE156",
    "cal_personal": "home",
    "cal_hobbies": "376992DD-3FE9-4695-AB18-2BC7B6BC1700",
    "cal_professional": "CB584A93-5F47-4015-9AEA-8B40476F5510",
    "cal_family": "D0B08AC5-1BF3-4568-AFAC-B4EE51E37E71",
    "test": "A7B4ACD3-A67D-4F47-A13F-11906297AAED",
}

home = os.environ.get("HOME")
morning = os.environ.get("MORNING")
repeat = os.environ.get("REPEAT")
home = bool(int(home)) if home is not None else False
morning = bool(int(morning)) if morning is not None else False
repeat = bool(int(repeat)) if repeat is not None else False
logger.log(logging.INFO, f"Home: {home}, Morning: {morning}, Repeat: {repeat}")

if __name__ == "__main__":
    scheduler = Scheduler(API_KEY, GRANT_ID, cals, home, repeat)

    # Утренняя рутина
    scheduler.create_routine(
        "cal_schedule",
        scheduler.wake_up,
        [
            ["Личная гигиена", timedelta(), timedelta(minutes=10)],
            ["Зарядка", timedelta(minutes=10), timedelta(minutes=30)],
            ["Медитация", timedelta(minutes=30), timedelta(minutes=45)],
            ["Работа с ежедневником", timedelta(
                minutes=45), timedelta(hours=1)],
            ["Завтрак", timedelta(hours=1), timedelta(hours=1, minutes=20)],
            [
                "Развиваю новые навыки",
                timedelta(hours=1, minutes=20),
                timedelta(hours=1, minutes=50),
            ],
        ],
        ends_before=timedelta(hours=8),
    )

    # Силовые тренировки
    if (
        scheduler.wake_up.weekday() == 0
        or scheduler.wake_up.weekday() == 2
        or scheduler.wake_up.weekday() == 4
    ):
        # Тренировка
        bias = None
        if scheduler.wake_up.weekday() == 0 or scheduler.wake_up.weekday() == 2:
            bias = timedelta(days=2)
        elif scheduler.wake_up.weekday() == 4:
            bias = timedelta(days=3)
        scheduler.create_routine(
            "cal_health",
            scheduler.wake_up,
            [["Full Body", timedelta(hours=2), timedelta(
                hours=3, minutes=15)]],
            recurrence="RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR",
            bias=bias,
        )
        # Рутина после тренировки
        scheduler.create_routine(
            "cal_schedule",
            scheduler.wake_up,
            [
                ["Душ", timedelta(hours=3, minutes=15),
                 timedelta(hours=3, minutes=30)],
                [
                    "Перекус",
                    timedelta(hours=3, minutes=30),
                    timedelta(hours=3, minutes=50),
                ],
            ],
            recurrence="RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR",
            bias=bias,
        )
    if not morning and scheduler.wake_up.hour > 8:
        # Время с Семьей
        if scheduler.wake_up.weekday() != 5 or scheduler.wake_up.weekday() != 6:
            bias = timedelta(days=1)
            if scheduler.wake_up.weekday() == 4:
                bias = timedelta(days=3)
            family_time = scheduler.shutdown - timedelta(hours=2)
            scheduler.create_routine(
                "cal_family",
                family_time,
                [["Время с Заей", timedelta(), timedelta(hours=2)]],
                bias=bias,
            )

        # Ужин
        dinner_time = scheduler.shutdown - timedelta(hours=1, minutes=30)
        scheduler.create_routine(
            "cal_schedule", dinner_time, [
                ["Ужин", timedelta(), timedelta(minutes=30)]]
        )

        # Обед
        lunch_time = (
            scheduler.wake_up
            + timedelta(hours=4)
            + (
                (
                    dinner_time
                    - timedelta(minutes=30)
                    - scheduler.wake_up
                    - timedelta(hours=4)
                )
                / 2
            )
        )
        scheduler.create_routine(
            "cal_schedule",
            lunch_time,
            [
                ["Обед", timedelta(), timedelta(minutes=30)],
                ["Разбираю «Входящие»", timedelta(
                    minutes=30), timedelta(hours=1)],
            ],
        )

        # Отход ко сну
        scheduler.create_routine(
            "cal_schedule",
            scheduler.shutdown,
            routine=[
                ["Личная гигиена", timedelta(), timedelta(minutes=10)],
                [
                    "Планирование следующего дня",
                    timedelta(minutes=10),
                    timedelta(minutes=30),
                ],
                ["Работа с ежедневником", timedelta(
                    minutes=30), timedelta(minutes=40)],
                ["Медитация", timedelta(minutes=40), timedelta(hours=1)],
            ],
            starts_after=timedelta(hours=16),
        )
