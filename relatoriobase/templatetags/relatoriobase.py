from django import template
from django.apps import apps

register = template.Library()


@register.filter
def get_valor_campo(modelo, campo):
    """
    Recebe o modelo e retorna o valor de acordo com o campo passado por parametro
    """
    try:
        return getattr(modelo, campo)
    except Exception as e:
        return None


@register.inclusion_tag("relatoriobase/_modal_seleciona_fields_relatorio.html")
def modal_seleciona_fields_relatorio(request, app, modelo):
    """
    :param request:
    :param app:
    :param modelo:
    :return: Mostra a modal com os campos disponível para o relatório da app/modelo/usuario_empresa.
    Os campos checados são aqueles que o usuário já definiu.
    Exemplo de uso:
    {% load relatoriobase %}
    {%  modal_seleciona_fields_relatorio request=request app='ordemservico' modelo='ServicoRecorrente' %}
    """
    fields_usuario = request.user.report_fields_app(app=app, modelo=modelo)
    classe_modelo = apps.get_model(app, modelo)
    fields = list()
    for field in classe_modelo.report_fields():
        if 'campos' in request.GET:
            checked = [True for campo in request.GET.getlist('campos') if campo == field['name']]
        else:
            try:
                checked = bool(fields_usuario.filter(campo=field['name']))
            except Exception as e:
                checked = True

        fields.append(
            {'name': field['name'], 'label': field['label'],
             'checked': checked}
        )
    return {'fields': fields, 'app': app, 'modelo': modelo, 'request': request}
