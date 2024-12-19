from sqlalchemy.inspection import inspect

def stream_csv(query, model):
    """Stream CSV data for download."""

    columns = [column.key for column in inspect(model).columns]
    header_row = ",".join(columns) + "\n"
    yield header_row.encode("utf-8")

    for q in query.yield_per(1000): 
        row = [str(getattr(q, column)) for column in columns]
        yield (",".join(row) + "\n").encode("utf-8")