from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from stores.models import Product, Variation
from .models import Cart, CartItem
from django.contrib.auth.decorators import login_required


# Create your views here.


def _cart_id(request):
    cart = request.session.session_key  # This gets the session id/key in the browser
    if not cart:
        cart = request.session.create()  # If a session does not exist create a new session
    return cart


@csrf_exempt
def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:  # IF THE USER IS AUTHENTICATED
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:  # Loop through all items in the url and get the color and size variations
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)  # check if the results in the key are similar in the database
                    product_variation.append(variation)
                    print(variation)
                except:
                    pass

        #  If the cart item exists do this
        if_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if if_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product,
                                                user=current_user)  # Combining both the cart containing the session id and the products

            existing_variation_list = []
            id = []

            # GET A LIST OF ALL EXISTING VARIATIONS
            for item in cart_item:  # Loop through all items in the CartItem model
                ex_var = item.variations.all()
                existing_variation_list.append(list(ex_var))
                id.append(item.id)  # GET THE ID of the CartItem

            # if the variation exists in the CartItem increase the quantity
            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id[index]  # GET the ID of the CartItem
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            #  Else add another cart item
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:  # IF the length of the product variations is greater than 0
                    item.variations.clear()  # IF the variation is added twice, unlink the previous variation
                    item.variations.add(
                        *product_variation)  # after looping through the variations add it to the variations column in the CartItem model
                item.save()

        #  Else Create a new cart item
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
            )
            if len(product_variation) > 0:  # IF the length of the product variations is greater than 0
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    else:  #  FOR USERS THAT ARE NOT LOGGED IN
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:  # Loop through all items in the url and get the color and size variations
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                      variation_value__iexact=value)  # check if the results in the key are similar in the database
                    product_variation.append(variation)
                    print(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # gets the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)  # if the cart does not exist, this creates a new one
            )
        cart.save()

        #  If the cart item exists do this
        if_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if if_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)  # Combining both the cart containing the session id and the products

            existing_variation_list = []
            id = []

            # GET A LIST OF ALL EXISTING VARIATIONS
            for item in cart_item:  #  Loop through all items in the CartItem model
                ex_var = item.variations.all()
                existing_variation_list.append(list(ex_var))
                id.append(item.id)  #  GET THE ID of the CartItem

            # if the variation exists in the CartItem increase the quantity
            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = id[index]  #  GET the ID of the CartItem
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            #  Else add another cart item
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:  # IF the length of the product variations is greater than 0
                    item.variations.clear()  # IF the variation is added twice, unlink the previous variation
                    item.variations.add(*product_variation)  # after looping through the variations add it to the variations column in the CartItem model
                item.save()

        #  Else Create a new cart item
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation) > 0:  # IF the length of the product variations is greater than 0
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')


def remove_or_delete(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:

            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def delete_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, tax=0, grand_total=0, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:  # for logged in users
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:  #for users that are not logged in
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,
                                             is_active=True)  # filter every product based on the session id and active status
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
def checkout(request, tax=0, grand_total=0, total=0, quantity=0, cart_items=None):
    try:
        if request.user.is_authenticated:  # for logged in users
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:  #for users that are not logged in
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,
                                             is_active=True)  # filter every product based on the session id and active status
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
