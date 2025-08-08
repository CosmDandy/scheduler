from config import LoadConfig, LoadSchedule
from service import NylasService
from test import Scheduler

grant_id, api_key, api_uri = LoadConfig("./config/config.json").load()
client = NylasService(grant_id, api_key, api_uri)

# schedule = LoadSchedule("./config/schedule.json").load()
schedule = LoadSchedule("./config/test_schedule.json").load()

scheduler = Scheduler(client, schedule)
scheduler.create_routine()
