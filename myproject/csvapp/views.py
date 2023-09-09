from django.shortcuts import render, redirect
from django.http import FileResponse
from .models import CSVHistory
from .forms import CSVOptionsForm
import datetime
import os

# Assuming your scripts are in the same directory
from . import indiamart, plastic4trade
from django.http import HttpResponse

def download_csv(request, filename):
    file_path = os.path.join('YOUR_DIRECTORY_WHERE_CSVS_ARE_STORED', filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    return HttpResponse("File not found.", status=404)
def generate_csvs(request):
    if request.method == "POST":
        form = CSVOptionsForm(request.POST)
        file_to_download = None  # This will store the path to the generated file

        if form.is_valid():
            generated_files = []

            if form.cleaned_data.get('indiamart'):
                file_to_download = indiamart.generate()  # Assuming it returns the file path
                generated_files.append('indiamart.csv')

            if form.cleaned_data.get('plastic4trade'):
                plastic4trade.generate()
                generated_files.append('plastic4trade.csv')

            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=7)

            CSVHistory.objects.create(
                start_date=start_date,
                end_date=end_date,
                generated_files=",".join(generated_files)
            )

            # If indiamart.csv was generated, serve it as a download
            if file_to_download:
                return FileResponse(open(file_to_download, 'rb'), as_attachment=True, filename=os.path.basename(file_to_download))
            else:
                return redirect('history')

    else:
        form = CSVOptionsForm()

    return render(request, 'csvapp/form.html', {'form': form})

def history(request):
    histories = CSVHistory.objects.all().order_by('-start_date')
    return render(request, 'csvapp/history.html', {'histories': histories})