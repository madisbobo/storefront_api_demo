from decimal import Decimal
from store .models import Product, Collection, Review
from rest_framework import serializers

##  SERIALIZING ##
# Serializer converts a model instance to a dictionary (Like a DTO)
# In Django REST Framework, there's a class called JSONRenderer, which takes a dictionary and turns it into a JSON object
# There are 4 ways to seralize relationships: Primary key, String, Nested object, Hyperlink

# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)


# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
#     price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
#     # collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all()) # Serializing relationship with Primary key
#     # collection = serializers.StringRelatedField() # Serializing relationship with String Related Field
#     collection = CollectionSerializer() # Serializing relationship with object

#     def calculate_tax(self, product: Product):
#         return product.unit_price * Decimal(1.1)


## MODEL SERIALIZING ##

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']

    product_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'inventory', 'description', 'unit_price', 'price_with_tax', 'collection']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
    
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description',]

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

    



