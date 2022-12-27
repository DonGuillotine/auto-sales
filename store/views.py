from django.shortcuts import render
from stores.models import Product, ReviewRating, BannerGallery
from accounts.models import UserProfile
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from store import settings


def home(request):
    title = 'Dapperautoparts - Dealer in original motor parts direct from the factory.'
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY
    product = Product.objects.all().filter(is_available=True).order_by('?')
    paginator = Paginator(product, 45)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    # Get the reviews
    reviews = None
    for products in product:
        reviews = ReviewRating.objects.filter(product_id=products.id, status=True)

    banner = BannerGallery.objects.all()

    context = {
        'title': title,
        'product': paged_products,
        'reviews': reviews,
        'banner': banner
    }
    return render(request, 'home.html', context)


def footer(request):
    product = Product.objects.all()
    context = {'product': product}
    return render(request, 'includes/footer.html', context)


@login_required(login_url='login')  # Check login
def savelangcur(request):
    lasturl = request.META.get('HTTP_REFERER')
    curren_user = request.user
    #  Save to User profile database
    data = UserProfile.objects.get(user_id=curren_user.id )
    data.currency_id = request.session['currency']
    data.save()  # save data
    return HttpResponseRedirect(lasturl)


def selectcurrency(request):
    lasturl = request.META.get('HTTP_REFERER')
    if request.method == 'POST':  # check post
        request.session['currency'] = request.POST['currency']
    return HttpResponseRedirect(lasturl)
