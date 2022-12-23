from django.db import models
from category.models import Category
from accounts.models import Account
# Create your models here.
from django.db.models import Avg, Count
from django.urls import reverse


class Product(models.Model):
    product_name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    images = models.ImageField(upload_to='pictures/products')
    alt_images = models.ImageField(upload_to='pictures/products', blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_details', args=[self.category.url, self.slug])

    def __str__(self):
        return self.product_name

#  TO GET THE AVERAGE REVIEWS OF THE REVIEW_RATING TABLE
    def average_review(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

#  TO GET THE TOTAL NUMBER OF REVIEWS FOR A PRODUCT
    def review_count(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(total=Count('id'))
        total = 0
        if reviews['total'] is not None:
            total = int(reviews['total'])
        return total


class VariationManager(models.Manager):  # To get separate values for color and size
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category = (
    ('color', 'color'),
    ('size', 'size'),
)


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'


class BannerGallery(models.Model):
    subtitle = models.TextField(max_length=500, blank=True)
    heading = models.TextField(max_length=500, blank=True)
    description = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to='banner/images', max_length=255)

    def __str__(self):
        return self.heading

    class Meta:
        verbose_name = 'bannergallery'
        verbose_name_plural = 'banner gallery'


class ContactPage(models.Model):
    email = models.EmailField(max_length=500)
    subject = models.CharField(max_length=500)
    message = models.TextField(max_length=500)
