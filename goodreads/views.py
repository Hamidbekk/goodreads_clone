from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render

from books.models import BookReview


# Create your views here.


def landing_page(request):
    print(request.user.is_authenticated)
    return render(request, 'landing.html')


def home_page(request):
    book_reviews = BookReview.objects.all().order_by("-created_at")
    page_size = request.GET.get('page_size', 10)
    paginator = Paginator(book_reviews, page_size)

    page_num = request.GET.get('page', 1)
    page_object = paginator.get_page(page_num)

    return render(request, "home.html", {"page_obj": page_object})


