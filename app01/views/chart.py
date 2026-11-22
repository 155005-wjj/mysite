"""
数据统计可视化视图
"""
from django.db.models import Count, Sum
from django.shortcuts import render
from django.http import JsonResponse
from app01.models import Employee, Salary


def chart_index(request):
    """数据统计页面"""
    return render(request, "app01/chart.html")


def chart_depart_people(request):
    """AJAX接口：各部门人数分布"""
    queryset = Employee.objects.values("depart__title").annotate(
        count=Count("id")
    ).order_by()
    data = [{"name": row["depart__title"], "value": row["count"]} for row in queryset]
    return JsonResponse({"status": True, "data": data})


def chart_salary_trend(request):
    """AJAX接口：各月实发工资趋势"""
    queryset = Salary.objects.values("month").annotate(
        total=Sum("total")
    ).order_by("month")
    months = [row["month"] for row in queryset]
    totals = [float(row["total"]) for row in queryset]
    return JsonResponse({"status": True, "months": months, "totals": totals})
