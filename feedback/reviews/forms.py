
from django import forms
from .models import Review

# class ReviewForm(forms.Form):
#     user_name = forms.CharField(label="Your Name", 
#                                 max_length=10,
#                                 error_messages={"required": "Please enter your valid name.",
#                                                 "max_length": "Your name is too long."})
#     review_text = forms.CharField(label="your Feedback", 
#                                   widget=forms.Textarea,
#                                   max_length=200,
#                                   )

#     rating = forms.IntegerField(label="Your Rating", min_value=1,max_value=5)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ['owner']  # Set by the view from request.user, never chosen in the form ('__all__' would show it)
        labels = {"user_name": "Your Name",
                  "review_text" : "Your Feedback",
                  "rating": "Your Rating"}

        error_messages = {"user_name": {"required":"Please enter your valid name.",
                           "max_length": "Your name is too long."}}

