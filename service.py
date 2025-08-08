from nylas import Client


class CalendarService:
    """
    Абстрактный сервис для работы с календарём
    """

    def create_event(self, request_body, reminders, calendar_id):
        raise NotImplementedError

    def delete_event(self, event_id, calendar_id):
        raise NotImplementedError

    def search_events(self, query_params):
        raise NotImplementedError


class NylasService(CalendarService):
    """
    Реализация CalendarService для работы с API Nylas
    """

    def __init__(self, grant_id: str, api_key: str, api_uri: str):
        self.grant_id = grant_id
        self.client = Client(api_key, api_uri)

    def create_event(self, request_body, reminders, calendar_id):
        # TODO: добвить функицю которая будет составлять реквест для напоминаний события
        reminders_list = []
        if reminders:
            for minutes in reminders:
                reminders_list.append(
                    {
                        "reminder_minutes": minutes,
                        "reminder_method": "display",
                    }
                )

            request_body["reminders"] = {
                "use_default": False,
                "overrides": reminders_list,
            }
        else:
            request_body["reminders"] = {"use_default": True}
        return self.client.events.create(
            self.grant_id,
            request_body,
            {"notify_participants": False, "calendar_id": calendar_id},
        )

    def delete_event(self, event_id, calendar_id):
        return self.client.events.destroy(
            self.grant_id,
            event_id,
            {"notify_participants": False, "calendar_id": calendar_id},
        )

    def search_events(self, query_params):
        return self.client.events.list(self.grant_id, query_params)
