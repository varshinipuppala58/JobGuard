from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Job


def home(request):
    return render(request, 'jobs/home.html')


def job_list(request):
    query = request.GET.get('q')

    if query:
        jobs = Job.objects.filter(title__icontains=query)
    else:
        jobs = Job.objects.all()

    for job in jobs:
        verify_job(job)

    return render(request, 'jobs/job_list.html', {'jobs': jobs})


def job_detail(request, job_id):
    job = Job.objects.get(id=job_id)

    warnings = verify_job(job)

    return render(
        request,
        'jobs/job_detail.html',
        {
            'job': job,
            'warnings': warnings
        }
    )


def verify_job(job):
    score = 0
    warnings = []

    if job.company:
        score += 25
    else:
        warnings.append("Company information is missing")

    if job.location:
        score += 20
    else:
        warnings.append("Location information is missing")

    if job.salary:
        score += 20
    else:
        warnings.append("Salary information is missing")

    if job.description and len(job.description.strip()) >= 50:
        score += 20
    else:
        warnings.append("Job description is too short")

    if job.application_url:
        score += 15
    else:
        warnings.append("Application link is missing")

    if score >= 85:
        job.is_verified = True
    else:
        job.is_verified = False

    job.verification_score = score
    job.save()

    return warnings


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')

    else:
        form = UserCreationForm()

    return render(request, 'jobs/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')

    return render(request, 'jobs/login.html')


def user_logout(request):
    logout(request)
    return redirect('/')

from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    jobs = Job.objects.all()

    verified_count = jobs.filter(is_verified=True).count()
    total_jobs = jobs.count()

    return render(
        request,
        'jobs/dashboard.html',
        {
            'total_jobs': total_jobs,
            'verified_count': verified_count,
        }
    )