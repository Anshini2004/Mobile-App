from django.db.models import Avg
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from merger.models import Activity, BookingReview


class ActivityViewSet(ViewSet):
    """
    Returns all activities grouped by activity_type.
    Each activity includes its images (absolute URLs) and average review rating.
    Only includes activity types that have at least one activity.

    GET /api/activities/
    """

    def list(self, request):
        result = []

        for activity_type, _ in Activity.ACTIVITY_TYPES:
            activities_qs = (
                Activity.objects
                .filter(activity_type=activity_type)
                .prefetch_related("images")
            )

            activities_data = []

            for activity in activities_qs:
                avg_rating = (
                    BookingReview.objects
                    .filter(booking__activity=activity, is_deleted=False)
                    .aggregate(avg=Avg("rating"))["avg"]
                )

                images = [
                    request.build_absolute_uri(img.image.url)
                    for img in activity.images.all()
                ]

                activities_data.append({
                    "id": activity.id,
                    "name": activity.name,
                    "activity_type": activity.activity_type,
                    "description": activity.description,
                    "base_price": activity.base_price,
                    "location": activity.location,
                    "duration": activity.duration,
                    "max_participants": activity.max_participants,
                    "images": images,
                    "average_rating": round(avg_rating, 1) if avg_rating is not None else None,
                })

            result.append({
                "activity_type": activity_type,
                "activities": activities_data,
            })

        return Response(result)