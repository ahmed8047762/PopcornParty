# movies/models.py

from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    poster_url = models.URLField()
    imdb_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.title

# Deprecated: MovieEvent model has been moved to the events app
# class MovieEvent(models.Model):
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     event_date = models.DateTimeField()
#     host = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
#     participants = models.ManyToManyField('accounts.CustomUser', related_name='movie_events')

#     def __str__(self):
#         return f"{self.movie.title} - {self.event_date}"