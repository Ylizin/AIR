from djongo import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=30)
    password = models.CharField(max_length=50)
    email = models.EmailField()
    initial_domain_0 = [models.TextField()]
    initial_domain_1 = [models.TextField()]

    def __unicode__(self):
        return self.username

