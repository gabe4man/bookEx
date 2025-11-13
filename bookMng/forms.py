from django import forms
from django.forms import ModelForm
from .models import Book, Comment, Reply

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

class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = ['text']

