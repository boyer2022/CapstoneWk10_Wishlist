import tempfile
import filecmp
import os

from django.test import TestCase
from django.urls import reverse
from django.test import override_settings

from django.contrib.auth.models import User
from .models import Place

from PIL import Image 

# Create your tests here.
class TestHomePage(TestCase):
    def test_home_page_shows_empty_list_message_for_empty_database(self):
        home_page_url = reverse('place_list')                               # Check url operations
        response = self.client.get(home_page_url)                           # Check response for server
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')            # Check that html is working
        self.assertContains(response, 'You have no places in your wishlist') # Check for certain content on page

class TestWishList(TestCase):
    
    fixtures = ['test_places']

    def test_wishlist_contains_not_visited_places(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertContains(response, 'Tokyo')
        self.assertContains(response, 'New York')
        self.assertNotContains(response, 'San Francisco')
        self.assertNotContains(response, 'Moab')

class TestVisitedPage(TestCase):

    def test_visited_page_shows_emtpty_list_message_for_empty_database(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertContains(response, 'You have not visited any places yet')


class VisitedList(TestCase):

    fixtures = ['test_places']

    def test_visited_list_shows_visited_places(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertContains(response, 'San Francisco')
        self.assertContains(response, 'Moab')
        self.assertNotContains(response, 'New York')
        self.assertNotContains(response, 'Tokyo')

# Test for adding a new place
class TestAddNewPlace(TestCase):

    def test_add_new_unvisited_place(self):
        add_place_url = reverse('place_list')
        new_place_data = {'name': 'Malibu', 'visited': False }

        response = self.client.post(add_place_url, new_place_data, follow=True)
            # follow=True means: If another request is made as a result of the first request, this on will follow the redirect. 
            #   Not something that happens by default.
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        response_places = response.context['places']                # From views.py
        self.assertEqual(1, len(response_places))                    # Check only one place
        malibu_from_response = response_places[0]

        malibu_from_database = Place.objects.get(name='Malibu', visited=False)

        self.assertEqual(malibu_from_database, malibu_from_response)

# Check that when a place is visited, the DB is updated
class TestVisitedPlace(TestCase):

    fixtures =['test_places']

    def test_visit_place(self):
        visit_place_url = reverse('place_was_visited', args=(2, ))
        response = self.client.post(visit_place_url, follow=True)

        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        self.assertNotContains(response, 'New York')
        self.assertContains(response, 'Tokyo')

        # Checking the DB
        new_york = Place.objects.get(pk=2)
        self.assertTrue(new_york.visited)

# Test for 404
    def test_not_existent_place(self):
        visit_nonexistent_place_url = reverse('place_was_visited', args=(123456, ))
        response = self.client.post(visit_nonexistent_place_url, follow=True)
        self.assertEqual(404, response.status_code)