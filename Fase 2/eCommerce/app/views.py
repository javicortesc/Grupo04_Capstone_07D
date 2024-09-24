from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm, ProductForm, CustomUserCreationForm, CategoryForm, QueryTypeForm, RentalOrderForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import Product, Category, Contact, QueryType, RentalOrder
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework import viewsets, serializers
from .serializers import ProductSerializer, CategorySerializer, ContactSerializer, QueryTypeSerializer, RentalOrderSerializer
import requests
from django.contrib.auth.decorators import login_required, permission_required
from app.cart import Cart
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Sum, Count
from django.views.decorators.csrf import csrf_exempt


from .models import Order,OrderItem

from django.middleware.csrf import get_token
import logging


# Create your views here.
from telnetlib import LOGOUT
from tokenize import group
from turtle import delay
from django import forms
from unicodedata import name
from .models import  Usuarios
from .forms import  UsuariosForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from rest_framework.decorators import permission_classes
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseRedirect
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from conejofurioso.viewsLogin import login as api_login
import json
import requests
from rest_framework.authtoken.models import Token
from rest_framework.response import Response as apiResponse
from rest_framework.views import APIView

tok = None

def is_staff(user):
    return (user.is_authenticated and user.is_superuser)
#VIEWSETS PARA APIS
class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        products = Product.objects.all()

        name = self.request.GET.get('name')
        is_featured = self.request.GET.get('is_featured')
        category = self.request.GET.get('category')
        is_new = self.request.GET.get('is_new')
        min_price = self.request.GET.get('min_price_filter')
        max_price = self.request.GET.get('max_price_filter')
        is_rentable = self.request.GET.get('is_rentable')

        if name:
            products = products.filter(name__contains=name)
        if category:
            products = products.filter(category=category)
        if min_price and max_price:
            products = products.filter(price__range=(min_price, max_price))
        elif min_price:
            products = products.filter(price__gte=min_price)
        elif max_price:
            products = products.filter(price__lte=max_price)
        
        # Aplicar los filtros de featured y new
        if is_featured:
            products = products.filter(is_featured=True)
        if is_new:
            products = products.filter(is_new=True)
        #filtro para rentable
        if is_rentable:
            products = products.filter(is_rentable=True)

        return products
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)
    
    def perform_create(self, serializer):
        serializer.save()
    
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        status = request.data.get('status')
        instance.status = status
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class QueryTypeViewset(viewsets.ModelViewSet):
    queryset = QueryType.objects.all()
    serializer_class = QueryTypeSerializer

class RentalOrderViewSet(viewsets.ModelViewSet):
    queryset = RentalOrder.objects.all()
    serializer_class = RentalOrderSerializer
    

#VISTAS INICIALES
def home(request):
    # Definimos los parámetros para filtrar productos
    params = {
        'is_new__in': 'true,false',
        'is_featured__in': 'true,false',
    }
    # Obtenemos los productos desde la API aplicando los filtros
    product_response = requests.get(settings.API_BASE_URL + 'product/', params=params).json()
    # Filtrar los productos para excluir los que tienen is_rentable=True
    filtered_products = [product for product in product_response if not product['is_rentable']]
    
    categories_response = requests.get(settings.API_BASE_URL + 'category/').json()
    
    data = {
        'products': filtered_products,
        'categories': categories_response
    }
    
    return render(request, 'app/home.html', data)

def catalogue(request):
    # Obtenemos los filtros desde el html
    name_filter = request.GET.get('name', '')
    category_filter = request.GET.get('category', '')
    min_price_filter = request.GET.get('min_price_filter', '')
    max_price_filter = request.GET.get('max_price_filter', '')

    # Definimos los parámetros para filtrar productos
    params = {
        'name': name_filter,
        'category': category_filter,
        'min_price_filter': min_price_filter,
        'max_price_filter': max_price_filter,
    }

    # Obtenemos los productos desde la API aplicando los filtros
    response = requests.get(settings.API_BASE_URL + 'product/', params=params)
    products = response.json()
    # Filtrar los productos para excluir los que tienen is_rentable=True
    filtered_products = [product for product in products if not product['is_rentable']]

    # Obtenemos las categorías desde la API
    categories = requests.get(settings.API_BASE_URL + 'category/').json()
    
    # Para limpiar los filtros
    if 'clear_filters' in request.GET:
        response = requests.get(settings.API_BASE_URL + 'product/').json()
        products = response

    data = {
        'products': filtered_products,
        'categories': categories,
    }

    return render(request, 'app/catalogue.html', data)

def rental_service(request):
    if request.method == 'POST':
        form = RentalOrderForm(request.POST)
        if form.is_valid():
            # Obtener el objeto datetime del formulario
            deliver_date = form.cleaned_data['deliver_date']
            # Convertir el objeto datetime a una cadena de texto en formato ISO 8601
            deliver_date_iso = deliver_date.strftime('%Y-%m-%dT%H:%M')

            rental_order_data = {
                'rut': form.cleaned_data['rut'],
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data['address'],
                'phone': form.cleaned_data['phone'],
                'deliver_date': deliver_date_iso,  # Utilizar la cadena de texto en lugar del objeto datetime
            }

            # Obtener la lista de productos seleccionados
            products_selected = request.POST.getlist('products')
            products_selected = [int(product_id) for product_id in products_selected if product_id.isdigit()]

            rental_order_data['products'] = products_selected  # Agregar la lista de productos seleccionados

            try:
                # Crear la orden a través de la API
                rental_order_response = requests.post(settings.API_BASE_URL + 'rental-orders/', json=rental_order_data)
                if rental_order_response.status_code == 201:
                    rental_order = rental_order_response.json()

                    # Agregar los productos a la orden a través de la API
                    product_ids = [str(product_id) for product_id in products_selected]  # Convertir los IDs de productos a cadena de texto
                    add_product_url = settings.API_BASE_URL + f'rental-orders/{rental_order["id"]}/add-product/?products={",".join(product_ids)}'
                    requests.post(add_product_url)

                    return JsonResponse({'message': 'La solicitud de arriendo ha sido enviado correctamente'})
                else:
                    return JsonResponse({'error': 'Error al enviar la solicitud'})

            except Exception as e:
                return JsonResponse({'error': 'Error en el servidor'})

    else:
        form = RentalOrderForm()

    # Definimos los parámetros para filtrar productos
    params = {
        'is_rentable': 'true',
    }

    # Obtenemos los productos desde la API aplicando los filtros
    product_response = requests.get(settings.API_BASE_URL + 'product/', params=params).json()

    data = {
        'form': form,
        'products': product_response,
        'csrf_token': get_token(request)
    }

    return render(request, 'app/rental_service.html', data)


#CONTATO
def contact(request):
    data = {
        'form': ContactForm()
    }

    return render(request, 'app/contact/contact.html', data)

def update_contact_status(request, contact_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        data = {
            'status': status
        }
        response = requests.patch(settings.API_BASE_URL + f'contact/{contact_id}/', data=data)

    return redirect('list_contact')

@permission_required('app.view_contact')
def list_contact(request):
    response = requests.get(settings.API_BASE_URL + 'contact/')
    contacts = response.json()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(contacts, 5)
        contacts = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity': contacts,
        'paginator': paginator
    }
    return render(request, 'app/contact/list.html', data)

#VISTAS DE QUERYTYPE
def get_object_query_type(id):
    response = requests.get(settings.API_BASE_URL + f'query-type/{id}/')

    if response.status_code == 200:
        query_type_data = response.json()
        return query_type_data
    else:
        print(f'Error al obtener el tipo de consulta: {response.content}')
        return None
    
def add_query_type(request):
    if request.method == 'POST':
        form = QueryTypeForm(request.POST, request.FILES)
        if form.is_valid():
            error_message = None  # Inicializamos la variable error_message
            try:
                serializer = QueryTypeSerializer(data=form.cleaned_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                messages.success(request, 'Tipo de consulta agregada exitosamente.')
                return redirect('list_query_type')
            except serializers.ValidationError as e:
                form.add_error('name', e.detail['name'][0])  # Agregar mensaje de error al campo 'name'
        else:
            error_message = "Error en los datos del formulario"
        data = {
            'form': form,
            'error_message': error_message
        }
    else:
        data = {
            'form': QueryTypeForm()
        }

    return render(request, 'app/querytype/add.html', data)

def list_query_type(request):
    response = requests.get(settings.API_BASE_URL + 'query-type/')
    query_types = response.json()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(query_types, 5)
        query_types = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity': query_types,
        'paginator': paginator
    }
    return render(request, 'app/querytype/list.html', data)

def update_query_type(request, id):
    querytype_data = get_object_query_type(id)

    if querytype_data:
        error_message = ""

        if request.method == 'POST':
            form = QueryTypeForm(request.POST)

            if form.is_valid():
                name = form.cleaned_data['name']

                # Verificar si existe una categoría con el mismo nombre a través de la API
                response = requests.get(settings.API_BASE_URL + f'query-type/?name={name}')

                if response.status_code == 200:
                    existing_querytype = response.json()

                    if existing_querytype:
                        # Verificar si alguna categoría tiene un nombre diferente al nombre actual
                        for existing_querytype in existing_querytype:
                            if existing_querytype['name'] == name and existing_querytype['id'] != int(id):
                                form.add_error('name', 'Este tipo de consulta ya existe')
                                error_message = "Este tipo de consulta ya existe"
                                print("existing_querytype['name']: ", existing_querytype['name'])
                                print("name: ", name)
                                break  # Salir del bucle si se encuentra una categoría existente

                    if not error_message:
                        description = form.cleaned_data['description']

                        # Crear un nuevo diccionario con los datos actualizados
                        updated_data = {
                            'name': name,
                            'description': description
                        }

                        # Actualizar la categoría a través de la API
                        update_url = settings.API_BASE_URL + f'query-type/{id}/'
                        response = requests.put(update_url, data=updated_data)

                        if response.status_code == 200:
                            print('Tipo de consulta actualizado exitosamente')
                            messages.success(request, "Modificado correctamente")
                            return redirect(to="list_query_type")
                        else:
                            print(f'Error al actualizar el tipo de consulta: {response.content}')
                            error_message = "Error al actualizar el tipo de consulta a través de la API"
                else:
                    print(f'Error al verificar la existencia de el tipo de consulta: {response.content}')
                    error_message = "Error al verificar la existencia de el tipo de consulta a través de la API"
            else:
                error_message = "Error en los datos del formulario"
        else:
            form = QueryTypeForm(initial=querytype_data)
            error_message = ""

        data = {
            'form': form,
            'error_message': error_message
        }

        return render(request, 'app/querytype/update.html', data)
    else:
        # Manejar el caso si no se puede obtener la categoría de la API
        messages.error(request, "Error al obtener el tipo de consulta de la API")
        return redirect(to="list_query_type")
    
def delete_query_type(request, id):
    querytype_data = get_object_query_type(id)

    if querytype_data:
        querytype = QueryType(id=querytype_data['id'])  # Crear una instancia de Product solo con el ID

        # Realizar una solicitud DELETE a la API para eliminar el producto
        delete_response = requests.delete(settings.API_BASE_URL + f'query-type/{id}/')

        if delete_response.status_code == 204:
            querytype.delete()
            messages.success(request, "Eliminado correctamente")
            return redirect(to="list_query_type")
        else:
            # Manejar el caso de error en la solicitud DELETE
            print(f'Error al eliminar el tipo de consulta: {delete_response.content}')
            error_message = "Error al eliminar el tipo de consulta a través de la API"
            data = {
                'form': QueryTypeForm(instance=querytype),
                'error_message': error_message
            }
            return render(request, 'app/query-type/update.html', data)
    else:
        # Manejar el caso de error al obtener el producto
        error_message = "Error al obtener el tipo de consulta a través de la API"
        data = {
            'error_message': error_message
        }
        return render(request, 'app/query-type/update.html', data)

#VISTAS DE PRODUCT
def get_object_product(id):
    response = requests.get(settings.API_BASE_URL + f'product/{id}/')

    if response.status_code == 200:
        product_data = response.json()
        product_data.pop('image', None)  # Eliminar el campo de imagen del JSON
        return product_data
    else:
        print(f'Error al obtener el producto: {response.content}')
        return None
    
@permission_required('app.add_product') 
def add_product(request):
    if request.method == 'POST':
        error_message = ""
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']

            # Verificar si existe un producto con el mismo nombre a través de la API
            response = requests.get(settings.API_BASE_URL + f'product/?name={name}')

            if response.status_code == 200:
                existing_products = response.json()

                if existing_products:
                        # Verificar si algún producto tiene un nombre diferente al nombre actual
                        for existing_product in existing_products:
                            if existing_product['name'] == name and existing_product['id'] != id:
                                form.add_error('name', 'Este producto ya existe')
                                error_message = "Este producto ya existe"
                                print("existing_product['name']: ", existing_product['name'])
                                print("name: ", name)
                                break  # Salir del bucle si se encuentra un producto existente
                if not error_message:
                    price = form.cleaned_data['price']
                    description = form.cleaned_data['description']
                    is_new = form.cleaned_data['is_new']
                    category_id = form.cleaned_data['category'].id
                    stock = form.cleaned_data['stock']
                    is_featured = form.cleaned_data['is_featured']
                    image = form.cleaned_data['image']
                    is_rentable = form.cleaned_data['is_rentable']

                    product_data = {
                        'name': name,
                        'price': price,
                        'description': description,
                        'is_new': is_new,
                        'category': category_id,
                        'stock': stock,
                        'is_featured': is_featured,
                        'is_rentable': is_rentable,
                    }

                    response = requests.post(
                        settings.API_BASE_URL + 'product/',
                        data=product_data,
                        files={'image': image}
                    )

                    if response.status_code == 201:
                        print('Producto creado exitosamente')
                        messages.success(request, 'Producto agregado exitosamente.')
                        return redirect('list_product')
                    else:
                        print(f'Error al crear el producto: {response.content}')
                        error_message = "Error al crear el producto a través de la API"
            else:
                print(f'Error al verificar la existencia del producto: {response.content}')
                error_message = "Error al verificar la existencia del producto a través de la API"
        else:
            error_message = "Error en los datos del formulario"
        data = {
            'form': form,
            'error_message': error_message
        }
    else:
        data = {
            'form': ProductForm()
        }
    return render(request, 'app/product/add.html', data)

@permission_required('app.view_product')
def list_product(request):
    name_filter = request.GET.get('name', '')
    category_filter = request.GET.get('category', '')

    params = {}
    if name_filter:
        params['name'] = name_filter
    if category_filter:
        params['category'] = category_filter

    response = requests.get(settings.API_BASE_URL + 'product/', params=params)
    if response.status_code == 200:
        products = response.json()
    else:
        products = []

    paginator = Paginator(products, 5)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    response = requests.get(settings.API_BASE_URL + 'category/')
    categories = response.json()

    data = {
        'entity': products,
        'paginator': paginator,
        'name_filter': name_filter,
        'category_filter': category_filter,
        'categories': categories,
    }
    return render(request, 'app/product/list.html', data)

@permission_required('app.change_product')
def update_product(request, id):
    product_data = get_object_product(id)

    if product_data:
        error_message = ""

        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)

            if form.is_valid():
                name = form.cleaned_data['name']

                # Verificar si existe un producto con el mismo nombre a través de la API
                response = requests.get(settings.API_BASE_URL + f'product/?name={name}')

                if response.status_code == 200:
                    existing_products = response.json()

                    if existing_products:
                        # Verificar si algún producto tiene un nombre diferente al nombre actual
                        for existing_product in existing_products:
                            if existing_product['name'] == name and existing_product['id'] != id:
                                form.add_error('name', 'Este producto ya existe')
                                error_message = "Este producto ya existe"
                                print("existing_product['name']: ", existing_product['name'])
                                print("name: ", name)
                                break  # Salir del bucle si se encuentra un producto existente

                    if not error_message:
                        description = form.cleaned_data['description']
                        price = form.cleaned_data['price']
                        is_new = form.cleaned_data['is_new']
                        category_id = form.cleaned_data['category'].id
                        stock = form.cleaned_data['stock']
                        is_featured = form.cleaned_data['is_featured']
                        image = form.cleaned_data['image']
                        is_rentable = form.cleaned_data['is_rentable']

                        # Crear un nuevo diccionario con los datos actualizados
                        updated_data = {
                            'name': name,
                            'description': description,
                            'price': price,
                            'is_new': is_new,
                            'category': category_id,
                            'stock': stock,
                            'is_featured': is_featured,
                            'is_rentable': is_rentable
                        }

                        # Actualizar el producto a través de la API
                        update_url = settings.API_BASE_URL + f'product/{id}/'
                        files = {'image': image}  # Archivo adjunto
                        response = requests.put(update_url, data=updated_data, files=files)

                        if response.status_code == 200:
                            print('Producto actualizado exitosamente')
                            messages.success(request, "Modificado correctamente")
                            return redirect(to="list_product")
                        else:
                            print(f'Error al actualizar el producto: {response.content}')
                            error_message = "Error al actualizar el producto a través de la API"
                else:
                    print(f'Error al verificar la existencia del producto: {response.content}')
                    error_message = "Error al verificar la existencia del producto a través de la API"
            else:
                error_message = "Error en los datos del formulario"
        else:
            form = ProductForm(initial=product_data)
            error_message = ""

        data = {
            'form': form,
            'error_message': error_message
        }

        return render(request, 'app/product/update.html', data)
    else:
        # Manejar el caso si no se puede obtener el producto de la API
        messages.error(request, "Error al obtener el producto de la API")
        return redirect(to="list_product")

@permission_required('app.delete_product')
def delete_product(request, id):
    product_data = get_object_product(id)

    if product_data:
        product = Product(id=product_data['id'])  # Crear una instancia de Product solo con el ID

        # Realizar una solicitud DELETE a la API para eliminar el producto
        delete_response = requests.delete(settings.API_BASE_URL + f'product/{id}/')

        if delete_response.status_code == 204:
            product.delete()
            messages.success(request, "Eliminado correctamente")
            return redirect(to="list_product")
        else:
            # Manejar el caso de error en la solicitud DELETE
            print(f'Error al eliminar el producto: {delete_response.content}')
            error_message = "Error al eliminar el producto a través de la API"
            messages.error(request, error_message)
            return redirect(to="list_product")  # Redireccionar a la página de listado con mensaje de error
    else:
        # Manejar el caso de error al obtener el producto
        error_message = "Error al obtener el producto a través de la API"
        messages.error(request, error_message)
        return redirect(to="list_product")  # Redireccionar a la página de listado con mensaje de error

def product_detail(request, id):
    # Realizar una solicitud GET a la API para obtener los detalles del producto
    response = requests.get(settings.API_BASE_URL + f'product/{id}/')

    if response.status_code == 200:
        product_data = response.json()

        # Obtener la instancia de Category a través de la API
        category_id = product_data['category']
        category_data = get_object_category(category_id)

        if category_data:
            # Crear el objeto Category con los datos obtenidos de la API
            category = Category(**category_data)

            # Remover el campo 'category_name' del diccionario product_data
            product_data.pop('category_name', None)

            # Actualizar el campo 'category' en product_data con la instancia de Category
            product_data['category'] = category

            # Crear el objeto Product con los datos actualizados
            product = Product(**product_data)

            data = {
                'product': product
            }
            return render(request, 'app/product/detail.html', data)
        else:
            # Manejar el caso si no se puede obtener la categoría de la API
            error_message = "Error al obtener la categoría de la API"
            return render(request, 'app/product/detail.html', {'error_message': error_message})
    else:
        # Manejar el caso de error en la solicitud
        print(f'Error al obtener los detalles del producto: {response.content}')
        error_message = "Error al obtener los detalles del producto a través de la API"
        return render(request, 'app/product/detail.html', {'error_message': error_message})

#VISTA DE REGISTRO NO API
def register(request):
    data = {
        'form': CustomUserCreationForm()
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(
                username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            login(request, user)
            messages.success(request, "Te has registrado correctamente")
            # redirigir al home
            return redirect(to="home")
        data["form"] = formulario
    return render(request, 'registration/register.html', data)

#METODOS DEL CARRITO NO API
def add_prod_cart(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)

    if product.stock <= 0:
        messages.error(request, "Error: Product is out of stock.")
    elif cart.get_product_quantity(product) >= product.stock:
        messages.error(request, "Error: Maximum stock limit reached.")
    else:
        cart.add(product)
        # messages.success(request, "Product added to cart successfully.")

    return redirect(to="Cart")

def del_prod_cart(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    cart.delete(product)
    return redirect(to="Cart")

def subtract_product_cart(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    cart.subtract(product)
    return redirect("Cart")

def clean_cart(request):
    cart = Cart(request)
    cart.clean()
    return redirect("Cart")

def cart_page(request):
    products = Product.objects.all()
    data = {
        'products': products
    }

    return render(request, 'app/cart_page.html', data)

def buy_confirm(request):
    cart = Cart(request)
    cart.buy()
    cart.clean()
    return redirect('cart')

#VISTAS CATEGORY
def get_object_category(id):
    response = requests.get(settings.API_BASE_URL + f'category/{id}/')

    if response.status_code == 200:
        category_data = response.json()
        category_data.pop('image', None)
        return category_data
    else:
        print(f'Error al obtener la categoria: {response.content}')
        return None

@permission_required('app.add_category')
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            error_message = None  # Inicializamos la variable error_message
            try:
                serializer = CategorySerializer(data=form.cleaned_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                messages.success(request, 'Categoría agregada exitosamente.')
                return redirect('list_category')
            except serializers.ValidationError as e:
                form.add_error('name', e.detail['name'][0])  # Agregar mensaje de error al campo 'name'
        else:
            error_message = "Error en los datos del formulario"
        data = {
            'form': form,
            'error_message': error_message
        }
    else:
        data = {
            'form': CategoryForm()
        }

    return render(request, 'app/category/add.html', data)

@permission_required('app.view_category')
def list_category(request):
    response = requests.get(settings.API_BASE_URL + 'category/')
    categories = response.json()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(categories, 5)
        categories = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity': categories,
        'paginator': paginator
    }
    return render(request, 'app/category/list.html', data)

@permission_required('app.change_category')
def update_category(request, id):
    category_data = get_object_category(id)

    if category_data:
        error_message = ""

        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES)

            if form.is_valid():
                name = form.cleaned_data['name']

                # Verificar si existe una categoría con el mismo nombre a través de la API
                response = requests.get(settings.API_BASE_URL + f'category/?name={name}')

                if response.status_code == 200:
                    existing_categories = response.json()

                    if existing_categories:
                        # Verificar si alguna categoría tiene un nombre diferente al nombre actual
                        for existing_category in existing_categories:
                            if existing_category['name'] == name and existing_category['id'] != int(id):
                                form.add_error('name', 'Esta categoría ya existe')
                                error_message = "Esta categoría ya existe"
                                print("existing_category['name']: ", existing_category['name'])
                                print("name: ", name)
                                break  # Salir del bucle si se encuentra una categoría existente

                    if not error_message:
                        description = form.cleaned_data['description']
                        image = form.cleaned_data['image']

                        # Crear un nuevo diccionario con los datos actualizados
                        updated_data = {
                            'name': name,
                            'description': description
                        }

                        # Actualizar la categoría a través de la API
                        update_url = settings.API_BASE_URL + f'category/{id}/'
                        files = {'image': image}  # Archivo adjunto
                        response = requests.put(update_url, data=updated_data, files=files)

                        if response.status_code == 200:
                            print('Categoría actualizada exitosamente')
                            messages.success(request, "Modificado correctamente")
                            return redirect(to="list_category")
                        else:
                            print(f'Error al actualizar la categoría: {response.content}')
                            error_message = "Error al actualizar la categoría a través de la API"
                else:
                    print(f'Error al verificar la existencia de la categoría: {response.content}')
                    error_message = "Error al verificar la existencia de la categoría a través de la API"
            else:
                error_message = "Error en los datos del formulario"
        else:
            form = CategoryForm(initial=category_data)
            error_message = ""

        data = {
            'form': form,
            'error_message': error_message
        }

        return render(request, 'app/category/update.html', data)
    else:
        # Manejar el caso si no se puede obtener la categoría de la API
        messages.error(request, "Error al obtener la categoría de la API")
        return redirect(to="list_category")
    
@permission_required('app.delete_category')
def delete_category(request, id):
    category_data = get_object_category(id)

    if category_data:
        category = Category(id=category_data['id'])  # Crear una instancia de Product solo con el ID

        # Realizar una solicitud DELETE a la API para eliminar el producto
        delete_response = requests.delete(settings.API_BASE_URL + f'category/{id}/')

        if delete_response.status_code == 204:
            category.delete()
            messages.success(request, "Eliminado correctamente")
            return redirect(to="list_category")
        else:
            # Manejar el caso de error en la solicitud DELETE
            print(f'Error al eliminar la categoria: {delete_response.content}')
            error_message = "Error al eliminar la categoria a través de la API"
            data = {
                'form': CategoryForm(instance=category),
                'error_message': error_message
            }
            return render(request, 'app/category/update.html', data)
    else:
        # Manejar el caso de error al obtener el producto
        error_message = "Error al obtener la categoria a través de la API"
        data = {
            'error_message': error_message
        }
        return render(request, 'app/category/update.html', data)

#PANEL DE ADMIN
def admin_panel(request):

    return render(request, 'app/admin_panel.html')

def pago(request):
    return render(request, "app/pago.html")

def user_login(request):
    global tok
    datos={
        'form':LoginForm()
    }
    if(request.method == 'POST'):
        form = LoginForm(request.POST)
        if form.is_valid():
            usernameU = request.POST['usrN']
            passwordU = request.POST['pswrdN']
            user = authenticate(username=usernameU,password=passwordU)
            if user is not None:
                login(request,user)
                body= {"username": usernameU ,"password" : passwordU} #se genera json con info de usuario creado
                r = requests.post('http://127.0.0.1:8000/API/login',data=json.dumps(body)) # se realiza la creacion de token
                tok=r.text
                return render(request, "app/home.html")
    return render(request,"registration/login.html",datos)

def Recuperar(request):
    return render(request,"registration/Recuperar.html")

#se crea usuario nuevo y token
def Registrar(request): 
    global tok
    datos={
        'form':UsuariosForm()
    }
    if(request.method == 'POST'):
        form=UsuariosForm(request.POST)
        if form.is_valid():
            #obtiene los datos del usuario desde formulario
            usernameN = form.cleaned_data.get('usrN')
            passwordN = form.cleaned_data.get('pswrdN')
            passwordN2= form.cleaned_data.get('pswrdN2')
            try:
                #se verifica existencia del usuario
                user = User.objects.get(username = usernameN)
            except User.DoesNotExist:
                #si no existe se genera un nuevo usuario validando si es que las pswrd son identicas
                if(passwordN == passwordN2):
                    user = User.objects.create_user(username=usernameN,email=usernameN,password=passwordN)
                    user = authenticate(username=usernameN, password=passwordN) #autentifican las credenciales del usuario
                    #se logea al usuario nuevo
                    login(request,user)
                    #comienzo de creacion de token
                    body= {"username": usernameN ,"password" : passwordN} #se genera json con info de usuario creado
                    r = requests.post('http://127.0.0.1:8000//API/login',data=json.dumps(body)) # se realiza la creacion de token
                    tok=r.text #se imprime token en forma  de debug
                    #fin creacion token
                    return render(request, "app/home.html")
    return render(request,"registration/Registrar.html",datos)

def desconectar(request):
    logout(request)
    return redirect('login') 

@csrf_exempt
def update_last_order_paid_status(user):
    try:
        last_order = Order.objects.filter(user=user).latest('id')
        last_order.pagado = True
        last_order.save()
    except Order.DoesNotExist:
        pass 

def payment_success(request):
    if request.method == 'POST':
        # Obtener el usuario conectado actualmente
        user = request.user if request.user.is_authenticated else None
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        accumulated = request.POST.get('accumulated')

        # Crear la instancia de la orden
        order = Order(user=user, name=name, address=address, phone=phone, accumulated=accumulated)
        order.save()

        # Obtener los productos del carro de compras
        cart_items = request.session.get('cart', {}).items()

        # Agregar los productos a la orden
        for key, value in cart_items:
            product_name = value.get('product_name')
            product_price = value.get('product_price')
            amount = value.get('amount')

            # Crear la instancia del producto de la orden y establecer la relación con la orden
            order_item = OrderItem(order=order, product_name=product_name, product_price=product_price, amount=amount)
            order_item.save()

        # Lógica adicional, como enviar un correo electrónico de confirmación, generar una factura, etc.

        return render(request, 'app/payment_success.html')

    return render(request, 'app/pago.html')
  
def order_list(request):
    orders = Order.objects.prefetch_related('orderitem_set').all()
    page = request.GET.get('page', 1)

    # Filtros por rango de fecha
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        orders = orders.filter(fecha__range=[start_date, end_date])

    # Filtro por nombre de OrderItem
    order_item_name = request.GET.get('order_item_name')
    if order_item_name:
        orders = orders.filter(orderitem__product_name__icontains=order_item_name)

    total_accumulated = orders.aggregate(total_accumulated=Sum('accumulated'))['total_accumulated']

    # Obtener el total de productos vendidos
    total_products_sold = OrderItem.objects.filter(order__in=orders).aggregate(total_sold=Sum('amount'))['total_sold']

    # Obtener los 4 productos más vendidos considerando los filtros
    top_products = OrderItem.objects.filter(order__in=orders).values('product_name').annotate(total_amount=Count('product_name')).order_by('-total_amount')[:4]

    paginator = Paginator(orders, 5)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    data = {
        'entity': orders,
        'paginator': paginator,
        'total_accumulated': total_accumulated,
        'total_products_sold': total_products_sold,
        'top_products': top_products
    }
    return render(request, 'app/order_list.html', data)

def list_rental_order(request):
    response = requests.get(settings.API_BASE_URL + 'rental-orders/')
    rental_orders = response.json()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(rental_orders, 5)
        rental_orders = paginator.page(page)
    except:
        raise Http404

    data = {
        'entity': rental_orders,
        'paginator': paginator
    }
    return render(request, "app/rental_order/list.html", data)
