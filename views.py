import os
import pickle
import numpy as np

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import JobPost, PredictionResult
from .forms import JobPostForm
from .serializers import JobPostSerializer, PredictionResultSerializer


# ==============================
# ML MODEL LOADING
# ==============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'jobs', 'ml_model', 'model.pkl')
VECTORIZER_PATH = os.path.join(BASE_DIR, 'jobs', 'ml_model', 'vectorizer.pkl')

model = None
vectorizer = None

if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)

    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)


# ==============================
# HOME VIEW
# ==============================

def index(request):
    return render(request, 'index.html')

def predict_job(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')

        # Temporary dummy response
        result = "Real Job"
        confidence = "87%"

        return render(request, 'index.html', {
            'result': result,
            'confidence': confidence
        })

    return render(request, 'index.html')

# ==============================
# REGISTER VIEW
# ==============================

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please check the form.")
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


# ==============================
# LOGIN VIEW
# ==============================

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


# ==============================
# LOGOUT VIEW
# ==============================

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('home')


# ==============================
# DASHBOARD
# ==============================

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# ==============================
# SUBMIT JOB + PREDICTION
# ==============================

@login_required
def submit_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.save()

            if model is None or vectorizer is None:
                messages.error(request, "ML Model is not trained yet.")
                return redirect('dashboard')

            text = job.title + " " + job.description
            text_vector = vectorizer.transform([text])
            prediction = model.predict(text_vector)[0]
            probability = np.max(model.predict_proba(text_vector)) * 100

            label = "Fake" if prediction == 1 else "Real"

            result = PredictionResult.objects.create(
                job=job,
                prediction=label,
                confidence=round(probability, 2)
            )

            return render(request, 'result.html', {'result': result})
    else:
        form = JobPostForm()

    return render(request, 'submit_job.html', {'form': form})


# ==============================
# HISTORY VIEW
# ==============================

@login_required
def history_view(request):
    jobs = JobPost.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'jobs': jobs})


# ==============================
# ADMIN DASHBOARD
# ==============================

@staff_member_required
def admin_dashboard(request):
    jobs = JobPost.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard.html', {'jobs': jobs})

def about_us(request):
    return render(request, 'about_us.html')


# ==============================
# DRF API ENDPOINT
# ==============================

@api_view(['POST'])
def api_predict(request):
    title = request.data.get('title')
    description = request.data.get('description')

    if not title or not description:
        return Response(
            {"error": "Title and description are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if model is None or vectorizer is None:
        return Response(
            {"error": "Model not trained."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    text = title + " " + description
    text_vector = vectorizer.transform([text])

    prediction = model.predict(text_vector)[0]
    probability = np.max(model.predict_proba(text_vector)) * 100

    label = "Fake" if prediction == 1 else "Real"

    return Response({
        "prediction": label,
        "confidence": round(probability, 2)
    })