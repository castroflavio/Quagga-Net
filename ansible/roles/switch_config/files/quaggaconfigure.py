#!/usr/bin/python

from xml.etree.ElementTree import parse, tostring
from shutil import copyfile
import json
import socket
import sys

path = sys.argv[1]
quagga_info = sys.argv[1] + sys.argv[2]
system = sys.argv[3]

def pushTemp(repl, SourceXml, DestXml):
    copyfile(SourceXml, DestXml)
    lines = []
    with open(DestXml) as infile:
	for line in infile:
	    for src, target in repl.iteritems():
		line = line.replace(src, target)
	    lines.append(line)
    with open(DestXml, 'w') as outfile:
	for line in lines:
	    outfile.write(line)
    print system

def replace(down_if, down_ip, spine_as, guestmac, spine_id, down_nei, down_as):
	replacements = {'DOWN_IF': down_if,
						'DOWN_IP': down_ip,
						'SPINE_AS': spine_as,
						'GUESTMAC': guestmac,
						'SPINE_ID': spine_id,
						'DOWN_NEI': down_nei,
						'DOWN_AS': down_as}
	return replacements

with open(quagga_info) as data_file:    
    quagga_dict = json.load(data_file)
router_dict = quagga_dict['r1']
for config in router_dict:
    server = config['server']
    if server == system:
	sourceXML = path + '/templates/quagga.conf.j2'
	destXML = path + '/templates/' + server + '.quagga.conf.j2'
	pushTemp(replace(config), sourceXML, destXML)




