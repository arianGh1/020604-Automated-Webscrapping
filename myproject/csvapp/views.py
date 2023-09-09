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
    # Depending on the filename, determine the correct directory path
    if "indiamart" in filename:
        file_path = os.path.join('csvapp/indiamart', filename)
    elif "plastic4trade" in filename:
        file_path = os.path.join('csvapp/plastic4trade', filename)
    else:
        return HttpResponse("File not found.", status=404)

    # Check if the file exists and then serve it as a download
    if os.path.exists(file_path):
        with open(file_path, 'rb') as file:
            response = HttpResponse(file.read(), content_type='application/zip')
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
                generated_files.append('indiamart.zip')

            if form.cleaned_data.get('plastic4trade'):
                file_to_download = plastic4trade.generate()
                generated_files.append('plastic4trade.zip')

            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=7)

            CSVHistory.objects.create(
                start_date=start_date,
                end_date=end_date,
                generated_files=",".join(generated_files)
            )

            # If a zip file was generated, serve it as a download
            if file_to_download:
                return FileResponse(open(file_to_download, 'rb'), as_attachment=True, filename=os.path.basename(file_to_download))
            else:
                return redirect('history')

    else:
        form = CSVOptionsForm()

    return render(request, 'csvapp/form.html', {'form': form})

def history(request):
    histories = CSVHistory.objects.all().order_by('-start_date')
    split_histories = []
    
    for history in histories:
        split_histories.append({
            'start_date': history.start_date,
            'end_date': history.end_date,
            'files': history.generated_files.split(","),
        })
    
    return render(request, 'csvapp/history.html', {'histories': split_histories})