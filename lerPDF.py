import re
from collections import namedtuple
import pdfplumber
from time import time
from tqdm import tqdm
import xlsxwriter

re_seq = re.compile(r'^\d+')
re_nit = re.compile(r'\d{3}\.\d{5}\.\d{2}-\d')
re_codigo = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
re_origem = re.compile(r'[A-Z]+[A-Z \.-]+')
re_datas = re.compile(r'(\d{2}/\d{2}/\d{4})( \d{2}/\d{2}/\d{4})?')
re_tipo = re.compile(r'[A-Z]{1}[a-z]+\s?[A-Z]?[a-z]+')
re_ultRemu = re.compile(r'\s\d{2}/\d{4}')
re_indicador = re.compile(r'([A-Z]{4}-[A-Z]{3,5}-?M?I?N?[ ,A-Z-]+)?$')
re_nb = re.compile(r'\d{10}')
re_especie = re.compile(r'\d{2} - [A-Z ]+')

re_remu = re.compile(r'(\d{2}/\d{4}) (\d+[0-9\.]*,\d{2})( [A-Z]{4}-[A-Z]{3,5}-?M?I?N?)?')
re_contrib = re.compile(r'(\d{2}/\d{4}) (\d{2}/\d{2}/\d{4}) (\d+[0-9\.]*,\d{2}) (\d+[0-9\.]*,\d{2}) ?([A-Z]{4}-[A-Z]{3,5}-?M?I?N?)?') #apenas o indicador ta como opcional, se por acaso nao tiver alguma da colunas o resultado vai estar errado
#re_SEQ = re.compile(r'(^\d{1,2}) (\d{3}\.\d{5}\.\d{2}-\d) (\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}) ([A-Z]+[A-Z \.-]+) (\d{2}/\d{2}/\d{4})( \d{2}/\d{2}/\d{4})? ([A-Z]{1}[a-z]+\s?[A-Z]?[a-z]+)( \d{2}/\d{4})?( [A-Z]{4}-[A-Z]{3,5}-?M?I?N?[ ,A-Z-]+)?')

#idTuple = namedtuple('idTuple','emissao nit data_nascimento cpf nome nome_mae')
ntupleSEQ = namedtuple('ntupleSEQ','seq nit codigo origem data1 data2 tipo ultRemu indicadores nb especie situacao')
ntupleREMU = namedtuple('ntupleREMU','competencia remu_ou_SalarioContrib contribuicao dataPgto indicadores')
NamedTuple = namedtuple('NamedTuple', 'seq nit codigo origem data1 data2 tipo ultRemu indicadores nb especie situacao vazio competencia remu_ou_SalarioContrib contribuicao dataPgto indicadores2')

INDICADORES = ["PADM-EMPR","PREM-EMPR","PREM-FVIN","PREM-EXT","PREC-MENOR-MIN","PRES-EMPR","PADM-EMPR"]


def extract_text(pdf_path):
    #t1 = time()
    with pdfplumber.open(pdf_path) as pdf:
        #Garantir que o pdf é válido antes de tudo
        pag1 = pdf.pages[0].extract_text()
        if pag1 == None or "Extrato Previdenciário" not in pag1:
            return False,False

        #Ler o cabeçalho e agrupar todas as pags do pdf
        pag1 = pag1.split("\n")
        id_filiado = get_id(pag1) #retorna (emissao,nit,data_nascimento,cpf,nome,nome_mae)
        texto = pag1[9:-1] #ignorar o cabeçalho e o rodape
        for i in tqdm(range(1,len(pdf.pages)), desc = "Extraindo texto do pdf"):
            pagina = pdf.pages[i].extract_text().split("\n")
            texto += pagina[9:-1]
        pdf.close()
        
    #print(f'Tempo de extrair todo o texto do pdf: {time()-t1} segundos')
    return id_filiado,texto

def get_id(pag_lista):
    emissao = pag_lista[4]

    infos = pag_lista[6].split() #['NIT:', '111.16912.07-9', 'CPF:', '277.181.587-72', 'Nome:', 'RENATO', 'LOSCHI', 'CRISAFULLI']
    nit,cpf = infos[1],infos[3]
    nome = " ".join(infos[5:])

    infos = pag_lista[7].split() #['Data', 'de', 'nascimento:', '19/10/1952', 'Nome', 'da', 'mãe:', 'CARLINDA', 'AUGUSTA', 'CRISAFULLI']
    data_nascimento = infos[3]
    nome_mae = " ".join(infos[7:])

    return emissao,nit,data_nascimento,cpf,nome,nome_mae

def readPDF(pdf_path):
    id_filiado,texto = extract_text(pdf_path)

    if id_filiado == False:
        return False,False

    #t1 = time()
    seqs = []
    for i,linha in enumerate(tqdm(texto,desc = 'Extraindo informações')):
        if linha.startswith("Seq. NIT"):
            
            seq = get_seqID(texto[i+1:i+3]) #mandar as duas proximas linhas(as vezes ocupa duas linhas)
            
            if texto[i + 2] == "Remunerações" or texto[i + 3] == "Remunerações": #+3 no caso de um indicador ocupar mais de uma linha
                linhas_remuneracoes = []
                    
                i_aux = i + 2
                prox_seq = False
                while not prox_seq:
                    if texto[i_aux][0].isdecimal():   #sempre começa com uma data da competencia
                        linhas_remuneracoes.append(texto[i_aux])        

                    elif texto[i_aux].startswith("Seq. NIT") or texto[i_aux].startswith("Legenda de Indicadores"):
                        prox_seq = True
                    i_aux += 1

                seq_remu = get_remuneracoes(linhas_remuneracoes,seq)
                seqs += seq_remu
                
            elif texto[i + 2] == "Contribuições" or texto[i + 3] == "Contribuições":
                linhas_contribuicoes = []

                prox_seq = False
                i_aux = i + 2 
                while not prox_seq:
                    if texto[i_aux][0].isdecimal(): #sempre começa com a data da competencia
                        linhas_contribuicoes.append(texto[i_aux])
                            
                    elif texto[i_aux].startswith("Seq. NIT") or texto[i_aux].startswith("Legenda de Indicadores"):
                        prox_seq = True
                    i_aux += 1

                seq_remu = get_contribuicoes(linhas_contribuicoes,seq)
                seqs+=seq_remu

            elif texto[i + 2].startswith("Seq. NIT") or texto[i + 3].startswith("Seq. NIT"): #seqs sem remu
                
                _seq,nit,codigo,origem,data1,data2,tipo,ultRemu,indicadores,nb,especie,situacao = seq
                seq_sem_remu = NamedTuple(_seq,nit,codigo,origem,data1,data2,tipo,ultRemu,indicadores,nb,especie,situacao,'','','','','','')
                seqs.append(seq_sem_remu)

            else:   #seq do tipo Benefício nao tem remuneraçao/contribuiçao?
                print("ERRO readPDF()")
    #print(f'Tempo de ler o todas as seqs: {time()-t1} segundos')
    return id_filiado,seqs

def get_seqID(linhas): #seq,nit,codigo,origem,data1,data2,tipo,ultima_remu,indicadores,nb,especie,situacao
    linha1 = linhas[0]
    linha2 = linhas[1]
    
    codigo,tipo,ultRemu,indicadores,nb,especie,situacao = '','','','','','',''

    
    seq = int(re_seq.search(linha1).group())
    nit = re_nit.search(linha1).group()
    data1,data2 = re_datas.findall(linha1)[0] #se nao achar a data2 retorna ['data1', '']
    
    final_origem = ''
    if linha2 == 'EMPR': #siglas = ["EMPR",] tem mais siglas, ajeitar isso dps 
        linha1+=linha2
        indicadores = ", ".join(re_indicador.findall(linha1))
    elif linha2.isupper(): #alem dos indicadores, so a origem tem todas as letras maiusculas
        final_origem = linha2
    else:
        indicadores = ", ".join(re_indicador.findall(linha1))
        
    
    if 'AUTÔNOMO' in linha1:
        origem = 'AUTÔNOMO'
        tipo = 'Autônomo'
        
    elif 'RECOLHIMENTO' in linha1:
        origem = 'RECOLHIMENTO'
        tipo = 'Contribuinte Individual' 
        
    elif 'Benefício' in linha1:
        origem = 'Benefício'
        situacao = 'CESSADO' #mudar isso dps
        nb = re_nb.search(linha1).group()
        especie = re_especie.search(linha1).group()
        
    else:
        codigo = re_codigo.search(linha1).group()
        origem = re_origem.search(linha1).group() + final_origem
        tipo = re_tipo.search(linha1).group()
        ultRemu = re_ultRemu.search(linha1)
        if ultRemu:
            ultRemu = ultRemu.group()
        else: ultRemu = ''
        #match = re_SEQ.findall(linha1)
        #seq,nit,codigo,origem,data1,data2,tipo,ultRemu,indicadores = match[0]


    
    return ntupleSEQ(seq,nit,codigo,origem,data1,data2,tipo,ultRemu,indicadores,nb,especie,situacao)

def get_remuneracoes(linhas,seqID): #retorna as remus com os dados da seq antes de cada uma 
    a,b,c,d,e,f,g,h,i,j,k,l = seqID
    
    lista_remu = []
    for linha in linhas: 
        matches = re_remu.findall(linha) #cada linha pode ter tres remuneraçoes
        for match in matches:
            competencia,remu_ou_SalarioContrib,indicador = match

            remu_ou_SalarioContrib = remu_ou_SalarioContrib.replace('.','').replace(',','.')
            lista_remu.append(NamedTuple(a,b,c,d,e,f,g,h,i,j,k,l,'',competencia,remu_ou_SalarioContrib,'','',indicador)) 

    return lista_remu

def get_contribuicoes(linhas,seqID):
    a,b,c,d,e,f,g,h,i,j,k,l = seqID

    lista_contribs = []
    for linha in linhas: 
        matches = re_contrib.findall(linha) #cada linha pode ter duas contribs
        for match in matches:
            competencia,data_pgto,contribuicao,remu_ou_SalarioContrib,indicadores = match

            contribuicao = contribuicao.replace('.','').replace(',','.')
            remu_ou_SalarioContrib = remu_ou_SalarioContrib.replace('.','').replace(',','.')
            lista_contribs.append(NamedTuple(a,b,c,d,e,f,g,h,i,j,k,l,'',competencia,remu_ou_SalarioContrib,contribuicao,data_pgto,indicadores))
            
    return lista_contribs

def to_exel(id_filiado,seqs,save_path):
    workbook = xlsxwriter.Workbook(save_path,{'strings_to_numbers': True}) #'default_date_format', None
    bold = workbook.add_format({'bold': 1})
    
    id_sheet = workbook.add_worksheet('ID')
    seqs_sheet = workbook.add_worksheet('Sequencias')
    
    id_column_index = ['Emissão','NIT','Data de Nascimento','CPF','Nome','Nome da mãe']
    seq_row_index = ["Seq","NIT","Código Emp.","Origem do Vinculo","Data Início","Data Fim","Tipo Filiado no Vínculo","Últ. Remun.","Indicadores","NB","Espécie","Situação","/","Competência","Remuneração ou Salário Contribuição","Contribuição","Data pgto","Indicadores2"]
    
    id_sheet.write_column(0,0,id_column_index,bold)
    id_sheet.write_column(0,1,id_filiado)
    
    seqs_sheet.write_row(0,0,seq_row_index,bold)
    for i in tqdm(range(len(seqs)), desc = 'Escrevendo a planilha'):
        seqs_sheet.write_row(i+1,0,seqs[i])

    workbook.close()
