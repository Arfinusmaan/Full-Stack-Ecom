from django.urls import path
from . import views

urlpatterns=[
    path('',views.home, name='home'),
    path('register',views.register, name='register'),
    path('login',views.login_page, name='login'),
    path('logout',views.logout_page, name='logout'),
    path('collections',views.collections, name='collections'),
    path('collections/<str:name>',views.collectionsview, name='collections'),
    path('collections/<str:cname>/<str:pname>',views.product_details, name='product_details'),
    path('addtocart',views.add_to_cart, name='addtocart'),
    path('cart',views.cart_page, name='cart'),
    path('remove_cart/<str:cid>',views.remove_cart, name='remove_cart'),
    path('addtofav',views.add_to_fav, name='addtofav'),
    path('fav',views.favview_page, name='fav'),
    path('remove_fav/<str:fid>',views.remove_fav, name='remove_fav'),
    path('checkout/',views.checkout_page,name='checkout'),
    path('place-order',views.placeorder, name='placeorder'),

    path('proceed-to-pay',views.razorpaycheck),
    path('my-orders',views.orders_page, name= "myorders"),
    path('view-order/<str:t_no>',views.order_view, name= "orderview"),
]