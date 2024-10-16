from rest_framework import serializers
from .models import TimeSlot, Schedule

class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['start', 'stop', 'ids']

    def validate_ids(self, value):
        # Ensure ids is a list of integers
        if not isinstance(value, list) or not all(isinstance(i, int) for i in value):
            raise serializers.ValidationError("IDs must be a list of integers.")
        return value

class ScheduleSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True)

    class Meta:
        model = Schedule
        fields = ['day', 'time_slots']

    def create(self, validated_data):
        schedule_data = validated_data.pop('time_slots')  # Get all time slots data

        for day, time_slots_data in schedule_data.items():
            # Create or retrieve the schedule instance for the specific day
            schedule, created = Schedule.objects.get_or_create(day=day.capitalize())  # Ensure the day name is capitalized

            for slot_data in time_slots_data:
                # Check for existing time slot to prevent duplication
                existing_slot = TimeSlot.objects.filter(
                    schedule=schedule,
                    start=slot_data['start'],
                    stop=slot_data['stop']
                ).first()

                if existing_slot:
                    # Append new ids if they are not already present
                    existing_ids = set(existing_slot.ids)  # Convert to set for easier manipulation
                    new_ids = set(slot_data['ids'])

                    if not new_ids.issubset(existing_ids):
                        existing_ids.update(new_ids)  # Append new ids
                        existing_slot.ids = list(existing_ids)  # Update the ids
                        existing_slot.save()  # Save the updated time slot
                    continue  # Skip to the next time slot as we already processed this one

                # Create the TimeSlot instance if no existing slot was found
                TimeSlot.objects.create(schedule=schedule, **slot_data)

        return schedule
