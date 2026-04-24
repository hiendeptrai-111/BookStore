from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_blacklisted_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_type', models.CharField(
                    choices=[('percent', 'Phần trăm'), ('fixed', 'Số tiền cố định')],
                    max_length=10,
                )),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('min_order_value', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('max_uses', models.IntegerField(default=0)),
                ('used_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'discount_codes',
            },
        ),
    ]
