import os

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from six import BytesIO
from xhtml2pdf import pisa


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL  # Typically /static/
    sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL  # Typically /static/media/
    mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def imprimir_pdf(empresa, template_name, queryset, campos, nome_arquivo='relatorio', download=True, extra_context={}):
    context = {}
    context['object_list_relatorio'] = queryset
    context['campos'] = campos
    context['empresa'] = empresa
    context.update(extra_context)

    template = get_template(template_name)
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        # Se o download for true, adiciona a opção para que retorna o arquivo par download, ao invés de abrir a página
        if download:
            response['Content-Disposition'] = 'attachment; filename="' + nome_arquivo + '.pdf"'

        return response
    return None
