from django.urls import path, include
from .views import home, rental_service, catalogue, contact,\
    add_product, list_product, update_product, delete_product,\
    ProductViewset, CategoryViewset, register, product_detail,\
    add_prod_cart, del_prod_cart, subtract_product_cart,\
    clean_cart, cart_page, buy_confirm, add_category,\
    list_category, update_category, delete_category, admin_panel,\
    ContactViewSet,pago, list_contact,\
    QueryTypeViewset, update_contact_status, add_query_type, list_query_type,\
    update_query_type, delete_query_type, RentalOrderViewSet, list_rental_order


from unicodedata import name
from . import views
#from .views import index

from .views import Registrar, order_list

from .views import Recuperar
from .views import user_login
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static




from .views import payment_success



from rest_framework import routers

router = routers.DefaultRouter()
router.register('product', ProductViewset)
router.register('category', CategoryViewset)
router.register('contact', ContactViewSet, basename='contact')
router.register('query-type', QueryTypeViewset, basename='query-type')
router.register(r'rental-orders', RentalOrderViewSet)


urlpatterns = [
    path('', home, name="home"),
    path('catalogue/', catalogue, name="catalogue"),
    path('rental-service/', rental_service, name="rental_service"),
    path('contact/', contact, name="contact"),
    path('list-contact/', list_contact, name="list_contact"),
    path('update-status/<int:contact_id>/', update_contact_status, name='update_status'),
    path('add-query-type/', add_query_type, name="add_query_type"),
    path('list-query-type/', list_query_type, name="list_query_type"),
    path('update-query-type/<int:id>/', update_query_type, name="update_query_type"),
    path('delete-query-type/<id>/', delete_query_type, name="delete_query_type"),
    path('add-product/', add_product, name="add_product"),
    path('list-product/', list_product, name="list_product"),
    path('update-product/<int:id>/', update_product, name="update_product"),
    path('delete-product/<id>/', delete_product, name="delete_product"),
    path('product-detail/<int:id>/', product_detail, name="product_detail"),
    path('add-category/', add_category, name="add_category"),
    path('list-category/', list_category, name="list_category"),
    path('update-category/<id>/', update_category, name="update_category"),
    path('delete-category/<id>/', delete_category, name="delete_category"),
    path('api/', include(router.urls)),
    path('register/', register, name="register"),
    path("add/<int:product_id>", add_prod_cart, name="Add"),
    path("delete/<int:product_id>", del_prod_cart, name="Del"),
    path("subtract/<int:product_id>", subtract_product_cart, name="Sub"),
    path("clean/", clean_cart, name="Clean"),
    path("cart/", cart_page, name="Cart"),
    # path("checkout/", checkout, name="Checkout"),
    path("buy-confirm/", buy_confirm, name="buy_confirm"),
    path("admin-panel/", admin_panel, name="admin_panel"),
    # path("success-payment/", pago_exitoso, name="pago_exitoso"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('pago/', pago, name="pago"),
    path('login/', user_login, name='login'),
    path('accounts/', include('allauth.urls')),
    path('Recuperar/', Recuperar, name='Recuperar'),
    path('Registrar/', Registrar, name='Registrar'),
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_success/', views.update_last_order_paid_status, name='update_last_order_paid_status'),
    path('orders/', order_list, name='order_list'),
    path('list-rental-order/', list_rental_order, name="list_rental_order"),
]
