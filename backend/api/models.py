from django.db import models


class Authors(models.Model):
    author_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150)
    bio = models.TextField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'AUTHORS'


class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CATEGORIES'


class Publishers(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'PUBLISHERS'


class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    isbn = models.CharField(unique=True, max_length=20)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Authors, models.DO_NOTHING)
    category = models.ForeignKey(Categories, models.DO_NOTHING)
    publisher = models.ForeignKey(Publishers, models.DO_NOTHING)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    description = models.TextField(blank=True, null=True)  # thêm
    image_url = models.CharField(max_length=500, blank=True, null=True)  # thêm

    class Meta:
        managed = False
        db_table = 'BOOKS'

class Customers(models.Model):
    customer_id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=150)
    email = models.CharField(unique=True, max_length=150)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.IntegerField()
    created_at = models.DateField()

    class Meta:
        managed = False
        db_table = 'CUSTOMERS'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customers, models.DO_NOTHING)
    order_date = models.DateField()
    status = models.CharField(max_length=9)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'ORDERS'


class OrderItems(models.Model):
    item_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, models.DO_NOTHING)
    book = models.ForeignKey(Books, models.DO_NOTHING)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'ORDER_ITEMS'


class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Books, models.DO_NOTHING)
    quantity_in = models.IntegerField()
    quantity_out = models.IntegerField()
    transaction_date = models.DateField()
    note = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'INVENTORY'