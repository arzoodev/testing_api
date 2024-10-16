from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TimeSlot, Schedule
from .serializers import ScheduleSerializer, TimeSlotSerializer

class TimeSlotAPIView(APIView):

    # POST method to create a new time slot
    def post(self, request, *args, **kwargs):
        schedule_data = request.data.get('schedule', {})

        for day, time_slots in schedule_data.items():
            # Validate day
            if day.capitalize() not in dict(Schedule.DAY_CHOICES):
                return Response({"error": f"Invalid day: {day}"}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create the schedule instance for the specific day
            schedule_instance, created = Schedule.objects.get_or_create(day=day.capitalize())

            for slot in time_slots:
                # Check for existing time slots
                existing_slot = TimeSlot.objects.filter(
                    schedule=schedule_instance,
                    start=slot['start'],
                    stop=slot['stop']
                ).first()

                if existing_slot:
                    # Append new IDs if they are not already present
                    existing_ids = set(existing_slot.ids)  # Convert to set for easier manipulation
                    new_ids = set(slot['ids'])

                    if not new_ids.issubset(existing_ids):
                        existing_ids.update(new_ids)  # Append new IDs
                        existing_slot.ids = list(existing_ids)  # Update the IDs
                        existing_slot.save()  # Save the updated time slot
                    continue  # Skip to the next time slot since we processed this one

                # Create a new TimeSlot instance if no existing slot was found
                TimeSlot.objects.create(schedule=schedule_instance, **slot)

        return Response({"message": "Time slots processed successfully."}, status=status.HTTP_201_CREATED)


    def get(self, request, *args, **kwargs):
        schedules = Schedule.objects.all()  # Retrieve all schedules
        
        # Initialize a structured dictionary for the response
        schedule_dict = {
            "schedule": {}
        }

        for schedule in schedules:
            day = schedule.day.lower()  # Convert day to lowercase
            time_slots = []

            for time_slot in schedule.time_slots.all():
                # Format start and stop times to "HH:MM"
                formatted_start = time_slot.start.strftime("%H:%M")
                formatted_stop = time_slot.stop.strftime("%H:%M")
                time_slots.append({
                    "start": formatted_start,
                    "stop": formatted_stop,
                    "ids": time_slot.ids
                })

            schedule_dict["schedule"][day] = time_slots

        return Response(schedule_dict, status=status.HTTP_200_OK)  # Return the structured data

    def delete(self, request, *args, **kwargs):
        schedule_data = request.data.get('schedule', {})

        for day, time_slots in schedule_data.items():
            # Validate day
            if day.capitalize() not in dict(Schedule.DAY_CHOICES):
                return Response({"error": f"Invalid day: {day}"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the schedule instance for the specific day
            try:
                schedule_instance = Schedule.objects.get(day=day.capitalize())
            except Schedule.DoesNotExist:
                return Response({"error": f"No schedule found for {day.capitalize()}"}, status=status.HTTP_404_NOT_FOUND)

            # Iterate over the provided time slots for deletion
            for slot in time_slots:
                # Retrieve existing time slots for the schedule that match start and stop times
                existing_time_slots = TimeSlot.objects.filter(
                    schedule=schedule_instance,
                    start=slot['start'],
                    stop=slot['stop']
                )

                for existing_slot in existing_time_slots:
                    # Convert existing ids to a set for easier manipulation
                    existing_ids = set(existing_slot.ids)
                    ids_to_delete = set(slot['ids'])

                    # Remove IDs that need to be deleted
                    remaining_ids = existing_ids - ids_to_delete

                    if remaining_ids:
                        # Update the time slot with remaining IDs and save it
                        existing_slot.ids = list(remaining_ids)
                        existing_slot.save()
                    else:
                        # If no IDs remain, delete the time slot
                        existing_slot.delete()

        return Response({"message": "Time slots updated successfully."}, status=status.HTTP_204_NO_CONTENT)

    
    def patch(self, request, *args, **kwargs):
        schedule_data = request.data.get('schedule', {})

        for day, time_slots in schedule_data.items():
            # Validate day
            if day.capitalize() not in dict(Schedule.DAY_CHOICES):
                return Response({"error": f"Invalid day: {day}"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the schedule instance for the specific day
            try:
                schedule_instance = Schedule.objects.get(day=day.capitalize())
            except Schedule.DoesNotExist:
                return Response({"error": f"No schedule found for {day.capitalize()}"}, status=status.HTTP_404_NOT_FOUND)

            # Iterate over the provided time slots for updating
            for slot in time_slots:
                # Retrieve the existing time slot that matches start and stop times
                existing_time_slot = TimeSlot.objects.filter(
                    schedule=schedule_instance,
                    start=slot['start'],
                    stop=slot['stop']
                ).first()

                if existing_time_slot:
                    # Update the IDs of the existing time slot
                    existing_time_slot.ids = slot['ids']  # Update to the new list of IDs
                    existing_time_slot.save()  # Save the changes
                else:
                    # If no existing time slot was found, you can choose to handle this case
                    return Response({"error": f"No time slot found for {slot['start']} - {slot['stop']} on {day.capitalize()}"},
                                    status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Time slots updated successfully."}, status=status.HTTP_200_OK)
