from django.shortcuts import render, redirect
from django.http import FileResponse
from .models import CSVHistory
from .forms import CSVOptionsForm
import datetime
import os
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .forms import LoginForm

from .indiamart import indiamart
from .plastic4trade import plastic4trade
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse

def stream_response(request):
    def event_stream():
        for progress_message in indiamart.scrape():
            yield f"data: {progress_message}\n\n"

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

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
def generate_csvs(request):
    if request.method == "POST":
        form = CSVOptionsForm(request.POST)
        
        if form.is_valid():
            generated_files = []

            if form.cleaned_data.get('indiamart'):
                generated_files.append(indiamart.generate())

            if form.cleaned_data.get('plastic4trade'):
                generated_files.append(plastic4trade.generate())

            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=7)

            CSVHistory.objects.create(
                start_date=start_date,
                end_date=end_date,
                generated_files=",".join(generated_files) # This should store 'indiamart.zip,plastic4trade.zip'
            )

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