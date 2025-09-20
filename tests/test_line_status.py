from etl.transform import normalize_line_status

def test_status_cols():
    sample = [
      {"id":"central","lineStatuses":[{"statusSeverity":10,"statusSeverityDescription":"Good Service"}]},
      {"id":"district","lineStatuses":[{"statusSeverity":5,"statusSeverityDescription":"Minor Delays"}]},
    ]
    df = normalize_line_status(sample)
    assert {"as_of","line_id","status_severity","status_description"} <= set(df.columns)
    assert len(df) == 2
