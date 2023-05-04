from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage


# Create your models here.
class Place(models.Model) :
    # Creating a foreign key user account, Built into Django
        # on-delete=models.CASCADE means if user is deleted, delete all info
    user = models.ForeignKey('auth.User', null=False, on_delete=models.CASCADE)     
    name = models.CharField(max_length=200)
    visited = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True)
    date_visited = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='user_images/', blank=True, null=True)

    
    def save(self, *args, **kwargs):
        # get reference to previous version of this Place 
        old_place = Place.objects.filter(pk=self.pk).first()
        if old_place and old_place.photo:
            if old_place.photo != self.photo:
                self.delete_photo(old_place.photo)

        super().save(*args, **kwargs)
            

    def delete(self, *args, **kwargs):
        if self.photo:
            self.delete_photo(self.photo)

        super().delete(*args, **kwargs)

    
    def delete_photo(self, photo):
        if default_storage.exists(photo.name):
            default_storage.delete(photo.name)


    def _str_(self):
        photo_str = self.photo.url if self.photo else 'No Photo!'
        # Info on notes, first 100 Characters
        notes_str = self.notes[100:] if self.notes else 'No Notes!'

        return f'{self.pk}: {self.name} visited? {self.visited} on {self.date_visited}. Notes: {notes_str}. Photo {photo_str}'
