import json

from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from carts.models import CartItem
from django.template.loader import render_to_string
from stores.models import Product
from .forms import OrderForm
from .models import *
import datetime
from django.http import HttpResponseRedirect
# Create your views here.


def place_order(request, total=0, quantity=0):
    current_user = request.user
    #  IF THE CART COUNT IS LESS THAN OR EQUALS 0 REDIRECT THE USER TO THE STORE PAGE
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    else:
        grand_total = 0
        tax = 0
        for cart_item in cart_items:
            total = total + (cart_item.product.price * cart_item.quantity)
            quantity = quantity + cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
        if request.method == 'POST':
            form = OrderForm(request.POST)
            if form.is_valid():
                data = Order()
                data.user = current_user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.order_note = form.cleaned_data['order_note']
                data.order_total = grand_total
                data.tax = tax
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()

                # GENERATE THE ORDER NUMBER FROM THE DATE AND ID OF THE ORDER MODEL

                year = int(datetime.date.today().strftime('%Y'))
                day = int(datetime.date.today().strftime('%d'))
                month = int(datetime.date.today().strftime('%m'))
                date = datetime.date(year, month, day)
                current_date = date.strftime('%Y%m%d')
                order_number = current_date + str(data.id)
                data.order_number = order_number
                data.save()

                order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                    'tax': tax,
                    'grand_total': grand_total,
                }
                return render(request, 'orders/payment.html', context)
            else:
                return redirect('checkout')
        else:
            pass


def payments(request):
    body = json.loads(request.body)  # GETTING THE DETAILS FROM PAYPAL REFER: PAYMENT.HTML-> SCRIPT
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])  # We want to get the total orders so we get it based on the user, setting the status to False and getting the order number based on paypal's order number
    #   1. STORE TRANSACTION DETAILS INTO THE PAYMENT MODEL
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()
    #  2. UPDATE THE ORDER MODEL, (THE PAYMENT FIELD IS IN THE ORDER MODEL AS A FOREIGN KEY) AND SET THE ORDERED PRODUCT TO TRUE
    order.payment = payment
    order.is_ordered = True
    order.save()
    #  3. MOVE THE CART ITEMS TO THE ORDER PRODUCT TABLE
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()

        #  4. TO ADD THE PRODUCT VARIATION TO THE ORDER PRODUCT TABLE
        cart_item = CartItem.objects.get(id=item.id)  #  GET THE VARIATIONS OF A PARTICULAR CART ITEM
        product_variation = cart_item.variations.all()  # GET THE PRODUCT VARIATIONS
        order_product = OrderProduct.objects.get(id=order_product.id)  #  GET THE NEW ID AFTER THE FIRST SAVE
        order_product.variations.set(product_variation) #  ADD THE VARIATIONS TO THE ORDER TABLE
        order_product.save()
        #  5. REDUCE THE QUANTITY OF THE SOLD PRODUCTS
        product = Product.objects.get(id=item.product_id)  # GET THE PRODUCTS FROM THE PRODUCTS MODEL ID = CART ITEM->PRODUCT->PRODUCT_ID
        product.stock -= item.quantity  # REDUCE THE STOCK OF THE PRODUCTS
        product.save()
    #  6. CLEAR THE CART ITEMS
    CartItem.objects.filter(user=request.user).delete()
    #  7. SEND AN ORDER RECEIVED EMAIL TO THE UESR
    # mail_subject = 'Thank you for your Patronage'
    # message = render_to_string('orders/order_received_email.html', {
    #     'user': request.user,
    #     'order': order
    # })
    # to_email = request.user.email
    # send_email = EmailMessage(mail_subject, message, to=[to_email])
    # send_email.send()
    #  8. SEND THE ORDER NUMBER AND TRANSACTION ID TO THE SEND DATA METHOD VIA JSON RESPONSE IN THE PAYMENT.HTML
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }
    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    trans_id = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=trans_id)

        sub_total = 0
        for i in ordered_products:  #  LOOP OVER THE ORDER PRODUCT TABLE. TO GET THE TOTAL sub_total + sub_total + product price x quantity
            sub_total += i.product_price * i.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'trans_id': payment.payment_id,
            'payment': payment,
            'sub_total': sub_total,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

