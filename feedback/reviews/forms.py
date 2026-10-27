
from django import forms

class ReviewForm(forms.Form):
    user_name = forms.CharField(label="Your Name", 
                                max_length=10,
                                error_messages={"required": "Please enter your valid name.",
                                                "max_length": "Your name is too long."})

