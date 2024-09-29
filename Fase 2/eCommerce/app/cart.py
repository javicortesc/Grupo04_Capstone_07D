from .models import Product
from django.contrib import messages

class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart_items = self.session.get("cart")
        if not cart_items:
            self.session["cart"] = {}
            self.cart_items = self.session["cart"]
        else:
            self.cart_items = cart_items
    
    def add(self, product):
        product_id = str(product.id)
        if product_id not in self.cart_items.keys():
            self.cart_items[product_id] = {
                "product_id": product.id,
                "product_name": product.name,
                "product_price": product.price,
                "accumulated": product.price,
                "amount": 1,
            }
        else:
            if self.cart_items[product_id]["amount"] < product.stock:
                self.cart_items[product_id]["amount"] += 1
                self.cart_items[product_id]["accumulated"] += product.price
            else:
                messages.error(self.request, "Error: Maximum stock limit reached.")
                return
    
        self.save_cart()
    
    def save_cart(self):
        self.session["cart"] = self.cart_items
        self.session.modified = True

    def delete(self, product):
        product_id = str(product.id)
        if product_id in self.cart_items:
            del self.cart_items[product_id]
            self.save_cart()

    def subtract(self, product):
        product_id = str(product.id)
        if product_id in self.cart_items.keys():
            self.cart_items[product_id]["amount"] -= 1
            self.cart_items[product_id]["accumulated"] -= product.price
            if self.cart_items[product_id]["amount"] <= 0:
                self.delete(product)
                messages.success(self.request, "Producto Eliminado.")
            self.save_cart()

    def clean(self):
        self.session["cart"] = {}
        self.session.modified = True

    def buy(self):
        products = Product.objects.all()
        for key, value in self.session["cart"].items():
            for product in products:
                if int(value["product_id"]) == product.id:
                    product.stock -= int(value["amount"])
                    product.save()

    def get_product_quantity(self, product):
        product_id = str(product.id)
        if product_id in self.cart_items:
            return self.cart_items[product_id]["amount"]
        return 0