from django import forms
from django.core.exceptions import ValidationError

class CSVOptionsForm(forms.Form):
    indiamart = forms.BooleanField(required=False)
    plastic4trade = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        if not (cleaned_data.get("indiamart") or cleaned_data.get("plastic4trade")):
            raise ValidationError("Please select at least one option before generating CSV.")
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)