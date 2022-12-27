from django import forms
from .models import ReviewRating, ContactPage


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactPage
        fields = ['email', 'subject', 'message']
