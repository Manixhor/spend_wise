from django.db import models

# Create your models here.
from django.db import models

class Expense(models.Model):
    title = models.CharField(max_length=100)
    amount = models.FloatField()
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Income(models.Model):
    source = models.CharField(max_length=100)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)


class Target(models.Model):
    amount = models.FloatField()
    achieved = models.FloatField(default=0)