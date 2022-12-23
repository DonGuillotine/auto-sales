from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from carts.views import _cart_id
from carts.models import Cart, CartItem
from orders.models import Order, OrderProduct
import requests


# Create your views here.


@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # Create a user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            #  USER ACTIVATION WITH TOKEN TO EMAIL ACCOUNT
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('accounts/verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # Encode the users primary key
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Thank you for registering, an email has been sent to you please verify your account')
            return redirect('/accounts/login/?command=verification&email=' + email)
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                if_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if if_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # GET ALL EXISTING PRODUCT VARIATIONS
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))  #  BY DEFAULT THE VARIATIONS ARE QUERY SETS, THE LIST FUNCTION MAKES IT A LIST(S)

                    #  GET ALL VARIATIONS BASED ON THE USER
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variations_list = []
                    id = []
                    for item in cart_item:
                        existing_variations = item.variations.all()
                        existing_variations_list.append(list(existing_variations))
                        id.append(item.id)

                    #  GET ALL VARIATIONS PRESENT IN THE CART ITEM
                    for product in product_variation:
                        if product in existing_variations_list:
                            index = existing_variations_list.index(product)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in')
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:  #  IF THERE'S 'next' IN THE URL REDIRECT TO ?next/cart/checkout
                    next_page = params['next']
                    return redirect(next_page)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Login details')
            return redirect('login')
    return render(request, 'accounts/login.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations your account has been activated!')
        return redirect('login')
    else:
        messages.error(request, 'Invalid Activation Link')
        return redirect('register')


@login_required(login_url='login')  # If a user types the logout url this would redirect to login
def logout(request):
    auth.logout(request)
    messages.success(request, 'Logged Out successfully')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    order_count = orders.count()
    profile_picture = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'order_count': order_count,
        'profile_picture': profile_picture
    }
    return render(request, 'accounts/dashboard.html', context)


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)  #  THE EXACT IS USED TO GET THE EXACT VALUE FROM THE DATABASE
            #  USER RESET PASSWORD
            current_site = get_current_site(request)
            mail_subject = 'Reset your account password'
            message = render_to_string('accounts/reset_password.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),  # Encode the users primary key
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.info(request, 'An email has been sent to you, click on the link to reset your password')
        else:
            messages.error(request, 'Account Does not Exist')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Reset your Password Please')
        return redirect('reset_password_view')
    else:
        messages.error(request, 'The activation link has expired')
        return redirect('login')


def reset_password_view(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')  #  FROM THE SESSIONS GET THE UID OF THE PARTICULAR USER REQUESTING FOR A PASSWORD RESET
            user = Account.objects.get(pk=uid)  # PASS THE UID TO THE DATABASE AND FIND THE PARTICULAR USER
            user.set_password(password)
            user.save()
            messages.success(request, 'Password Reset Successfully')
            return redirect('login')
        else:
            messages.error(request, 'Passwords does not match')
            return redirect('reset_password_view')
    else:
        return render(request, 'accounts/reset_password_view.html')


@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')  # THE "-" IN created_at WILL ORDER THE RESULT IN DESCENDING ORDER
    context = {
        'orders': orders
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    userprofile = UserProfile.objects.filter(user=request.user).first()
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)  #  TO UPDATE THE FORM
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)  #  THE iexact isn't case sensitive

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password Updated Successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Password does not match')
                return redirect('change_password')
        else:
            messages.error(request, 'Enter a Valid Password')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order_details = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_details:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_details,
        'order': order,
        'sub_total': subtotal
    }
    return render(request, 'accounts/order_details.html', context)
