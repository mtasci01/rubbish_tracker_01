import datetime
import json
from service.rubbish_tracker_service import RubbishTrackerService


service = RubbishTrackerService()

reports = service.getAllReports()

rightnowUTC = round(datetime.datetime.now(datetime.timezone.utc).timestamp()*1000)

with open('rubbish_tracker_get_reports_out_' + str(rightnowUTC) + '.json', 'w', encoding='utf-8') as f:
    json.dump(reports, f, ensure_ascii=False, indent=4)