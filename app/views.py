from django.shortcuts import render,redirect
from django.views import View
from app import models
from datetime import date
from dateutil.relativedelta import relativedelta
import datetime,calendar
from django.contrib import messages
from django.db.models import Q,Sum
from django.http import HttpResponse

class AddTennant(View):
    def get(self,requests,id=0):
        if id:
            edit_data=models.AddTenantModel.objects.get(id=id)
        else:
            edit_data=""
        data=models.AddTenantModel.objects.all()
        frnt={
            'tan':data,
            'edit_data':edit_data
        }
        return render(requests,'app/add_tennant.html',frnt)
    def post(self,requests,id=0):
        data=requests.POST
        if id:
            dat=models.AddTenantModel.objects.get(id=id)
            dat.name=data.get('name')
            try:
                if data.get('phone').isdigit():
                    dat.phone_number=data.get('phone')
                else:
                    messages.success(requests,'Invalid Phone number')
                dat.save()
            except:
                messages.success(requests,'Phone number already presented')
                return  redirect('/addtennant')
        else:
            if data.get('phone').isdigit():
                name=data.get('name').title()
                try:
                    phone_number=data.get('phone')
                    toda=date.today()
                    Add=models.AddTenantModel(name=name,phone_number=phone_number,date=toda)
                    Add.save()
                except:
                    messages.success(requests,'Phone number already presented')
                    return  redirect('/addtennant')
            else:
                messages.success(requests,'Invalid Phone number')
        return redirect('/addtennant')
    def delete_data(requests,id=0):
        dat=models.AddTenantModel.objects.get(id=id)
        dat.delete()
        return redirect('/addtennant')


class AddExpense(View):
    def get(self,requests,id=0):
        e_name=models.AddTenantModel.objects.all()
        e_data=models.AddExpeseModel.objects.all()
        search=requests.GET.get('search')
        if search:
          if search.isdigit():
            frntdata=models.AddExpeseModel.objects.filter(Q(date__contains=search)|Q(item_price__contains=search))
          else:
            frntdata=models.AddExpeseModel.objects.filter(Q(expenser_name__name__icontains=search)|Q(item__icontains=search))  
        else:
            today=date.today()
            thismonth=today.month
            frntdata=models.AddExpeseModel.objects.filter(date__contains=thismonth)
        if id:
            edit_data=models.AddExpeseModel.objects.get(id=id)
        else:
            edit_data=""          
        totol=0
        today=date.today()
        thismonth=today.month
        this_month_data=models.AddExpeseModel.objects.filter(date__contains=thismonth)
        for ip in this_month_data:
            totol+=ip.item_price
        frnttime=today.strftime("%d-%m-%Y")
        if search:
            btn_change=True
        else:
            btn_change=False
        data={
            'e_name':e_name,
            'e_data':frntdata,
            'edit_data':edit_data,
            'today':[frnttime,totol,btn_change],

        }
        return render(requests,'app/add_expense.html', context=data)
    def post(self,requests,id=0):
        fnt=requests.POST
        if id:
            e_data=models.AddExpeseModel.objects.get(id=id)
            name_id=fnt.get('name')
            e_name=models.AddTenantModel.objects.get(id=name_id)
            e_data.expenser_name=e_name
            e_data.date=fnt.get('date')
            e_data.item=fnt.get('item')
            e_data.item_price=fnt.get('price')
            e_data.save()
            messages.success(requests,'Updated Successfuly!')
        else:    
            name_id=fnt.get('name')
            date=fnt.get('date')
            item=fnt.get('item')
            price=fnt.get('price')
            mas_name=models.AddTenantModel.objects.get(id=name_id)
            com=models.AddExpeseModel(expenser_name=mas_name,date=date,item=item,item_price=price)
            com.save()
        return redirect("/addexpense")
    def delete_data(self,id):
        del_item=models.AddExpeseModel.objects.get(id=id)
        del_item.delete()
        return redirect("/addexpense")

class CalcExpenseView(View):
    add_tenent=models.AddTenantModel.objects.all()
    def get(self,requests):
        this_month=date.today()
        previous_month=this_month-relativedelta(months=1)
        month_name=previous_month.strftime('%B')
        p_month=previous_month.month
        requests.session['pm']=p_month
        requests.session['month_name']=month_name
        p_month_data=models.AddExpeseModel.objects.filter(date__month=p_month).aggregate(Sum('item_price'))
        month_range=calendar.monthrange(previous_month.year,p_month)[1]
        requests.session['mr']=month_range
        totol=p_month_data['item_price__sum']
        requests.session['totol']=totol
        per_member=totol/self.add_tenent.count()
        requests.session['per_member']=per_member
        per_day=f'{(per_member/month_range):.2f}'
        requests.session['per_day']=float(per_day)
        calculate_expese_model=models.CalculateExpenseModel.objects.filter(date__month=p_month)
        if not calculate_expese_model:
            for dat in self.add_tenent:
                up=models.CalculateExpenseModel(name_of_expenser=dat,date=previous_month,Amount_to_be_paid=float(per_member))
                up.save()
        else:
            pass
        ans=[ (ds,'-',month_range) for ds in calculate_expese_model]
        front_data={
            'room_members':ans,
            'per_day':per_day,
            'per_member':per_member,
            'no_of_days':month_range,
            'month_name':month_name,
            'totol':totol
        }
        search=requests.GET.get('date')
        if search:
            try:
                date_split=search.split('-')
                og_date=datetime.datetime(int(date_split[0]),int(date_split[1]),int(date_split[2]))
                year=og_date.year
                month=og_date.month
                month_name=og_date.strftime('%B')
                data=models.CalculateExpenseModel.objects.filter(Q(date__month=month)&Q(date__year=year))
                ans=[ (ds,'-',month_range) for ds in data]
                totol=ans[0][0].totol_amount
                water_bill_se=ans[0][0].water_bill
                food_bill_se=ans[0][0].food_expense
                electric_bill_se=ans[0][0].electric_bill
                front_data={
                    'water_bill_se':water_bill_se,
                    'food_bill_se':food_bill_se,
                    'electric_bill_se':electric_bill_se,
                    'room_members':ans,
                    'per_day':' ',
                    'per_member':0,
                    'no_of_days':0,
                    'month_name':month_name,
                    'totol':totol,
                    'search':True
                }
            except Exception as e:
                print(e)
                messages.error(requests,'Data not available')
        return render(requests,'app/calculate_expense.html',front_data)

    def post(self,requests):
        data=requests.POST
        sum_of_water_food=eval(data['water'])+eval(data['food'])+eval(data['electric'])
        water_bill=float(data['water'])
        food_bill=float(data['food'])
        electric_bill=float(data['electric'])
        keys,values,month=[],[],[]
        totol=requests.session.get('totol',0)+sum_of_water_food
        per_day=requests.session.get('per_day',0)
        per_member=requests.session.get('per_member',0)
        month_range=requests.session.get('mr',0)
        p_month=requests.session.get('pm',0)
        this_month=date.today()
        previous_month=this_month-relativedelta(months=1)
        month_name=previous_month.strftime('%B')
        requests.session['month_name']=month_name
        count=self.add_tenent.count()
        try:
            for k,v in data.items():
                if k.isdigit():
                    keys.append(k)
                    if int(v)>month_range:
                        raise Exception("Invalid number")
                    elif int(v)==0:
                        values.append(month_range)
                        month.append(month_range-int(v))
                    elif int(v)==month_range:
                        values.append(0)
                        month.append(month_range-int(v))
                        count-=1
                    else:
                        values.append(int(v))
                        month.append(month_range-int(v))
            average=totol/count
            print(count)
            per_day=f'{(average/month_range):.2f}'
            # print(average,per_day,values)
            for i in range(len(values)):
                if values[i]:
                    values[i]=(average)-(eval(per_day)*values[i])
                    # print(values[i])
            final_cal=totol-sum(values)
            final_cal_2=final_cal/count
            print(values)
            ans=[f'{(final_cal_2+j):.2f}' if j else 0 for j in values]
            for kr in range(len(keys)):
                up_d=models.CalculateExpenseModel.objects.filter(date__month=p_month).get(id=keys[kr])
                up_d.Amount_to_be_paid=float(ans[kr])
                up_d.water_bill=water_bill
                up_d.food_expense=food_bill
                up_d.electric_bill=electric_bill
                up_d.no_of_days=month[kr]
                up_d.totol_amount=totol
                up_d.per_day=float(per_day)
                up_d.save()
            calc=models.CalculateExpenseModel.objects.filter(date__month=p_month)
            da_1=[da for da in calc]
            average=f'{average:.2f}'
            frnt_data={
                'totol':totol,
                'month_name':month_name,
                'room_members':zip(da_1,ans,month),
                'per_day':per_day,
                'per_member':average,
                'water_bill':water_bill,
                'food_expense':food_bill,
                'electric_bill':electric_bill
            }
            return render(requests,'app/calculate_expense.html',frnt_data)
        except Exception as e:
            print(e)
            messages.error(requests,'Invalid Data')
            return redirect('/calcexpense')
class HomeView(View):
    def get(self,requests):
        month_name=requests.session.get('month_name')
        p_month=requests.session.get('pm',0)
        calc_expense=models.CalculateExpenseModel.objects.filter(date__month=p_month)
        water_bill=int(calc_expense[0].water_bill)
        Electric_bill=int(calc_expense[0].electric_bill)
        food_expense=int(calc_expense[0].food_expense)
        totol=int(calc_expense[0].totol_amount)
        final={}
        sum_person=models.AddExpeseModel.objects.filter(date__month=p_month).values('expenser_name__name').annotate(Sum('item_price'))
        for nam in calc_expense:
            for dat in sum_person:
                if nam.name_of_expenser.name==dat['expenser_name__name']:
                    print(nam.name_of_expenser.name,dat['expenser_name__name'],dat['item_price__sum'],nam.Amount_to_be_paid)
                    print({dat['expenser_name__name']:dat['item_price__sum']-nam.Amount_to_be_paid})
                    final.update({dat['expenser_name__name']:{'Totol_Amount':f'{nam.Amount_to_be_paid-dat['item_price__sum']:.2f}','Purchase_Amount':dat['item_price__sum']}})        
        print(final)
        data={
            'room_members':calc_expense,
            'month_name':month_name,
            'water':water_bill,
            'electric':Electric_bill,
            'food':food_expense,
            'totol':totol,
            'final':final
        }

        return render(requests,'app/home.html',data)
    def post(self,requests):
        return redirect('/')