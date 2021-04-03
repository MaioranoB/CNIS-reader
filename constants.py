import re
from collections import namedtuple

re_seq = re.compile(r'^\d+')
re_nit = re.compile(r'\d{3}\.\d{5}\.\d{2}-\d')
re_codigo = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
re_codigo2 =re.compile(r'\d{2}\.\d{3}\.\d{3}')
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
NamedTuple = namedtuple('NamedTuple', 'seq nit codigo origem data1 data2 tipo ultRemu indicadores nb especie situacao competencia remu_ou_SalarioContrib contribuicao dataPgto indicadores2')

INDICADORES = ["PADM-EMPR","PREM-EMPR","PREM-FVIN","PREM-EXT","PREC-MENOR-MIN","PRES-EMPR","PADM-EMPR"]