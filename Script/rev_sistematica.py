'''
rev_sistematica.py

Um programa criado para a última atividade de Metodologia de Pesquisa/Ifes Campus Serra 2021/2
Recebe: 
    str -> caminho de um diretório com artigos .pdf
    str -> caminho de um arquivo JSON com termos a serem encontrados nos arquivos

Exporta:
    Imagens de tabela e gráfico de pizza + relatório com ambas inclusas

Autor: Arthur Santos Miguel
'''

import plotly.graph_objects as graph
from PIL import Image
import pdfplumber
import json
import glob
import os

EXT = '.pdf'


def pega_arquivos():
    caminho = str(
        input(('Insira o caminho do diretório com os arquivos {0}: ').format(EXT)))
    return (caminho, glob.glob("{0}\*{1}".format(caminho, EXT)))

def pega_termos():
    caminho = str(
        input(('Insira o caminho do arquivo .JSON com os termos: ')))
    a = open(caminho)
    dados = json.load(a)
    try:
        lst_saida = dados['termos']
    except KeyError:
        lst_saida = dados[' termos']
    return lst_saida

def concatena_verticalmente(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst

def relacionar_termosxartigos(lista_arq, lista_termos):
    lista_relacionados, lista_palavras = [], []
    nome_arq = ''
    for arq in lista_arq:
        print('\nAnalisando arquivo {0} de {1}'.format(
            lista_arq.index(arq) + 1, len(lista_arq)))
        nome_arq = (arq.split("\\")[-1])
        pdf = pdfplumber.open(arq)
        i = 0
        try:
            while(1):
                pages = pdf.pages[i]
                text = pages.extract_text()
                lista_palavras = text.split(' ')
                for termo in lista_termos:
                    for palavra in lista_palavras:
                        if (termo == palavra and lista_relacionados.count((termo, nome_arq)) == 0):
                            lista_relacionados.append((termo, nome_arq))
                            break
                i = i+1
        except IndexError:
            pass
    return lista_relacionados

def listar_valores(arquivos, termos, relacoes):
    print('Calculando valores...')
    lista_valoresTabela, lista_aux = [], []
    for arq in arquivos:
        arq_nome_ext = (arq.split("\\")[-1])
        nome_arq = arq_nome_ext.replace(EXT, '')
        lista_aux.append(nome_arq)
    lista_valoresTabela.append(lista_aux)
    for ter in termos:
        lista_aux = []
        for arq in arquivos:
            arq_nome_ext = (arq.split("\\")[-1])
            ocorrencias = relacoes.count((ter, arq_nome_ext))
            lista_aux.append(ocorrencias)
        lista_valoresTabela.append(lista_aux)
    print('\n')
    return lista_valoresTabela

def criar_tabela(cab, val):
    print('Gerando tabela...')
    tabela = graph.Figure(data=[graph.Table(columnwidth=[1500, 300],
                                            header=dict(values=cab,
                                                        font_size=[14, 10]),
                                            cells=dict(values=val,
                                                       font_size=[12]))
                                ])
    return tabela

def criar_pizza(qntd_arq, lista_termos, resultado, titulo=''):
    print('Gerando gráfico de pizza...')
    valor, valores = 0, []
    del resultado[0]
    for i in range(len(lista_termos)):
        valor = (sum(resultado[i]) / qntd_arq) * 100
        valores.append(valor)
    pizza = graph.Figure(data=[graph.Pie(labels=lista_termos, values=valores)])
    pizza.update_layout(title=titulo)
    pizza.update_traces(hoverinfo='label+value',
                        texttemplate='%{value:.2f}%', textfont_size=qntd_arq)
    return pizza



def obter_dados():
    cabecalho, pdfs_match = [], []
    caminho, lista_arquivos = pega_arquivos()
    lista_termos = pega_termos()
    pdfs_match = relacionar_termosxartigos(lista_arquivos, lista_termos)
    cabecalho.append('Arquivo')
    cabecalho += lista_termos
    resultado = listar_valores(lista_arquivos, lista_termos, pdfs_match)
    return caminho, resultado, cabecalho, lista_arquivos, lista_termos


def criar_graficos(lista_arquivos, lista_termos, cabecalho, caminho_export, resultado):
    print('Criando os gráficos')
    tabela = criar_tabela(cabecalho, resultado)
    pizza = criar_pizza(len(lista_arquivos), lista_termos,
                        resultado, titulo="Porcentagem dos PDF's em que o termo aparece")
    if not os.path.exists(caminho_export):
        os.mkdir(caminho_export)
    dim = len(lista_arquivos) * 60
    caminho_tabela = caminho_export + "\\tabela.png"
    caminho_pizza = caminho_export + "\\pizza.png"
    print('Gerando relatório final...')
    tabela.write_image(caminho_tabela, width=dim, height=dim)
    pizza.write_image(caminho_pizza, width=dim, height=(dim/2))
    return caminho_tabela, caminho_pizza


def main():
    lista_arquivos, cabecalho = [], []
    caminho, resultado, cabecalho, lista_arquivos, lista_termos = obter_dados()
    caminho_saida = caminho + '\\relatorios'
    caminho_tab, caminho_piz = criar_graficos(
        lista_arquivos, lista_termos, cabecalho, caminho_saida, resultado)
    tab = Image.open(caminho_tab)
    piz = Image.open(caminho_piz)
    concatena_verticalmente(tab, piz).save(caminho_saida + '\\relatorio.jpg')
    print('\n \n Fim!')


if(__name__ == '__main__'):
    main()
