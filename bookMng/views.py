from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import MainMenu, Book, Comment, Reply
from .forms import BookForm, CommentForm, ReplyForm


def index(request):
    return render(request, 'bookMng/index.html', {
        'item_list': MainMenu.objects.all()
    })

def postbook(request):
    submitted = False
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.username = request.user if request.user.is_authenticated else None
            book.save()
            return HttpResponseRedirect('/postbook?submitted=True')
    else:
        form = BookForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'bookMng/postbook.html', {
        'form': form,
        'item_list': MainMenu.objects.all(),
        'submitted': submitted
    })


def displaybooks(request):
    books = Book.objects.all()
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request, 'bookMng/displaybooks.html', {
        'item_list': MainMenu.objects.all(),
        'books': books
    })


class Register(CreateView):
    template_name = 'registration/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('register-success')

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.pic_path = book.picture.url[14:]
    comments = book.comments.select_related('user').prefetch_related('replies__user')

    if request.method == 'POST':
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.book = book
                comment.user = request.user
                comment.save()
                return redirect('book_detail', book_id=book.id)

        elif 'reply_submit' in request.POST:
            reply_form = ReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.comment_id = request.POST.get('comment_id')
                reply.user = request.user
                reply.save()
                return redirect('book_detail', book_id=book.id)

    else:
        comment_form = CommentForm()
        reply_form = ReplyForm()

    return render(request, 'bookMng/book_detail.html', {
        'item_list': MainMenu.objects.all(),
        'book': book,
        'comments': comments,
        'comment_form': comment_form,
        'reply_form': reply_form
    })


def mybooks(request):
    books = Book.objects.filter(username=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request, 'bookMng/mybooks.html', {
        'item_list': MainMenu.objects.all(),
        'books': books
    })


def book_delete(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    book.delete()
    return render(request, 'bookMng/book_delete.html', {
        'item_list': MainMenu.objects.all()
    })


def about_us(request):
    return render(request, 'bookMng/about_us.html', {
        'item_list': MainMenu.objects.all()
    })


def search_books(request):
    query = request.GET.get('q')
    results = Book.objects.filter(name__icontains=query) if query else []
    return render(request, 'bookMng/search_results.html', {
        'item_list': MainMenu.objects.all(),
        'query': query,
        'results': results
    })


