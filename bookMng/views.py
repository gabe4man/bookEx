from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import MainMenu, Book, Comment, Rating, Favorite
from .forms import BookForm, CommentForm, ReplyForm, RatingForm


def index(request):
    return render(request, 'bookMng/index.html', {
        'item_list': MainMenu.objects.all(),
        'user':request.user
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

    # Get all comments (including replies) but order newest first
    comments = (
        book.comments
            .select_related('user')
            .filter(parent__isnull=True)   # ONLY top-level comments
            .order_by('-created_at')
    )
    # Default empty forms
    comment_form = CommentForm()
    reply_form = CommentForm()  # reply uses same Comment model
    rating_form = RatingForm()

    # Get user’s existing rating (if any)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(book=book, user=request.user).first()
    
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, book=book).exists()
    if request.method == 'POST':
        # Comment
        if 'comment_submit' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.book = book
                comment.user = request.user
                comment.save()
                return redirect('book_detail', book_id=book.id)

        # Reply
        elif 'reply_submit' in request.POST:
            reply_form = CommentForm(request.POST)
            if reply_form.is_valid():
                parent_id = request.POST.get('parent_comment_id')
                parent_comment = Comment.objects.get(id=parent_id)

                reply = reply_form.save(commit=False)
                reply.book = book
                reply.user = request.user
                reply.parent = parent_comment
                reply.save()

                return redirect('book_detail', book_id=book.id)

        # Rating
        elif 'rating_submit' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                stars = rating_form.cleaned_data['stars']
                Rating.objects.update_or_create(
                    book=book,
                    user=request.user,
                    defaults={'stars': stars},
                )
                return redirect('book_detail', book_id=book.id)
        # Favorite
        elif 'favorite_submit' in request.POST:
            if request.user.is_authenticated:
                fav, created = Favorite.objects.get_or_create(user=request.user, book=book)
                
                if not created:
                    # If it already existed, unfavorite it
                    fav.delete()
                
            return redirect('book_detail', book_id=book.id)
    rating = book.average_rating
    rating_string = ""
    for i in range(0,5):
        delta = round(2*(rating - i))
        if delta >= 2:
            rating_string += "🌕"
        elif delta == 1:
            rating_string += "🌗"
        else:
            rating_string += "🌑"

    return render(request, 'bookMng/book_detail.html', {
        'item_list': MainMenu.objects.all(),
        'book': book,
        'comments': comments,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'rating_form': rating_form,
        'user_rating': user_rating,
        'rating_string': rating_string,
        'is_favorited': is_favorited,
    })



def mybooks(request):
    books = Book.objects.filter(username=request.user)
    favorite_books = Book.objects.filter(favorited_by__user=request.user)
    for b in books:
        b.pic_path = b.picture.url[14:]
    return render(request, 'bookMng/mybooks.html', {
        'item_list': MainMenu.objects.all(),
        'books': books,
        'favorite_books': favorite_books,
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
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Book.objects.filter(name__icontains=query)

    return render(request, 'bookMng/search_results.html', {
        'item_list': MainMenu.objects.all(),
        'query': query,
        'results': results,
    })

@property
def average_rating(self):
    ratings = self.ratings.all()
    if ratings.exists():
        return round(sum(r.stars for r in ratings) / ratings.count(), 1)
    return 0
