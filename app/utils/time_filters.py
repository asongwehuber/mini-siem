from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


CAMEROON_TZ = ZoneInfo("Africa/Douala")


def get_time_range(period):

    now = datetime.now(ZoneInfo("UTC"))


    if period == "today":

        cameroon_now = now.astimezone(CAMEROON_TZ)

        start_cameroon = cameroon_now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        start = start_cameroon.astimezone(
            ZoneInfo("UTC")
        )


    elif period == "24h":

        start = now - timedelta(hours=24)


    elif period == "7d":

        start = now - timedelta(days=7)


    elif period == "30d":

        start = now - timedelta(days=30)


    else:

        start = None


    return start, now