from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Recruiter

# Register CustomUser with Django Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "user_type")
    search_fields = ("username", "email")
    list_filter = ("user_type",)

# Register Student model
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user_id", "get_username", "get_email")  # Use user_id instead of id
    search_fields = ("user__username", "user__email")

    def get_username(self, obj):
        return obj.user.username
    get_username.admin_order_field = "user__username"
    get_username.short_description = "Username"

    def get_email(self, obj):
        return obj.user.email
    get_email.admin_order_field = "user__email"
    get_email.short_description = "Email"

# Register Recruiter model
@admin.register(Recruiter)
class RecruiterAdmin(admin.ModelAdmin):
    list_display = ("user_id", "get_username", "get_email")  # Use user_id instead of id
    search_fields = ("user__username", "user__email")

    def get_username(self, obj):
        return obj.user.username
    get_username.admin_order_field = "user__username"
    get_username.short_description = "Username"

    def get_email(self, obj):
        return obj.user.email
    get_email.admin_order_field = "user__email"
    get_email.short_description = "Email"

