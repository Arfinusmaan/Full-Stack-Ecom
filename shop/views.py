from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
from .forms import CustomUserForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth.decorators import login_required

import random


# Create your views here.
def home(request):
    products=Product.objects.filter(trending=1)
    return render(request,'shop/index.html', {'products':products})

def register(request):
    form=CustomUserForm()
    if request.method=='POST':
        form=CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,' Registered Successfully! ')
            return redirect('/login')
    return render(request,'shop/register.html', {'form':form})

def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method=='POST':
            username=request.POST.get('username')
            password=request.POST.get('password')
            user=authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request,' Logged In Successfully! ')
                return redirect('/')
            else:
                messages.warning(request,' Invalid Credentials! ')
                return redirect('/')
    return render(request, 'shop/login.html')

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,' Logged Out Successfully! ')
    return redirect('/')

def collections(request):
    category=Category.objects.filter(status=0)
    return render(request,'shop/collections.html',{'category':category})

def collectionsview(request,name):
    if(Category.objects.filter(name=name, status=0)):
        products=Product.objects.filter(category__name=name)
        return render(request,'shop/products/index.html',{'products':products, 'category__name':name})
    else:
        messages.warning(request,'No Such Category Found')
        return redirect('collections')

def product_details(request, cname, pname):
    if(Category.objects.filter(name=cname, status=0)):
        if(Product.objects.filter(name=pname, status=0)):
            products=Product.objects.filter(name=pname, status=0).first()
            return render(request,'shop/products/product_details.html',{'products':products})
        else:
            messages.warning(request,'No Such Category Found')
            return redirect('collections')
    else:
        messages.warning(request,'No Such Category Found')
        return redirect('collections')
    

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            product_qty = data['product_qty']
            product_id = data['product_id']
            product_status = Product.objects.filter(id=product_id).first()
            if product_status:
                if Cart.objects.filter(user=request.user, product_id=product_id).exists():
                    return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                else:
                    if product_status.quantity >= product_qty:
                        Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                        return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                    else:
                        return JsonResponse({'status': 'Product Stock Not Available'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add to Cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=200)
    
def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,'shop/cart.html',{'cart':cart})
    else:
        return redirect('/')
    
def remove_cart(request,cid):
    cartitem=Cart.objects.get(id=cid)
    cartitem.delete()
    return redirect('/cart')

def add_to_fav(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            data = json.loads(request.body)
            product_id = data['product_id']
            product_status = Product.objects.filter(id=product_id).first()
            if product_status:
                if Favourite.objects.filter(user=request.user, product_id=product_id).exists():
                    return JsonResponse({'status': 'Product Already in Favourite'}, status=200)
                else:
                    Favourite.objects.create(user=request.user, product_id=product_id)
                    return JsonResponse({'status': 'Product Added to Favourite'}, status=200)
        else:
            return JsonResponse({'status': 'Login to Add to Favourite'}, status=200)
    else:
         return JsonResponse({'status': 'Invalid Access'}, status=200)



def favview_page(request):
    if request.user.is_authenticated:
        fav=Favourite.objects.filter(user=request.user)
        return render(request,'shop/fav.html',{'fav':fav})
    else:
        return redirect('/')
    
def remove_fav(request,fid):
    fav_item=Favourite.objects.get(id=fid)
    fav_item.delete()
    return redirect('/fav')

@login_required(login_url='login_page')
def checkout_page(request):
    cart=Cart.objects.filter(user=request.user)
    for item in cart:
        if item.product_qty > item.product.quantity:
            Cart.objects.delete(id=item.id)
    cartitems = Cart.objects.filter(user=request.user)
    total_price = 0
    for item in cartitems:
        total_price= total_price+item.product.selling_price*item.product_qty

    context = {'cartitems':cartitems, 'total_price':total_price }
    return render(request, 'shop/checkout.html', context)

@login_required(login_url='login_page')
def placeorder(request):
    if request.method == 'POST':
        neworder = Order()
        neworder.user = request.user
        neworder.fname = request.POST.get('fname')
        neworder.lname = request.POST.get('lname')
        neworder.email = request.POST.get('email')
        neworder.phone = request.POST.get('phone')
        neworder.address = request.POST.get('address')
        neworder.city = request.POST.get('city')
        neworder.state = request.POST.get('state')
        neworder.country = request.POST.get('country')
        neworder.pincode = request.POST.get('pincode')

        neworder.payment_mode = request.POST.get('payment_mode')
        neworder.payment_id = request.POST.get('payment_id')

        cart = Cart.objects.filter(user=request.user)
        cart_total_price = 0
        for item in cart:
            cart_total_price = cart_total_price + item.product.selling_price * item.product_qty
        neworder.total_price = cart_total_price

        trackno = 'epicdrop' + str(random.randint(1111111, 9999999))
        while Order.objects.filter(tracking_no=trackno).exists():
            trackno = 'epicdrop' + str(random.randint(1111111, 9999999))

        neworder.tracking_no = trackno
        neworder.save()

        neworderitems = Cart.objects.filter(user=request.user)
        for item in neworderitems:
            OrderItem.objects.create(
                order=neworder,
                product=item.product,
                price=item.product.selling_price,
                quantity=item.product_qty
            )

            # Fix: Reduce product quantity and save
            orderproduct = Product.objects.filter(id=item.product_id).first()
            if orderproduct:
                orderproduct.quantity = orderproduct.quantity - item.product_qty
                orderproduct.save()

        # Clear cart after order
        Cart.objects.filter(user=request.user).delete()

        # Fix: Ensure PayPal returns JSON response
        payMode = request.POST.get('payment_mode')
        if payMode == "Paid by Razorpay" or payMode == "Paid by Paypal":
            return JsonResponse({'status': "Your Order has been placed Successfully"})

        messages.success(request, "Your Order has been placed Successfully")

    return redirect('/')



@login_required(login_url='login_page')
def razorpaycheck(request):
    cart=Cart.objects.filter(user=request.user)
    total_price=0
    for item in cart:
        total_price = total_price + item.product.selling_price * item.product_qty
    
    return JsonResponse({
        'total_price':total_price
    })


def orders_page(request):
    orders = Order.objects.filter(user = request.user)
    context = {'orders' : orders}
    return render(request, 'shop/myorders.html', context)


def order_view(request,t_no):
    order = Order.objects.filter(tracking_no=t_no).filter(user=request.user).first()
    orderitem = OrderItem.objects.filter(order=order)
    context = {'orders':order, 'orderitem' : orderitem}
    return render(request, 'shop/orderview.html', context)