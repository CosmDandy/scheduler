import logging
from datetime import datetime, timedelta
from typing import Optional, Union

import pytz
from nylas import Client

logger = logging.getLogger("logger")
logger.setLevel(logging.DEBUG)

# Files
file_handler = logging.FileHandler("app.log", mode="a")
file_handler.setLevel(logging.DEBUG)

# Console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


class Calendar:
    """
    Класс, представляющий календарь
    """

    def __init__(self, calendar_id: str, timezone: str):
        self.calendar_id = calendar_id
        self.timezone = timezone


class Scheduler:
    """
    This class creates, deletes and updates events in calendar
    """

    def __init__(
        self,
        api_key: str,
        grant_id: str,
        calendars: dict,
        home: bool = True,
        repeat: bool = True,
    ):
        """
        Инициализирует объект класса, устанавливает подключение к API Nylas и настраивает параметры календаря.

        :param api_key: API ключ для подключения к Nylas Client.
        :param grant_id: Идентификатор гранта, используемый для аутентификации.
        :param calendars: Словарь с информацией о календарях, которые будут использоваться.

        :raises Exception: Генерирует исключение, если не удалось подключиться к Nylas Client.

        :attribute nylas: Экземпляр клиента Nylas, подключенного к API.
        :attribute grant_id: Идентификатор гранта, сохраненный для дальнейшего использования.
        :attribute calendars: Словарь календарей, переданный при инициализации.
        :attribute wake_up: Время "пробуждения", округленное до ближайших 5 минут от текущего времени.
        :attribute shutdown: Время завершения работы на основе времени пробуждения и логики смещения.
        """
        # API init
        try:
            self.nylas = Client(api_key=api_key, api_uri="https://api.eu.nylas.com")
            self.grant_id = grant_id
            self.repeat = repeat
        except Exception as e:
            logger.log(logging.ERROR, f"Connect to Nylas Client with error | {e}")
        else:
            logger.log(
                logging.INFO,
                f"Connect to Nylas Client | {self.nylas.applications.info()}",
            )

        # Calendars init
        self.calendars = calendars
        # Wake-up time
        tz_info = pytz.timezone("Europe/Moscow")
        if home:
            self.wake_up = datetime.now(tz=tz_info).replace(second=0) + timedelta(
                minutes=5
            )
        else:
            self.wake_up = datetime.now(tz=tz_info).replace(second=0) + timedelta(
                minutes=15
            )
        logger.log(logging.INFO, f"Init wake-up time: {self.wake_up.time()}")

        # Shutdown time
        if self.wake_up.hour > 8:
            self.shutdown = datetime(
                self.wake_up.year,
                self.wake_up.month,
                self.wake_up.day,
                20,
                0,
                0,
                tzinfo=tz_info,
            )
            if self.wake_up.hour < 12:
                bias = self.wake_up - timedelta(hours=8)
                bias = timedelta(minutes=int((bias.hour * 60 + bias.minute) / 2))
                self.shutdown += bias
            elif self.wake_up.hour >= 12:
                self.shutdown += timedelta(hours=2)
            logger.log(logging.INFO, f"Init shutdown time: {self.shutdown.time()}")

    def create_event(
        self,
        calendar: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        recurrence: Union[str, None] = None,
    ):
        """
        Создает новое событие в указанном календаре.

        :param calendar: Название календаря, в котором нужно создать событие.
        :param title: Заголовок события.
        :param start_time: Время начала события (объект datetime).
        :param end_time: Время окончания события (объект datetime).
        :param recurrence: Периодичность события (например, 'daily', 'weekly'). Если None, событие будет одноразовым.

        :raises Exception: Генерирует исключение в случае ошибки при создании события.

        :return: None. Логирует информацию о созданном событии или ошибке.
        """
        # The values to create the Event with
        event_request_body = {
            "title": title,
            "when": {
                "start_time": int(start_time.timestamp()),
                "end_time": int(end_time.timestamp()),
            },
            "reminders": {
                "use_default": False,
                "overrides": [{"reminder_minutes": 5, "reminder_method": "display"}],
            },
        }

        if recurrence:
            event_request_body.update({"recurrence": [recurrence]})

        # Query parameters
        event_query_params = {"calendar_id": self.calendars[calendar]}

        # Event create
        try:
            event = self.nylas.events.create(
                identifier=self.grant_id,
                request_body=event_request_body,
                query_params=event_query_params,
            )
        except Exception as e:
            logger.log(
                logging.ERROR,
                f"Error while creating event | calendar: {calendar}, title: {title}, start_time: {start_time}, end_time: {end_time}, recurrence: {recurrence}\n{e}",
            )
        else:
            logger.log(logging.INFO, f"Event created | {event}")

    def search_event(
        self, calendar: str, title: str, starts_after: datetime, ends_before: datetime
    ):
        """
        Ищет событие в указанном календаре по названию и временным рамкам.

        :param calendar: Название календаря, в котором осуществляется поиск.
        :param title: Название события, которое нужно найти.
        :param starts_after: Время начала поиска событий (объект datetime).
        :param ends_before: Время окончания поиска событий (объект datetime).

        :return: Найденное событие или None, если событие не найдено. Логирует результат поиска.

        :raises Exception: Генерирует исключение в случае ошибки при выполнении запроса поиска.
        """
        if not self.repeat:
            starts_after += timedelta(hours=(datetime.now() - timedelta(hours=5)).hour)
            ends_before += timedelta(hours=(datetime.now() - timedelta(hours=5)).hour)
        search_query_params = {
            "calendar_id": self.calendars[calendar],
            "start": int(starts_after.timestamp()),
            "end": int(ends_before.timestamp()),
            "title": title,
        }
        try:
            search = self.nylas.events.list(
                identifier=self.grant_id, query_params=search_query_params
            ).data
        except Exception as e:
            logger.log(
                logging.ERROR,
                f"Error while creating event | calendar: {calendar}, title: {title}, starts_after: {starts_after}, ends_before: {ends_before}\n{e}",
            )
        else:
            if search:
                logger.log(logging.INFO, f"Event successfully found | {search}")
                return search
            else:
                logger.log(logging.INFO, "Event does not exist")
                return None

    def delete_event(
        self,
        calendar: str,
        title: str,
        starts_after: datetime,
        ends_before: datetime,
        recurrence: str,
        bias: timedelta,
    ):
        """
        Удаляет событие из указанного календаря по названию и временным рамкам.

        :param calendar: Название календаря, из которого нужно удалить событие.
        :param title: Название события, которое нужно удалить.
        :param starts_after: Время начала поиска событий для удаления (объект datetime).
        :param ends_before: Время окончания поиска событий для удаления (объект datetime).
        :param recurrence: Периодичность события (например, 'daily', 'weekly'). Если None, событие будет одноразовым.
        :param bias: Смещение времени для создания нового события.

        :return: None. Логирует информацию об удаленном событии или ошибке.

        :raises Exception: Генерирует исключение в случае ошибки при удалении события.
        """
        event = self.search_event(calendar, title, starts_after, ends_before)
        if event:
            if self.repeat:
                self.create_event(
                    calendar=calendar,
                    title=event[0].title,
                    start_time=datetime.fromtimestamp(event[0].when.start_time) + bias,
                    end_time=datetime.fromtimestamp(event[0].when.end_time) + bias,
                    recurrence=recurrence,
                )
            try:
                self.nylas.events.destroy(
                    identifier=self.grant_id,
                    event_id=event[0].ical_uid,
                    query_params={"calendar_id": self.calendars[calendar]},
                )
            except Exception as e:
                logger.log(
                    logging.ERROR,
                    f"Error while removing event | calendar: {calendar}, title: {title}, starts_after: {starts_after}, ends_before: {ends_before}\n{e}",
                )
            else:
                logger.log(logging.INFO, f"Event removed | {event}")

    def create_routine(
        self,
        calendar: str,
        wake_up_time: datetime,
        routine: list,
        starts_after: Union[datetime, timedelta] = datetime.now().replace(
            hour=0, minute=0, second=0
        ),
        ends_before: Union[datetime, timedelta] = datetime.now().replace(
            hour=23, minute=59, second=59
        ),
        recurrence: str = "RRULE:FREQ=DAILY",
        bias: Optional[timedelta] = timedelta(days=1),
    ):
        """
        Создает новый ряд событий и смешает (удаляет и заново создает) старый в указанном календаре на основе заданного распорядка.

        :param calendar: Название календаря, в котором нужно создать или обновить события.
        :param wake_up_time: Время начала распорядка, от которого отсчитывается время каждого события.
        :param routine: Список событий для создания, где каждый элемент содержит название события, время начала и конца относительно времени пробуждения.
        :param starts_after: Время начала поиска существующих событий для удаления (может быть datetime или timedelta). По умолчанию – начало текущего дня.
        :param ends_before: Время окончания поиска существующих событий для удаления (может быть datetime или timedelta). По умолчанию – конец текущего дня.
        :param recurrence: Периодичность событий (например, 'daily', 'weekly'). По умолчанию – ежедневно. Нельзя использовать для одноразовых событи, так как тогда событие создасться с повтором.
        :param bias: Смещение времени для создания новых событий.

        :return: None. Логирует информацию о созданных или обновленных событиях, а также об ошибках.

        :raises Exception: Генерирует исключение в случае ошибки при создании или удалении события.
        """

        if isinstance(starts_after, timedelta):
            starts_after = (
                datetime.now().replace(hour=0, minute=0, second=0) + starts_after
            )
        if isinstance(ends_before, timedelta):
            ends_before = (
                datetime.now().replace(hour=0, minute=0, second=0) + ends_before
            )
        try:
            for title, start_time, end_time in routine:
                # Delete the event before creation
                start_time = wake_up_time + start_time
                end_time = wake_up_time + end_time
                try:
                    self.delete_event(
                        calendar, title, starts_after, ends_before, recurrence, bias
                    )
                    self.create_event(calendar, title, start_time, end_time)
                except Exception as e:
                    logger.log(
                        logging.ERROR,
                        f"Error in loop while create routine | calendar: {calendar}, title: {title}, start_time: {start_time}, end_time: {end_time}, starts_after: {starts_after}, ends_before: {ends_before}\n{e}",
                    )
        except Exception as e:
            logger.log(
                logging.ERROR,
                f"Error while create routine | calendar: {calendar}, starts_after: {starts_after}, ends_before: {ends_before}\n{e}",
            )
        else:
            logger.log(
                logging.INFO, f"Routine successfully created | calendar: {calendar}"
            )
