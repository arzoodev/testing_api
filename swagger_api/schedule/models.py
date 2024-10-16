from django.db import models

class Schedule(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    day = models.CharField(max_length=10, choices=DAY_CHOICES)

    def __str__(self):
        return self.day

class TimeSlot(models.Model):
    start = models.TimeField()
    stop = models.TimeField()
    ids = models.JSONField()  # Assuming this will store a list of IDs
    schedule = models.ForeignKey(Schedule, related_name='time_slots', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.schedule.day}: {self.start} - {self.stop}"
