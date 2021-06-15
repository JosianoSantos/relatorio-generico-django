import csv
import datetime
from decimal import Decimal

import xlwt
from django.db import models
from django.http import HttpResponse


def imprimir_xls(nome_arquivo, queryset, campos):
    """Exemplo de passagem dos parâmetros:
    campos = ['username', 'first_name', 'last_name', 'email']
    exemplo de queryset - User.objects.all().values_list('username', 'first_name', 'last_name', 'email')"""

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="{0}.xls"'.format(nome_arquivo[:30])

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet(nome_arquivo[:30])

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    label_campos = [campo.get_label for campo in campos]

    for col_num in range(len(label_campos)):
        ws.write(row_num, col_num, label_campos[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    lista = [[] for i in range(len(queryset))]

    i = 0
    for object in queryset:
        for campo in campos:
            field = getattr(object, campo.campo)
            if isinstance(field, datetime.datetime):
                field = field.strftime('%d/%m/%Y %H:%M')
            if isinstance(field, datetime.date):
                field = field.strftime('%d/%m/%Y')
            if isinstance(field, Decimal):
                field = '{0:f}'.format(field).replace('.', ',')
            if isinstance(field, bool) and field is True:
                field = 'Ativo'
            if isinstance(field, bool) and field is False:
                field = 'Inativo'
            if isinstance(field, models.Model):
                field = field.__str__()
            lista[i].append(field)
        i += 1

    for object in lista:
        row_num += 1
        for col_num in range(len(object)):
            ws.write(row_num, col_num, object[col_num], font_style)

    wb.save(response)
    return response


def imprimir_csv(nome_arquivo, queryset, campos):
    """Exemplo de passagem dos parâmetros:
    campos = ['username', 'first_name', 'last_name', 'email']
    exemplo de queryset - User.objects.all().values_list('username', 'first_name', 'last_name', 'email')"""

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(nome_arquivo)

    writer = csv.writer(response)
    writer.writerow(campos)

    for index in queryset:
        writer.writerow(index)

    return response
