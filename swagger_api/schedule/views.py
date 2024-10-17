from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TimeSlot, Schedule
from .serializers import ScheduleSerializer, TimeSlotSerializer

class TimeSlotAPIView(APIView):

    # POST method to create a new time slot
    def post(self, request, *args, **kwargs):
        schedule_data = request.data.get('schedule', {})
        print(schedule_data)
        
        duplicate_slots = []  # List to track duplicate time slots

        for day, time_slots in schedule_data.items():
            # Validate day
            if day.capitalize() not in dict(Schedule.DAY_CHOICES):
                return Response({"error": f"Invalid day: {day}"}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create the schedule instance for the specific day
            schedule_instance, created = Schedule.objects.get_or_create(day=day.capitalize())

            for slot in time_slots:
                # Find existing time slots for the same schedule instance with matching start and stop times
                existing_slots = TimeSlot.objects.filter(
                    schedule=schedule_instance,
                    start=slot['start'],
                    stop=slot['stop']
                )

                if existing_slots.exists():
                    # We found existing slots, let's check for duplicate IDs
                    for existing_slot in existing_slots:
                        existing_ids = set(existing_slot.ids)  # Get existing IDs as a set
                        new_ids = set(slot['ids'])  # Get new IDs as a set

                        # Check for duplicate IDs
                        if existing_ids == new_ids:
                            duplicate_slots.append({
                                "start": existing_slot.start,
                                "stop": existing_slot.stop,
                                "ids": existing_slot.ids
                            })
                        else:
                            # Combine existing and new IDs
                            combined_ids = list(existing_ids.union(new_ids))  # Union of existing and new IDs
                            existing_slot.ids = combined_ids  # Update the slot's IDs
                            existing_slot.save()  # Save the updated time slot

                    continue  # Skip to the next time slot since we processed this one

                # If no existing slot is found, create a new TimeSlot instance
                TimeSlot.objects.create(schedule=schedule_instance, **slot)

        # Prepare response
        if duplicate_slots:
            return Response(
                {
                    "message": " data already exists."
                },
                status=status.HTTP_200_OK
            )

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
        no_records_found = True  # Flag to track if any day-related records were found
        ids_not_found = True  # Flag to track if the specific ids were found

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

                if not existing_time_slots.exists():
                    continue  # If no matching time slots are found, move to the next one

                for existing_slot in existing_time_slots:
                    no_records_found = False  # Set to False since we found a record for this day
                    
                    # Convert existing ids to a set for easier manipulation
                    existing_ids = set(existing_slot.ids)
                    ids_to_delete = set(slot['ids'])

                    if ids_to_delete.issubset(existing_ids):
                        ids_not_found = False  # Set to False if we find the specific ids to delete

                        # Remove IDs that need to be deleted
                        remaining_ids = existing_ids - ids_to_delete

                        if remaining_ids:
                            # Update the time slot with remaining IDs and save it
                            existing_slot.ids = list(remaining_ids)
                            existing_slot.save()
                        else:
                            # If no IDs remain, delete the time slot
                            existing_slot.delete()
                    else:
                        # If the specific ids were not found in the existing time slot
                        continue  # Move to the next time slot

        if no_records_found:
            # If no records were found for the day, return a message indicating this
            return Response({"message": "No matching records found for deletion."}, status=status.HTTP_404_NOT_FOUND)
        
        if ids_not_found:
            # If the day was found but the specific ids were not found
            return Response({"message": "No matching IDs found for deletion."}, status=status.HTTP_404_NOT_FOUND)

        # If records were deleted successfully, return a success message
        return Response({"message": "Data deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


    
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
