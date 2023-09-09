from django.shortcuts import render, redirect
from django.http import FileResponse
from .models import CSVHistory
from .forms import CSVOptionsForm
import datetime
import os

# Assuming your scripts are in the same directory
from .indiamart import indiamart
from .plastic4trade import plastic4trade
from django.http import HttpResponse

def download_csv(request, filename):
    filename = filename.replace("\\", "/")
    if 'indiamart' in filename:
        file_path = os.path.join('csvapp/indiamart', filename)
    elif 'plastic4trade' in filename:
        file_path = os.path.join('csvapp/plastic4trade', filename)
    else:
        return HttpResponse("Invalid file name.", status=400)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    return HttpResponse("File not found.", status=404)
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

def history(request):
    histories = CSVHistory.objects.all().order_by('-start_date')
    
    # Split the generated_files for each history entry
    for history in histories:
        history.file_list = history.generated_files.split(',')

    return render(request, 'csvapp/history.html', {'histories': histories})