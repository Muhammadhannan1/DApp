from django.db import models
from django.core.validators import MinValueValidator,FileExtensionValidator
# Create your models here.


class Category(models.Model):
    Name = models.CharField(max_length=15)




class SubCategory(models.Model):
    Name = models.CharField(max_length=15)
    category = models.ForeignKey(Category,on_delete=models.PROTECT, blank=True,default=9)



class Product(models.Model):
    Name =models.CharField(max_length=50)
    Description =models.TextField()
    Hash = models.CharField(max_length=100)
    subCategory = models.ForeignKey(SubCategory,on_delete=models.PROTECT, blank=True ,default=9)
    price = models.IntegerField(validators=[MinValueValidator(100)],default=100)
    image = models.ImageField(validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],null=True)
    exists = models.BooleanField(default=False)
