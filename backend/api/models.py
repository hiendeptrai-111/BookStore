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
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)

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
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

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


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question[:80]

    class Meta:
        verbose_name = "FAQ"


class BlacklistedToken(models.Model):
    jti = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'blacklisted_tokens'

    @classmethod
    def cleanup_expired(cls):
        from django.utils import timezone
        cls.objects.filter(expires_at__lt=timezone.now()).delete()


class DiscountCode(models.Model):
    PERCENT = 'percent'
    FIXED = 'fixed'
    TYPE_CHOICES = [(PERCENT, 'Phần trăm'), (FIXED, 'Số tiền cố định')]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_uses = models.IntegerField(default=0)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'discount_codes'
