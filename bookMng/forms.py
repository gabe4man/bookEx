from django import forms
from django.forms import ModelForm
from .models import Book, Comment

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = [
            'name',
            'web',
            'price',
            'picture',
        ]

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Write a reply...'})
        }