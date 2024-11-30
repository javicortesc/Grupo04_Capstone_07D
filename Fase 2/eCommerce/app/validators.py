from django.forms import ValidationError

class MaxSizeFileValidator:
    def __init__(self,max_file_size=20):
        self.max_file_size = max_file_size

    def __call__(self, value):
       size = value.size
       max_size =  self.max_file_size * 1048576

       if size > max_size:
           raise ValidationError("El tamaño maximo del archivo debe ser de {self.max_file_size}MB")
       return value
    