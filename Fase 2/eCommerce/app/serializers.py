from .models import Product, Category, Contact, QueryType, RentalOrder
from rest_framework import serializers
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.dateformat import DateFormat

class CategorySerializer(serializers.ModelSerializer):

    def validate_name(self, value):
        instance = self.instance

        # Verificar si existe otro producto con el mismo nombre
        if instance is not None:
            exists = Category.objects.filter(name__iexact=value).exclude(pk=instance.pk).exists()
        else:
            exists = Category.objects.filter(name__iexact=value).exists()

        if exists:
            raise serializers.ValidationError("Esta categoria ya existe")

        return value
    
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(read_only=True, source="category.name")
    created_at = serializers.SerializerMethodField()

    def get_created_at(self, obj):
        # Obtener la fecha y hora en el formato deseado
        created_at = obj.created_at.astimezone(timezone.get_current_timezone())
        formatted_date = DateFormat(created_at).format("d-m-Y H:i")
        return formatted_date
    
    def validate_name(self, value):
        instance = self.instance

        # Verificar si existe otro producto con el mismo nombre
        if instance is not None:
            exists = Product.objects.filter(name__iexact=value).exclude(pk=instance.pk).exists()
        else:
            exists = Product.objects.filter(name__iexact=value).exists()

        if exists:
            raise serializers.ValidationError("Este producto ya existe")

        return value

    class Meta:
        model = Product
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    query_type_name = serializers.CharField(read_only=True, source="query_type.name")

    class Meta:
        model = Contact
        fields = '__all__'

    def create(self, validated_data):
        # Guardar los datos en la base de datos
        contact = Contact.objects.create(**validated_data)

        # Obtener los datos del formulario
        name = validated_data.get('name')
        email = validated_data.get('email')
        phone = validated_data.get('phone')
        message = validated_data.get('message')

        # Construir el mensaje de correo electrónico con los datos del formulario
        subject = 'Nuevo mensaje de contacto'
        email_message = f'''
            Se ha recibido un nuevo mensaje de contacto:
            Nombre: {name}
            Correo electrónico: {email}
            Teléfono: {phone}
            Mensaje: {message}
        '''
        from_email = 'erreapectm@gmail.com'  # Tu dirección de correo electrónico
        # La dirección de correo electrónico del destinatario
        to_email = 'dario.vera96@gmail.com'
        send_mail(subject, email_message, from_email, [to_email])

        return contact

class QueryTypeSerializer(serializers.ModelSerializer):

    def validate_name(self, value):
        instance = self.instance

        # Verificar si existe otro producto con el mismo nombre
        if instance is not None:
            exists = QueryType.objects.filter(name__iexact=value).exclude(pk=instance.pk).exists()
        else:
            exists = QueryType.objects.filter(name__iexact=value).exists()

        if exists:
            raise serializers.ValidationError("Este tipo de contacto ya existe")

        return value
    
    class Meta:
        model = QueryType
        fields = '__all__'

class RentalOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalOrder
        fields = '__all__'
    
