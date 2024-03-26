from email.mime.text import MIMEText
from smtplib import SMTPAuthenticationError

import requests
from django.core.files.storage import default_storage

from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from mysite.models import Contact, UserProfile
from mysite.models import PostJob
from mysite.models import Apply_job
import mysite.screen as screen

from django.contrib.auth.decorators import login_required
from django.views.generic import ListView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, get_user_model
from .models import PostJob
from .serializers import PostJobSerializer, UserSerializer, CandidateSerializer
from rest_framework import generics
import smtplib
from email.message import EmailMessage

# write your code
def index(request):
    job_list = PostJob.objects.get_queryset().order_by('id')
    total_jobs = job_list.count()
    total_users = User.objects.all().count()
    total_companies = PostJob.objects.values('company_name').annotate(Count('company_name', distinct=True))
    query_num = 10
    paginator = Paginator(job_list, query_num)
    page = request.GET.get('page')
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)
    if qs.has_previous():
        page_show_min = (qs.previous_page_number() - 1) * query_num + 1
    elif total_jobs > 0:
        page_show_min = 1
    else:
        page_show_min = 0
    if qs.has_next():
        page_show_max = (qs.previous_page_number() + 1) * query_num - 1
    else:
        page_show_max = total_jobs
    context = {
        'query': qs,
        'job_listings': job_list,
        'job_len': total_jobs,
        'curr_page1': page_show_min,
        'curr_page2': page_show_max,
        'companies': total_companies.count(),
        'candidates': total_users
    }
    return render(request, "mysite/index.html", context=context)


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # print("user: ", username)
        # print("password: ", password)
        user = auth.authenticate(username=username, password=password)
        if user:
            print(user.is_active, user.is_staff)
        if user is not None:
            auth.login(request, user)
            print(user)
            return redirect('index')
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')

    else:
        return render(request, 'mysite/login.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        userType = request.POST['user_type']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        # phone = request.POST['phone']
        # address = request.POST['address']
        # linkedin_id = request.POST['linkedin_id']
        # github_id = request.POST['github_id']

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Taken!')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken!')
                return redirect('register')
            else:
                user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username,
                                                email=email, is_staff=userType, password=password1)
                user.save()
                # print("username: ", user)
                # print("password: ", password1)
                messages.info(request, 'User Created!')
                return redirect('login')
        else:
            messages.info(request, 'Password is not matching!')
            return redirect('register')
        # return redirect('index')

    else:
        return render(request, 'mysite/register.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


def about(request):
    return render(request, 'mysite/about.html')


@login_required(login_url='login')
def job_single(request, id):
    job_query = PostJob.objects.get(id=id)
    context = {
        'q': job_query,
    }
    return render(request, "mysite/job-single.html", context)


def job_listings(request):
    job_list = PostJob.objects.get_queryset().order_by('id')
    total_jobs = job_list.count()
    total_users = User.objects.all().count()
    total_companies = PostJob.objects.values('company_name').annotate(Count('company_name', distinct=True))
    query_num = 7
    paginator = Paginator(job_list, query_num)
    page = request.GET.get('page')
    try:
        qs = paginator.page(page)
    except PageNotAnInteger:
        qs = paginator.page(1)
    except EmptyPage:
        qs = paginator.page(paginator.num_pages)
    if qs.has_previous():
        page_show_min = (qs.previous_page_number() - 1) * query_num + 1
    elif total_jobs > 0:
        page_show_min = 1
    else:
        page_show_min = 0
    if qs.has_next():
        page_show_max = (qs.previous_page_number() + 1) * query_num - 1
    else:
        page_show_max = total_jobs
    context = {
        'query': qs,
        'job_listings': job_list,
        'job_len': total_jobs,
        'curr_page1': page_show_min,
        'curr_page2': page_show_max,
        'companies': total_companies.count,
        'candidates': total_users
    }
    return render(request, "mysite/job-listings.html", context=context)


@login_required(login_url='login')
def post_job(request):
    if request.method == "POST":
        title = request.POST['title']
        company_name = request.POST['company_name']
        employment_status = request.POST['employment_status']
        vacancy = request.POST['vacancy']
        gender = request.POST['gender']
        if 'details' in request.POST:
            details = request.POST['details']
        else:
            details = False

        if 'responsibilities' in request.POST:
            responsibilities = request.POST['responsibilities']
        else:
            responsibilities = False

        experience = request.POST['experience']
        other_benefits = request.POST['other_benefits']
        job_location = request.POST['job_location']
        salary = request.POST['salary']
        application_deadline = request.POST['application_deadline']

        # Handling file upload
        image = request.FILES.get('image')
        if image:
            # Save the uploaded image to the media directory
            image_name = default_storage.save(image.name, image)

        job = PostJob.objects.filter(title=title, company_name=company_name, employment_status=employment_status)

        if not job:
            ins = PostJob(title=title, company_name=company_name, employment_status=employment_status, vacancy=vacancy,
                          gender=gender, details=details,
                          responsibilities=responsibilities, experience=experience, other_benefits=other_benefits,
                          job_location=job_location, salary=salary, application_deadline=application_deadline)

            if image:
                ins.image = image_name  # Assuming you have an image field in your PostJob model
            ins.save()
            messages.info(request, 'Job successfully posted!')
            print("The data has been added into the database!")
        else:
            messages.info(request, 'This job is already posted!')
            print('This job is already posted!')

        return redirect('job-listings')

    return render(request, 'mysite/post-job.html', {})


def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        # phone = request.POST['phone']
        if 'phone' in request.POST:
            phone = request.POST['phone']
        else:
            phone = False

        if 'subject' in request.POST:
            subject = request.POST['subject']
        else:
            subject = False

        if 'desc' in request.POST:
            desc = request.POST['desc']
        else:
            desc = False

        # desc = request.POST['desc']
        # print(name, email, phone, subject, desc)
        ins = Contact(name=name, email=email, phone=phone, subject=subject, desc=desc)
        ins.save()
        print("Data has been save in database!")
        return redirect('/')

    else:
        return render(request, "mysite/contact.html")


@login_required(login_url='login')
def applyjob(request, id):
    job = PostJob.objects.get(id=id)
    print(job.id)
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        print(name, email)
        gender = request.POST['gender']
        experience = request.POST['experience']
        print(experience)

        coverletter = request.POST['coverletter']
        cv = request.FILES['cv']
        print(cv)
        print(cv)
        Apply_job.objects.filter(name=name, email__exact=email, company_name=job.company_name, title=job.title).delete()
        ins = Apply_job(name=name, email=email, cv=cv, experience=experience,coverletter=coverletter, company_name=job.company_name, gender=gender,
                            title=job.title)
        ins.save()
        messages.info(request, 'Successfully applied for the post!')
        print("The Data is saved into database!")
        return redirect('job-listings')

    return render(request, 'mysite/applyjob.html', {'company_name': job.company_name, 'title': job.title})


@login_required(login_url='login')
def ranking(request, id):
    job_data = PostJob.objects.get(id=id)
    print(job_data.id, job_data.title, job_data.company_name)
    jobfilename = job_data.company_name + '_' + job_data.title + '.txt'
    job_desc = job_data.details + '\n' + job_data.responsibilities + '\n' + job_data.experience + '\n';
    resumes_data = Apply_job.objects.filter(company_name=job_data.company_name, title=job_data.title,
                                            cv__isnull=False)
    result_arr = screen.res(resumes_data, job_data)
    return render(request, 'mysite/ranking.html',
                  {'items': result_arr, 'company_name': job_data.company_name, 'title': job_data.title})


class SearchView(ListView):
    model = PostJob
    template_name = 'mysite/search.html'
    context_object_name = 'all_job'

    def get_queryset(self):
        return self.model.objects.filter(title__contains=self.request.GET['title'],
                                         job_location__contains=self.request.GET['job_location'],
                                         employment_status__contains=self.request.GET['employment_status'])


class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            # Utilisateur authentifié avec succès
            email = user.email  # Retrieve user's email (replace with your logic)
            # Call your custom login function here, e.g. custom_login(request, user)
            return JsonResponse({'success': True, 'message': 'Authentication successful.', 'email': email})
        else:
            # Échec de l'authentification
            return JsonResponse({'success': False, 'message': 'Invalid credentials.'}, status=401)





class JobListAPIView(generics.ListAPIView):
    serializer_class = PostJobSerializer

    def get_queryset(self):
        employment_status = self.request.query_params.get('employment_status')
        if employment_status is not None:
            try:
                # Convert the employment_status parameter to an integer
                employment_status = int(employment_status)
            except ValueError:
                # If the parameter cannot be converted to an integer, return an empty queryset
                return PostJob.objects.none()

            # Filter the queryset based on the integer employment_status value
            return PostJob.objects.filter(employment_status=employment_status)

        return PostJob.objects.all()
class SiteStatsAPIView(APIView):
    def get(self, request):
        total_jobs = PostJob.objects.all().count()
        total_users = User.objects.all().count()
        total_companies = PostJob.objects.values('company_name').distinct().count()
        candidates = Apply_job.objects.all().count()

        site_stats = {
            'total_jobs': total_jobs,
            'total_users': total_users,
            'total_companies': total_companies,
            'candidates': candidates,
        }

        return Response(site_stats)

class SearchJobsAPIView(generics.ListAPIView):
    serializer_class = PostJobSerializer

    def get_queryset(self):
        # Récupérer les paramètres de recherche depuis les paramètres de l'URL
        title = self.request.GET.get('title')
        job_location = self.request.GET.get('job_location')
        employment_status = self.request.GET.get('employment_status')

        # Filtrer les emplois en fonction des paramètres de recherche
        queryset = PostJob.objects.all()

        if title:
            queryset = queryset.filter(title__icontains=title)

        if job_location:
            queryset = queryset.filter(job_location__icontains=job_location)

        if employment_status:
            queryset = queryset.filter(employment_status__icontains=employment_status)

        return queryset
class SignupAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Add additional logic if needed

            return Response({'success': True, 'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'message': 'Invalid data provided.'}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def post_job_api(request):
    if request.method == 'POST':
        # Get the data from the POST request
        title = request.POST.get('title')
        company_name = request.POST.get('company_name')
        employment_status = request.POST.get('employment_status')
        vacancy = request.POST.get('vacancy')
        gender = request.POST.get('gender')
        details = request.POST.get('details')
        responsibilities = request.POST.get('responsibilities')
        experience = request.POST.get('experience')
        other_benefits = request.POST.get('other_benefits')
        job_location = request.POST.get('job_location')
        salary = request.POST.get('salary')
        application_deadline = request.POST.get('application_deadline')

        # Process the data and save it to your database
        # For simplicity, let's assume you have a model named PostJob and save the data to it.
        job = PostJob.objects.create(
            title=title,
            company_name=company_name,
            employment_status=employment_status,
            vacancy=vacancy,
            gender=gender,
            details=details,
            responsibilities=responsibilities,
            experience=experience,
            other_benefits=other_benefits,
            job_location=job_location,
            salary=salary,
            application_deadline=application_deadline,
        )

        # Return a success response for the API
        return JsonResponse({'success': True})

    return JsonResponse({'success': False})

@api_view(['POST'])
def job_application_api(request):
    required_fields = ['name', 'email', 'gender', 'coverletter', 'company_name', 'title', 'experience']

    for field in required_fields:
        if field not in request.data:
            return Response({'success': False, 'message': f'Missing {field} in request data.'}, status=status.HTTP_400_BAD_REQUEST)

    name = request.data['name']
    email = request.data['email']
    gender = request.data['gender']
    coverletter = request.data['coverletter']
    cv = request.FILES.get('cv')
    company_name = request.data['company_name']
    title = request.data['title']
    experience = request.data['experience']

    existing_application = Apply_job.objects.filter(
        name=name,
        email=email,
        company_name=company_name,
        title=title,
    ).first()

    if existing_application:
        return Response({'success': False, 'message': 'You have already applied for this job.'})

    application = Apply_job(
        name=name,
        email=email,
        gender=gender,
        coverletter=coverletter,
        cv=cv,
        company_name=company_name,
        title=title,
        experience=experience
    )
    application.save()
    return Response({'success': True, 'message': 'Job application submitted successfully.'})
@api_view(['GET'])
def job_rank_api(request, job_id):
    try:
        job_data = PostJob.objects.get(id=job_id)
        resumes_data = Apply_job.objects.filter(company_name=job_data.company_name, title=job_data.title, cv__isnull=False)
        result_arr = screen.res(resumes_data, job_data)

        # Create a list of dictionaries for the ranked candidates
        ranked_candidates = [{'rank': candidate['rank'], 'name': candidate['name'], 'score': candidate['score']} for candidate in result_arr.values()]

        # Sort the list based on rank
        ranked_candidates.sort(key=lambda x: x['rank'])

        return JsonResponse(ranked_candidates, safe=False)
    except PostJob.DoesNotExist:
        return Response({'message': 'Job not found'}, status=404)

@csrf_exempt
def send_contact_email(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        recipient_email = 'ouassen32@gmail.com'  # Replace with the recipient's email address

        # Email content
        email_content = f'Name: {name}\nEmail: {email}\nPhone: {phone}\nSubject: {subject}\nMessage: {message}'

        # Connect to the SMTP server
        smtp_server = 'smtp.office365.com'
        smtp_port = 587
        smtp_user = 'pfa2023@hotmail.com'  # Replace with your Outlook email address
        smtp_password = 'Danger@1234'  # Replace with your Outlook password or application-specific password

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)

            # Create the email message
            msg = MIMEText(email_content)
            msg['From'] = smtp_user
            msg['To'] = recipient_email
            msg['Subject'] = f'Contact Form Submission - {subject}'

            # Send the email
            server.sendmail(smtp_user, [recipient_email], msg.as_string())
            server.quit()

            return JsonResponse({'success': True, 'message': 'Email sent successfully.'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})