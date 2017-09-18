# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as BS
import requests
import json
import random
from xml.etree import cElementTree as ET
import xml.dom.minidom as minidom
from bs4.element import Tag, NavigableString

'''
proxymaster

This is my tool that can crawl all over some webservices to find proxies,
the proxies found by this tool will be used in the another tool of mine:

-- An not yet named anonymous e-mail sender service.



ADICIONAR FUNÇÃO:
	-SALVAR EM XML, CSV E TALVEZ XSML
'''

class UltraProxies:
	url = 'http://www.ultraproxies.com/'
	name = 'UltraProxies'
	
	def __init__(self, number=10):
		self.number = number
		self.got = requests.get(self.url)

	def get_proxies(self):
		get_text = self.got.text

		only_proxies = get_text.split("</thread>")[2].split("</table>")[0]
		soup = BS(only_proxies, 'lxml')
		
		final_proxies = []

		for proxy in soup.body.children:
			def conv_port():
				ports = proxy.find('td', {'class': 'port'}).get_text()
				digit = ports.split('-')
				port = ''
				for i in digit:
					port += chr(int(i)-17)
				return port

			if isinstance(proxy, Tag):
				proxydata = {
					'ip': proxy.find('td', {'class': 'ip'}).get_text()[:-1],
					'port': conv_port(),
					'place': proxy.find('td', {'width': '15%'}).get_text() ,
					'protocol': 'http'
				}
				final_proxies.append(proxydata)
		
		return final_proxies

class USProxy:
	name = 'USProxy'
	url = 'https://www.us-proxy.org/'

	def __init__(self, number=0):
		self.number = number
		self.got = requests.get(self.url)

	def get_proxies(self):
		protocol = {
			'yes': 'https',
			'no': 'http'
		}

		got_as_text = self.got.text

		soup = BS(got_as_text, 'html.parser')
		table = soup.find('table', {'id': 'proxylisttable', 'class': 'table table-striped table-bordered'})
		raw_proxies = [c for c in table.tbody.children][:self.number] if self.number > 0 else [c for c in table.tbody.children]

		final_proxies = []

		for proxy in raw_proxies:
			proxy_data = {}

			all_td = proxy.find_all('td')

			proxy_data['ip'] = all_td[0].get_text()
			proxy_data['port'] = all_td[1].get_text()
			proxy_data['place'] = all_td[2].get_text()
			proxy_data['protocol'] = protocol[all_td[5].get_text()]

			final_proxies.append(proxy_data)
		
		return final_proxies


# NÃO FUNCIONA AINDA, TALVEZ SEJA PRECISO USAR SELENIUM :(
class HideMyIP:
	name = "Hide My IP"
	url = "https://www.hide-my-ip.com/"
	url_ = 'https://www.hide-my-ip.com/pt/proxylist.shtml'

	def __init__(self, number=0):
		self.number = number
		self.got = requests.get(self.url_)

	def get_proxies(self):
		got_as_text = self.got.text

		soup = BS(got_as_text, 'html.parser')

		raw_proxies = soup.find('table', {'id':'sort-list'})

		return raw_proxies


class Hidester:
	nome = 'Hidester'
	url = 'https://hidester.com/'
	url_ = 'https://hidester.com/proxydata/php/data.php'

	def __init__(self, number=0):
		self.number = number

		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
			'Referer': 'https://hidester.com/pt/listaproxy/'
		}

		payload = {
			'mykey': 'data',
			'offset': '0',
			'orderBy': 'ping',
			'sortOrder': 'DESC',
			'country': '',
			'port': '',
			'type': 'undefined',
			'anonymity': 'undefined',
			'ping': 'undefined',
			'gproxy': '2'
		}

		payload['limit'] = self.number if self.number > 0 else '200'
		self.got = requests.get(self.url_, params=payload, headers=headers)

	def get_proxies(self):
		raw_proxies = self.got.json()

		final_proxies = []

		for proxy in raw_proxies:
			proxydata = {}

			proxydata['ip'] = proxy['IP']
			proxydata['port'] = str(proxy['PORT'])
			#proxydata['anonymity'] = proxy['anonymity']
			proxydata['place'] = proxy['country']
			if proxy['type'] in ['http', 'https']: proxydata['protocol'] = proxy['type']
			else: continue

			final_proxies.append(proxydata)

		return final_proxies

services = [UltraProxies, USProxy, Hidester]


def save_as_json(data, number):
	with open('proxies.json', 'w') as f:
		json.dump(data, f, indent=4)
	print('%s foram salvos para "proxies.json".' % number)


def save_as_xml(data, number):
	root = ET.Element("proxies")
	for proxy in data:
		proxy_root = ET.SubElement(root, "proxy")
		for each_proxy in proxy:
			ET.SubElement(proxy_root, each_proxy).text = proxy[each_proxy]
	
	rough_string = ET.tostring(root, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	save_it = reparsed.toprettyxml(indent="    ")
	with open("proxies.xml", 'wb') as filen:
		filen.write(save_it)
	print('%s foram salvos para "proxies.xml".' % number)


def save_as_csv(data, number):
	proxies = ["ip,port,protocol,place"]
	what_to_add = ''
	for proxy in data:
		what_to_add += proxy['ip']+','
		what_to_add += proxy['port']+','
		what_to_add += proxy['protocol']+','
		what_to_add += proxy['place']
		proxies.append(what_to_add)
		what_to_add = ''
	
	with open("proxies.csv", 'wb') as f:
		f.write('\n'.join(proxies))

	print('%s proxies foram salvos para "proxies.csv"' % number)




def main():
	opcoes = {
		'1': [services[0]],
		'2': [services[1]],
		'3': [services[2]],
		'4': services,
		'5': [random.choice(services)]
	}

	saving_types = {
		'1': save_as_json,
		'2': save_as_xml,
		'3': save_as_csv
	}
	print("""
[+]==========================================[+]
|         proxymaster - Proxies Fetcher        |
|                                     by Lord13|
[+]==========================================[+]
		""")
	print("""\n
[1] UltraProxies ({})
[2] USProxy      ({})
[3] Hidester     ({})
[4] Todos
[5] Aleatório

[0] Sair
	"""
	.format(UltraProxies.url, USProxy.url, Hidester.url))
	escolha = str(input("\nEscolha o numero correspondente: "))

	if escolha == '0':
		print ("==="*20)
		print ("Obrigado por usar o proxymaster!")
		exit()

	total_proxies= []
	quantos = int(input("\nInsira o numero de proxies que quiser (insira 0 para buscar o maximo): "))
	print("==="*20)
	print("""\n
    [1] Salvar como JSon 
    [2] Salvar como XML
    [3] Salvar como CSV
	""")
	saving_type = str(input("\nInsira o numero correspondente: "))
	save = saving_types[saving_type]
	
	for service in opcoes[escolha]:
		proxies = service().get_proxies()
		total_proxies.extend(proxies)

	f_total_proxies = total_proxies

	if quantos > 0:
		f_total_proxies = []
		for vez in range(quantos):
			proxy = random.choice(total_proxies)
			f_total_proxies.append(proxy)
			total_proxies.remove(proxy)

	print("==="*20)
	save(f_total_proxies, len(f_total_proxies))
	#print("\n%s Proxies foram salvos para 'proxies.txt', em formato json." % len(f_total_proxies))

if __name__ == '__main__':
	main()
