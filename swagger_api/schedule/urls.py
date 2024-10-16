from django.urls import path
from .views import TimeSlotAPIView

urlpatterns = [
    path('timeslots/', TimeSlotAPIView.as_view(), name='time_slot'),
]
