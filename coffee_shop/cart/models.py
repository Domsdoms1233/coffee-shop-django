from django.db import models
from django.conf import settings
from products.models import Product
import uuid
from decimal import Decimal

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-created_at']

    def __str__(self):
        return f'Корзина пользователя {self.user.username}'

    @property
    def total_price(self):
        """Общая стоимость всех товаров в корзине"""
        return sum(Decimal(str(item.total_price)) for item in self.items.all())

    @property
    def total_quantity(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        """Очистка корзины"""
        self.items.all().delete()
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Количество'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ['cart', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.quantity} x {self.product.name} (корзина {self.cart.user.username})'

    @property
    def total_price(self):
        """Общая стоимость позиции"""
        return Decimal(str(self.product.price)) * self.quantity


class Order(models.Model):
    ORDER_STATUS = (
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    order_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name='Номер заказа'
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default='new',
        verbose_name='Статус'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Общая сумма'
    )
    foxcoins_used = models.PositiveIntegerField(
        default=0,
        verbose_name='Использовано Foxcoins'
    )
    address = models.TextField(
        verbose_name='Адрес доставки'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )
    comments = models.TextField(
        blank=True,
        verbose_name='Комментарии'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.order_number} ({self.user.username})"

    def save(self, *args, **kwargs):
        """Генерация номера заказа при создании"""
        if not self.order_number:
            self.order_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    @property
    def original_total(self):
        """Исходная сумма без учета Foxcoins"""
        return self.total_price + Decimal(str(self.foxcoins_used))


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за единицу'
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (заказ #{self.order.order_number})"

    @property
    def total_price(self):
        """Общая стоимость позиции в заказе"""
        return Decimal(str(self.price)) * self.quantity