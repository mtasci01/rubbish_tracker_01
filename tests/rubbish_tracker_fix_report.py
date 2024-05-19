
from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()
rightnowUTC = service.getRightnowUTC()
reportId = "6639422b871fe7ce3722574c"
service.fixReport(reportId, rightnowUTC)