from django.db import models
from django.contrib.auth.models import User

class MainMenu(models.Model):
    item = models.CharField(max_length=300, unique=True)
    link = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.item

class Book(models.Model):
    name = models.CharField(max_length=200)
    web = models.URLField(max_length=300)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    publishdate = models.DateField(auto_now=True)
    picture = models.FileField(upload_to='bookEx/static/uploads')
    pic_path = models.CharField(max_length=300, editable=False, blank=True)
    username = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.stars for r in ratings) / ratings.count(), 1)
        return 0

    def __str__(self):
        return self.name

class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )

    def is_reply(self):
        return self.parent is not None

class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField()  # [1, 5]
    
    class Meta:
        unique_together = ('book', 'user')  # Unique to users + book

    def __str__(self):
        return f"{self.user.username} rated {self.book.name}: {self.stars} stars"

class Favorite(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f"{self.user.username} favorited {self.book.name}"