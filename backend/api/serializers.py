from rest_framework import serializers
from .models import Books, Authors, Categories, Publishers

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = ['author_id', 'full_name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['category_id', 'name']

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publishers
        fields = ['publisher_id', 'name']

class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)

    class Meta:
        model = Books
        fields = [
            'book_id', 'isbn', 'title', 'price', 'stock_quantity',
            'description', 'image_url',          # thêm
            'author', 'author_name',
            'category', 'category_name',
            'publisher', 'publisher_name',
        ]