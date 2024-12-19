"""Sel value API"""

from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config

from pyramid_app_caseinterview.models.depthseries import Depthseries
from pyramid_app_caseinterview.models.timeseries import Timeseries
from pyramid_app_caseinterview.views.serialization import DateObject

from . import View
from datetime import datetime

class API(View):
    """API endpoints"""

    @view_config(
        route_name="timeseries",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        request_method="GET",
    )
    def timeseries_api(self):
        start_date = self.request.params.get("from")
        end_date = self.request.params.get("to")

        try:
            if start_date:
                start_date =datetime.strptime(start_date, "%Y-%m-%d")
            if end_date:
                end_date =datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return {"Error" : "Invalid date format. use YYYY-MM-DD."}
        
        query = self.session.query(Timeseries)
        
        if start_date and end_date:
            query = query.filter((Timeseries.datetime >= start_date) & (Timeseries.datetime <= end_date))
        if start_date:
            query = query.filter((Timeseries.datetime >= start_date))
        if end_date:
            query = query.filter((Timeseries.datetime <= end_date)) 

        return [
            {
                "id": str(q.id),
                "datetime": DateObject(q.datetime),
                "value": q.value,
            }
            for q in query.all()
        ]

    @view_config(
        route_name="depthseries",
        permission=NO_PERMISSION_REQUIRED,
        renderer="json",
        request_method="GET",
    )
    def depthseries_api(self):
        query = self.session.query(Depthseries)
        return [
            {
                "id": str(q.id),
                "depth": q.depth,
                "value": q.value,
            }
            for q in query.all()
        ]
