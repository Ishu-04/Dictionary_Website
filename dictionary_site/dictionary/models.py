from django.db import models
from django.contrib.auth.models import User

class Word(models.Model):
    word = models.CharField(max_length=100)
    language = models.CharField(max_length=10, default='en')  # Added language field
    meaning = models.TextField()
    pronunciation = models.CharField(max_length=100)
    part_of_speech = models.CharField(max_length=20)
    synonyms = models.TextField()
    antonyms = models.TextField()
    notes = models.TextField(null=True, blank=True)

    class Meta:
        app_label = 'dictionary'

    def __str__(self):
        return self.word

class LinguisticFeature(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='linguistic_features')
    language = models.CharField(max_length=10, default='en')
    feature_name = models.CharField(max_length=100)
    feature_value = models.TextField()

    class Meta:
        app_label = 'dictionary'

    def __str__(self):
        return f"{self.word.word} - {self.feature_name} ({self.language})"


# 5A: Search History Model (Add this below the Word model)
class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Connects search history to a user
    word = models.CharField(max_length=255)  # Stores the searched word
    language = models.CharField(max_length=10, default='en')  # Stores the language code of the search
    search_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'dictionary'
    
    def __str__(self):
        return f"{self.user} searched {self.word} ({self.language}) at {self.search_time}"



class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'dictionary'


# Create your models here.
