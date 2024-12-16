"""Sel value API"""

from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.view import view_config
from pyramid.response import Response

from pyramid_app_caseinterview.models.depthseries import Depthseries
from pyramid_app_caseinterview.models.timeseries import Timeseries

from pyramid_app_caseinterview.views.serialization import DateObject

from pyramid_app_caseinterview.views.downloader import stream_csv

from sqlalchemy import func
from datetime import datetime

from . import View


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
        
        
        if start_date and end_date:
            query = query.filter((Timeseries.datetime >= start_date) & (Timeseries.datetime <= end_date))
        if start_date:
            query = query.filter((Timeseries.datetime >= start_date))
        if end_date:
            query = query.filter((Timeseries.datetime <= end_date)) 
        else:
            query = self.session.query(Timeseries)

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
        filter_max = self.session.query(
            Depthseries.depth,
            func.max(Depthseries.value).label("max_value")
    ).group_by(Depthseries.depth).subquery()

        query = self.session.query(Depthseries).join(
            filter_max,
            (Depthseries.depth == filter_max.c.depth) & (Depthseries.value == filter_max.c.max_value)
        ).filter(Depthseries.value.isnot(None)) #filter out "null" values
        return [
            {
                "id": str(q.id),
                "depth": q.depth,
                "value": q.value,
            }
            for q in query.all()
        ]
    
    @view_config(
        route_name="depthseries_download",
        permission=NO_PERMISSION_REQUIRED,
        renderer=None,
        request_method="GET",
    )
    def download_depthseries_api(self):
        start_depth = self.request.params.get("from")
        end_depth = self.request.params.get("to")

        try:
            if start_depth:
                start_depth = int(start_depth)
            if end_depth:
                end_depth = int(end_depth)
        except ValueError as e:
            return {"Error": f"Require integer. [{e}]"}

        query = self.session.query(Depthseries)

        if start_depth and end_depth:
            query = query.filter((Depthseries.depth >= start_depth) & (Depthseries.depth <= end_depth))
        elif start_depth:
            query = query.filter(Depthseries.depth >= start_depth)
        elif end_depth:
            query = query.filter(Depthseries.depth <= end_depth)

        filter_max = self.session.query(
            Depthseries.depth,
            func.max(Depthseries.value).label("max_value")
        ).group_by(Depthseries.depth).subquery()

        query = query.join(
            filter_max,
            (Depthseries.depth == filter_max.c.depth) & (Depthseries.value == filter_max.c.max_value)
        ).filter(Depthseries.value.isnot(None))

        response = Response(
            app_iter=stream_csv(query, Depthseries),
            content_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=depthseries.csv"
            }
        )
        return response
