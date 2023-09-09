from django import forms

class CSVOptionsForm(forms.Form):
    indiamart = forms.BooleanField(required=False)
    plastic4trade = forms.BooleanField(required=False)