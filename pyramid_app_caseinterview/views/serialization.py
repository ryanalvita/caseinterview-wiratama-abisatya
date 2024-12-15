from pyramid.view import view_config
import datetime

class DateObject:
    def __init__(self, datetime_value):
        self.datetime = datetime_value

    def __json__(self, request):
        if isinstance(self.datetime, datetime.datetime):
            return self.datetime.isoformat()