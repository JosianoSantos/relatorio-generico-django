from datetime import datetime

from django.http import HttpResponse
from django.template.loader import get_template
from six import BytesIO
from xhtml2pdf import pisa

from relatoriobase.imprimir_pdf import imprimir_pdf, link_callback
from relatoriobase.imprimir_xls_csv import imprimir_xls


class RelatorioMixin(object):

    def __init__(self, *args, **kwargs):
        super(RelatorioMixin, self).__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.get_template_name_relatorio_list(request)

        if 'relatorio' in request.GET:
            # Criando atributo 'campos_usuario' para ser usado em toda a view
            # self.campos_usuario = self.request.session['usuario_empresa'] \
            #     .report_fields_app(app=self.request.resolver_match.app_name, modelo=self.model.__name__)

            self.campos_usuario = self.request.user \
                .report_fields_app(app=request.GET.get('app'), modelo=request.GET.get('modelo'))

        return super().dispatch(request, *args, **kwargs)

    def get_template_name_relatorio_list(self, request, *args, **kwargs):
        """Altera o template name para o relatorio. Caso o "template_name_relatorio"
        for declarado explicitamente na classe, o mesmo é utilizado, caso contrario, o template_name é alterado
        para a nomenclatura padrão para templates de relatorio"""
        if 'relatorio' in request.GET:
            try:
                self.template_name = self.template_name_relatorio_list
            except:
                self.template_name = self.template_name.replace('list.html', '').replace('_relatorio',
                                                                                         '') + 'relatorio_list.html'

    def get_template_name_relatorio_pdf(self):
        """Altera o template name para o pdf do relatorio. Caso o "template_name_relatorio_pdf"
        for declarado explicitamente na classe, o mesmo é utilizado, caso contrario, o template_name é alterado
        para a nomenclatura padrão para templates de relatorio"""

        try:
            return self.template_name_relatorio_pdf
        except:
            return self.template_name.replace('list.html', '').replace('_relatorio', '') + 'relatorio_pdf.html'

    def get_nome_arquivo_relatorio(self):
        """
        Se for definido o nome do arquivo (xls, pdf, etc) na view, utiliza o mesmo e,
        caso contrário usa um nome padrao para o arquivo. Sempre concatenando com a data de hoje
        """
        try:
            return self.nome_arquivo_relatorio.replace(' ', '_') + '_' + str(
                datetime.strftime(datetime.now(), '%d_%m_%Y'))
        except:
            return 'Relatorio_' + str(datetime.strftime(datetime.now(), '%d_%m_%Y'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'relatorio' in self.request.GET:
            queryset = self.get_queryset()

            context['campos'] = self.campos_usuario
            context['object_list_relatorio'] = queryset

        return context

    def get_extra_context_data(self):
        """
        use caso precise enviar outros parametros para o relatório, por exemplo: valor total... etc
        """
        return {}

    def get(self, request, *args, **kwargs):

        if 'acao_relatorio' in request.GET:
            try:
                empresa = request.session['empresa']
            except:
                empresa = None

            queryset = self.get_queryset()
            if request.GET['acao_relatorio'] == 'gerar_excel':
                # queryset_values_list = self.get_queryset().values_list(*[campo.campo for campo in self.campos_usuario])

                return imprimir_xls(queryset=queryset,
                                    campos=self.campos_usuario,
                                    nome_arquivo=self.get_nome_arquivo_relatorio())

            elif request.GET['acao_relatorio'] == 'gerar_pdf':

                return imprimir_pdf(empresa=empresa,
                                    template_name=self.get_template_name_relatorio_pdf(),
                                    queryset=queryset, campos=self.campos_usuario,
                                    nome_arquivo=self.get_nome_arquivo_relatorio(),
                                    extra_context=self.get_extra_context_data())

            elif request.GET['acao_relatorio'] == 'imprimir':

                return imprimir_pdf(empresa=empresa,
                                    template_name=self.get_template_name_relatorio_pdf(),
                                    queryset=queryset,
                                    campos=self.campos_usuario,
                                    download=False,
                                    extra_context=self.get_extra_context_data())

        return super().get(request, *args, **kwargs)


class RelatorioDetailMixin(object):

    def get(self, request, *args, **kwargs):
        try:
            empresa = request.session['empresa']
        except:
            empresa = None

        self.object = self.get_object()
        context = self.get_context_data()
        context['empresa'] = empresa
        template = get_template(self.template_name)
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return None
