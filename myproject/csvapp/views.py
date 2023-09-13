from django.shortcuts import render, redirect
from django.http import FileResponse
from .models import CSVHistory
from .forms import CSVOptionsForm
from datetime import datetime, timedelta
import os
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .forms import LoginForm
from django.http import JsonResponse
from .indiamart import indiamart
from .plastic4trade import plastic4trade
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

def get_scrape_status(request):
    is_running = CSVHistory.objects.filter(is_running=True).exists()

    status = "RUNNING" if is_running else "FINISHED"
    return JsonResponse({"status": status})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('generate_csvs')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'csvapp/login.html', {'form': form})


def download_csv(request, filename):
    relative_path = filename.replace("csvapp/", "", 1)
    file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    print("Full File Path:", file_path)
    
    print("Requested File:", filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{file_path.split("/")[-1]}"'
            return response
    return HttpResponse("File not found.", status=404)
@login_required
@login_required
def generate_csvs(request):

    if request.method == "POST":
        form = CSVOptionsForm(request.POST)

        # Check if a scraping process is already running
        is_already_running = CSVHistory.objects.filter(is_running=True).exists()
        if is_already_running:
            messages.error(request, 'Another scraping process is already running. Please wait.')
            return redirect('history')
        
        if form.is_valid():
            generated_files = []

            # Create the CSVHistory entry with is_running=True since the scraping process is about to start
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            history = CSVHistory.objects.create(
                start_date=start_date,
                end_date=end_date,
                generated_files="",  # Initialize with empty. We'll fill this in later.
                is_running=True  # Set this to True since scraping starts now
            )

            try:
                if form.cleaned_data.get('indiamart'):
                    generated_files.append(indiamart.generate())
                    messages.success(request, 'Scraping Indiamart has finished.')

                if form.cleaned_data.get('plastic4trade'):
                    generated_files.append(plastic4trade.generate())
                    messages.success(request, 'Scraping Plastic4trade has finished.')
            except Exception as e:
                messages.error(request, f"Error during scraping: {e}")
            finally:
                # Now update the CSVHistory entry's generated_files field and set is_running=False
                history.generated_files = ",".join(generated_files)
                history.is_running = False
                history.save()

            return redirect('history')
    else:
        form = CSVOptionsForm()

    return render(request, 'csvapp/form.html', {'form': form})
@login_required
def history(request):
    #CSVHistory.objects.all().delete()

    histories = CSVHistory.objects.all().order_by('-start_date')
    

    # Split the generated_files for each history entry and create display names
    for history in histories:
        full_file_list = history.generated_files.replace("\\","/").split(',')
        display_file_list = [os.path.basename(filename) for filename in full_file_list]
        
        # Zip the lists into tuples of (full filename, display filename)
        history.files = list(zip(full_file_list, display_file_list))

    # Implementing pagination
    paginator = Paginator(histories, 20)  # Show 20 histories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'csvapp/history.html', {'page_obj': page_obj})