# App de geração de relatório genérico #

Essa app engloba as seguintes funções:
- Geração de relatórios com campos dinâmicos a partir dos models.
- Exporta esses relatórios em pdf e xls

##Como usar?##

1. Adicionar "RelatorioMixin" na ListView do modelo que deseja gerar relatórios

Exemplo:

class ClientesListView(ListView, RelatorioMixin):
     pass

2. No model, criar uma staticmethod chamado report_fields, com os fields ou properties que deseja exibir no relatório
 Exemplo:
   
@staticmethod

def report_fields():

    return [
        {'name': 'nome', 'label': 'Nome', 'default': True, 'css_class':''},
        {'name': 'telefone', 'label': 'Telefone', 'default': True, 'css_class':''},
        {'name': 'email', 'label': 'E-mail', 'default': True, 'css_class':''},
    ]


3. Passar a chave "relatorio" na requisição que chama a view (ClientesListView, no nosso exemplo do passo 1)


Melhorias futuras
É possível vincular ao usuário os campos a serem exibidos no relatório, para isso  