from service.rubbish_tracker_service import RubbishTrackerService

service = RubbishTrackerService()

pointsPolygon = [[12.2, 41.6], [12.2, 42.2], [12.8, 42.2], [12.8, 41.6]]

#service.saveArea(pointsPolygon,"Rome",'6636a276067a84bae086dd20')

pointsPolygon = [[12.335249,43.106983], [12.331796,43.141681], [12.434317,43.140302], [12.422668,43.084835]]

service.saveArea(pointsPolygon,"Perugia",None)