from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
from orders.models import OrderProduct
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import ReviewForm, ContactForm
from django.core.mail import EmailMessage, BadHeaderError
from django.conf import settings


# Create your views here.


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug != None:
        categories = get_object_or_404(Category, url=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products, 6)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 30)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

        # Get the reviews
    reviews = None
    for products in products:
        reviews = ReviewRating.objects.filter(product_id=products.id, status=True)
    context = {'product': paged_products, 'product_count': product_count, 'reviews': reviews}
    return render(request, 'store/store.html', context)


def product_details(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__url=category_slug, slug=product_slug)
        if_in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
#  TO CHECK IF A PRODUCT HAS BEEN ORDERED
    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product_id=single_product).exists()
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None

# TO SHOW ALL REVIEWS ON A PARTICULAR PRODUCT
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)

    # TO SHOW THE PRODUCT GALLERY
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {'single_product': single_product, 'if_in_cart': if_in_cart, 'order_product': order_product, 'reviews': reviews, 'product_gallery': product_gallery}
    return render(request, 'store/product_details.html', context)


def search(request):
    if 'my-search' in request.GET:  # If my-search which is input name=search is in the url; store it in the variable my-search
        my_search = request.GET['my-search']
        if my_search:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=my_search) | Q(product_name__icontains=my_search))
            product_count = products.count()
        context = {
            'product': products,
            'product_count': product_count,
        }
        return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')  # TO GET THE URL OF THE CURRENT PAGE AND PASS IT TO THE REDIRECT FUNCTION
    if request.method == 'POST':
        #  PERFORM TWO CHECKS->IF A USER HAS ALREADY REVIEWED A PRODUCT UPDATE HIS REVIEW ELSE CREATE A NEW REVIEW
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)  #  THE INSTANCE->reviews GETS THE FORM UPDATED NOT CREATED!
            form.save()
            messages.success(request, "Your Review Has Been Updated")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Your review has been submitted')
                return redirect(url)


def terms(request):
    title = "Terms and Conditions"
    context = {'title': title}
    return render(request, 'store/terms.html', context)


def delivery(request):
    title = "Terms and Conditions"
    context = {'title': title}
    return render(request, 'store/delivery.html', context)


def refund(request):
    title = "Terms and Conditions"
    context = {'title': title}
    return render(request, 'store/refund.html', context)


def privacy(request):
    title = "Terms and Conditions"
    context = {'title': title}
    return render(request, 'store/privacy.html', context)


def contact(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                send_email = EmailMessage(subject=subject, body=message, from_email=email, to=['support@dapperautoparts.com'])
                send_email.send()
                messages.success(request, 'Your Message has been sent!')
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('home')
    return render(request, "store/contact.html", {'form': form})
