from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Schedule

class ScheduleAPITests(APITestCase):
    
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')  # Log in the user

        self.schedule_data = {
            'day_of_week': 'monday',
            'start_time': '00:00',
            'stop_time': '01:00',
            'ids': [1, 2],
        }

    def test_create_schedule(self):
        response = self.client.post(reverse('schedule-list'), self.schedule_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_read_schedule(self):
        schedule = Schedule.objects.create(**self.schedule_data)
        response = self.client.get(reverse('schedule-detail', args=[schedule.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_schedule(self):
        schedule = Schedule.objects.create(**self.schedule_data)
        update_data = {'ids': [3, 4]}
        response = self.client.patch(reverse('schedule-detail', args=[schedule.id]), update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_schedule(self):
        schedule = Schedule.objects.create(**self.schedule_data)
        response = self.client.delete(reverse('schedule-detail', args=[schedule.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
