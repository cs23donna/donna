from django.db import models  
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class CustomUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)  
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('recruiter', 'Recruiter'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')

    class Meta:
        db_table = "custom_user"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="student_profile")
    username = models.CharField(max_length=150, unique=True)  
    password = models.CharField(max_length=128)  

    class Meta:
        db_table = "student"
        indexes = [models.Index(fields=['user'])]

class Recruiter(models.Model):
    STATUS_CHOICES = [
        ('AWAITING_APPROVAL', 'Awaiting Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True, related_name="recruiter_profile")
    username = models.CharField(max_length=150, unique=True)  
    password = models.CharField(max_length=128)  
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AWAITING_APPROVAL')  # ✅ Added status field

    class Meta:
        db_table = "recruiter"
        indexes = [models.Index(fields=['user'])]


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    """Automatically creates a profile for new users."""
    if created:
        if instance.user_type == "student":
            Student.objects.create(user=instance, username=instance.username, password=instance.password)
        elif instance.user_type == "recruiter":
            Recruiter.objects.create(user=instance, username=instance.username, password=instance.password, status="AWAITING_APPROVAL")

post_save.connect(create_profile, sender=CustomUser)
