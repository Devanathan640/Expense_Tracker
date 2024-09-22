from django.db import models

# Create your models here.


class AddTenantModel(models.Model):
    name=models.CharField(max_length=200,default='')
    phone_number=models.CharField(max_length=20,default="",unique=True)
    date=models.DateField(blank=True)

class AddExpeseModel(models.Model):
    expenser_name=models.ForeignKey(AddTenantModel,on_delete=models.CASCADE)
    date=models.DateField()
    item=models.CharField(max_length=300)
    item_price=models.IntegerField()
class CalculateExpenseModel(models.Model):
    name_of_expenser=models.ForeignKey(AddTenantModel,on_delete=models.CASCADE)
    Amount_to_be_paid=models.FloatField(default=0)
    date=models.DateField(null=True)
    water_bill=models.FloatField(default=0)
    food_expense=models.FloatField(default=0)
    electric_bill=models.FloatField(default=0)
    no_of_days=models.IntegerField(default=0)
    totol_amount=models.FloatField(default=0)
    per_day=models.FloatField(default=0)