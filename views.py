from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import SignUpForm
from .models import Student, Recruiter, CustomUser
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            print(f"✅ User saved: {user.username}, Type: {user.user_type}")

            if user.user_type == "student":
                student, created = Student.objects.get_or_create(
                    user=user, 
                    defaults={"username": user.username, "password": user.password}
                )

            elif user.user_type == "recruiter":
                recruiter, created = Recruiter.objects.get_or_create(
                    user=user, 
                    defaults={"username": user.username, "password": user.password, "status": "AWAITING_APPROVAL"}
                )

                # ✅ Send email to admin
                send_mail(
                    'Recruiter Approval Request',
                    f'Recruiter {user.username} has signed up and needs approval.',
                    settings.EMAIL_HOST_USER,  # Your email
                    [admin[1] for admin in settings.ADMINS],  # ✅ Fetch admin emails from settings
                    fail_silently=False,
                )

            messages.success(request, "🎉 Account created! Recruiters must wait for admin approval.")
            return redirect("login_api")  # ✅ Redirect to login after signup

    else:
        form = SignUpForm()

    return render(request, "recruiter/signup.html", {"form": form})

@login_required
def pending_recruiters(request):
    """Admin can see all recruiters awaiting approval."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    pending = Recruiter.objects.filter(status='AWAITING_APPROVAL')
    recruiters_list = [{'id': r.user.id, 'username': r.username, 'email': r.user.email} for r in pending]
    return JsonResponse({'pending_recruiters': recruiters_list})

@login_required  # ✅ Added @login_required
def approve_recruiter(request, recruiter_id):
    """Admin approves a recruiter."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    recruiter = get_object_or_404(Recruiter, user_id=recruiter_id)
    recruiter.status = 'APPROVED'
    recruiter.save()

    # ✅ Send approval email to recruiter
    send_mail(
        'Recruiter Account Approved',
        f'Hello {recruiter.username}, your account has been approved!',
        settings.EMAIL_HOST_USER,
        [recruiter.user.email],
        fail_silently=False,
    )

    return JsonResponse({'message': f'Recruiter {recruiter.username} approved'})

@login_required  # ✅ Added @login_required
def reject_recruiter(request, recruiter_id):
    """Admin rejects a recruiter."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    recruiter = get_object_or_404(Recruiter, user_id=recruiter_id)
    recruiter.status = 'REJECTED'
    recruiter.save()

    return JsonResponse({'message': f'Recruiter {recruiter.username} rejected'})

@csrf_exempt
def login_api(request):
    """API endpoint for user login."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            # Check if email and password are provided
            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            # Authenticate user
            user = authenticate(username=email, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({'message': 'Login successful', 'user_type': user.user_type})
            else:
                # Send a more detailed error message
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid request format'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

