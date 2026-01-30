from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=200)
    link = models.URLField(blank=True, null=True)           # Play Store link
    description = models.TextField()
    image = models.ImageField(upload_to='apps/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    
    # Admin will mark if it's fraud or not
    is_fraud = models.BooleanField(default=False)
    fraud_reason = models.TextField(blank=True, null=True)
    
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Review(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    text = models.TextField()  # User's comment
    rating = models.IntegerField(
        choices=[(1,1),(2,2),(3,3),(4,4),(5,5)],
        blank=True,
        null=True
    )

    # IP address of reviewer
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    # Filled automatically by sentiment analysis
    sentiment = models.CharField(max_length=20, blank=True, null=True)
    sentiment_score = models.FloatField(blank=True, null=True)

    # Admin can mark fake review
    is_fake = models.BooleanField(default=False)
    admin_note = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} → {self.application.name}"



class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback by {self.user.username}" 