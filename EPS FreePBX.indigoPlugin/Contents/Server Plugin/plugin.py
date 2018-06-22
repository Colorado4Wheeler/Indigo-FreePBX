#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""plugin.py: FreePBX Plugin."""

__version__ 	= "1.0.0-b1"

__modname__		= "Indigo FreePBX"
__author__ 		= "ColoradoFourWheeler"
__copyright__ 	= "Copyright 2018, ColoradoFourWheeler & EPS"
__credits__ 	= ["ColoradoFourWheeler"]
__license__ 	= "GPL"
__maintainer__ 	= "ColoradoFourWheeler"
__email__ 		= "Indigo Forums"
__status__ 		= "Production"

# Python Modules
import logging
import sys
import os
import hashlib 
import hmac
from random import randint
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
import json
import base64

# Third Party Modules
import indigo

# Package Modules
from lib.eps import ex
from lib.eps import version

class Plugin(indigo.PluginBase):

	################################################################################
	# CLASS HANDLERS
	################################################################################	

	###
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		
	###	
	def __del__(self):
		indigo.PluginBase.__del__(self)
	

	###
	def deviceStartComm (self, dev):
		self.debugLog(u"device start comm called")
		dev.stateListOrDisplayStateIdChanged() # Commit any state changes
		
		#self.dnd_status(dev)
		#if dev.deviceTypeId == 'Extension': self.dnd_on(dev)
		
	###
	def startup(self):
		self.debugLog(u"startup called")
				
	###
	def shutdown(self):
		self.debugLog(u"shutdown called")

	###
	def runConcurrentThread(self):
		try:
			while True:
					#self.processTimer()
					self.sleep(1)
		except self.StopThread:
			pass	

	
	################################################################################
	# SERVER FORM
	################################################################################
	
	################################################################################
	# ACTIONS
	################################################################################

	###
	def action_cf (self, action):
		try:
			method = 'callforward'
			
			dev = indigo.devices[action.deviceId]
			server = int(dev.pluginProps["server"])
			if not server in indigo.devices:
				self.logger.error (u"PBX Server {} is not in the Indigo device list, was it removed?  {} action cannot complete".format(server, dev.name))
				return
				
			server = indigo.devices[server]	
			params = {}
			
			if action.pluginTypeId == 'callForwarding':
				if action.props['cfenabled']: params['CF'] = int(action.props['cfnumber'])
				if action.props['cfuenabled']: params['CFU'] = int(action.props['cfunumber'])
				if action.props['cfuenabled']: params['CFB'] = int(action.props['cfbnumber'])
			elif action.pluginTypeId == 'cfDisableAll':
				params['CF'] = False
				params['CFB'] = False
				params['CFU'] = False
			elif action.pluginTypeId == 'cfDisableAll':
				params['CF'] = False
			elif action.pluginTypeId == 'cfDisableAll':
				params['CFB'] = False
			elif action.pluginTypeId == 'cfDisableAll':
				params['CFU'] = False
			
			#indigo.server.log(unicode(json.dumps(params)))
				
			result = self.invoke_api(server, method, dev.pluginProps["extension"], json.dumps(params))
			result = self.get_status(dev, method)
			#indigo.server.log(unicode(result))
			
			if result:
				keyValueList = []
				
				if not result['CF']:
					keyValueList.append({'key':'cfunconditional', 'value':'disabled'})
					keyValueList.append({'key':'cfunconditionalNumber', 'value':''})
				else:
					keyValueList.append({'key':'cfunconditional', 'value':'enabled'})
					keyValueList.append({'key':'cfunconditionalNumber', 'value':result['CF']})
					
				if not result['CFB']:
					keyValueList.append({'key':'cfbusy', 'value':'disabled'})
					keyValueList.append({'key':'cfbusyNumber', 'value':''})
				else:
					keyValueList.append({'key':'cfbusy', 'value':'enabled'})
					keyValueList.append({'key':'cfbusyNumber', 'value':result['CFB']})
					
				if not result['CFU']:
					keyValueList.append({'key':'cfunavailable', 'value':'disabled'})
					keyValueList.append({'key':'cfunavailableNumber', 'value':''})
				else:
					keyValueList.append({'key':'cfunavailable', 'value':'enabled'})	
					keyValueList.append({'key':'cfunavailableNumber', 'value':result['CFB']})	
					
				dev.updateStatesOnServer(keyValueList)
			
			
		
		except Exception as e:
			self.logger.error (ex.stack_trace(e))	

	###
	def action_dnd (self, action):
		try:
			method = 'donotdisturb'
			
			dev = indigo.devices[action.deviceId]
			server = int(dev.pluginProps["server"])
			if not server in indigo.devices:
				self.logger.error (u"PBX Server {} is not in the Indigo device list, was it removed?  {} action cannot complete".format(server, dev.name))
				return
				
			server = indigo.devices[server]	
			params = {}
			
			if action.pluginTypeId == 'dndEnable':
				params["status"] = 'enabled'
			else:
				params["status"] = False
				
			result = self.invoke_api(server, method, dev.pluginProps["extension"], json.dumps(params))
			result = self.get_status(dev, method)
			
			if result:
				keyValueList = []
				
				if result["status"] == "enabled":
					keyValueList.append({'key':'dnd', 'value':'enabled'})
				else:
					keyValueList.append({'key':'dnd', 'value':'disabled'})
					
				dev.updateStatesOnServer(keyValueList)
			
			
		
		except Exception as e:
			self.logger.error (ex.stack_trace(e))
		

	################################################################################
	# API
	################################################################################
	
	###
	def get_status (self, dev, method):
		try:
			if dev.deviceTypeId == 'Server':
				result = self.invoke_api(dev, method)
			
			elif dev.deviceTypeId == 'Extension':
				server = int(dev.pluginProps["server"])
				if not server in indigo.devices:
					self.logger.error (u"PBX Server {} is not in the Indigo device list, was it removed?  {} action cannot complete".format(server, dev.name))
					return
					
				server = indigo.devices[server]	
				result = self.invoke_api(server, method, dev.pluginProps["extension"])
				
				return result
		
		except Exception as e:
			self.logger.error (ex.stack_trace(e))
	
	###
	def invoke_api (self, dev, method, suffix = '', body = ''):
		try:
			if not suffix == '': suffix = '/' + suffix
			
			if body == '':
				verb = 'GET'
			else:
				verb = 'PUT'	
				
			#url = 'http://{}/admin/rest.php/rest/donotdisturb/users'.format(dev.pluginProps["ipaddress"])
			url = '{}/restapi/rest.php/rest/{}/users{}'.format(dev.pluginProps["ipaddress"], method, suffix)
			token = dev.pluginProps["token"]
			key = dev.pluginProps["key"]
			#body = ''
			
			d = indigo.server.getTime()
			keyString = d.strftime("%Y-%m-%d %H:%M:%S %f") + str(randint(1000, 1000001))
			nonce = hashlib.sha1(keyString.encode('ascii', 'ignore')).digest().encode("hex")  # [0:16]
			
			keyString = '{}:{}'.format(url, verb.lower())
			hash_a = hashlib.sha256(keyString.encode('ascii', 'ignore')).digest().encode("hex")
			
			keyString = '{}:{}'.format(token, nonce)
			hash_b = hashlib.sha256(keyString.encode('ascii', 'ignore')).digest().encode("hex")
			
			
			#keyString = '{}'.format(body.encode('base64'))
			keyString = base64.b64encode(bytes(body))
			#indigo.server.log(u"Body Encode64: {}".format(keyString))
			#hash_c = hashlib.sha256(keyString.encode('ascii', 'ignore')).digest().encode("hex")
			hash_c = hashlib.sha256(keyString).digest().encode("hex")
			#hash_d = hashlib.sha256(body.encode('ascii', 'ignore')).digest().encode("hex")
			#indigo.server.log(u"Body C: {}".format(hash_c))
			#indigo.server.log(u"Body D: {}".format(hash_d))
			#return
			
			keyString = '{}:{}:{}'.format(hash_a, hash_b, hash_c)
			data = hashlib.sha256(keyString.encode('ascii', 'ignore')).digest().encode("hex")
			
			signature = hmac.new(str(key), str(data), hashlib.sha256).hexdigest() # Py 2.x, in Py 3.x we'll need to use bytes instead
			#signature = hmac.new(str(key), str(hash_c), hashlib.sha256).hexdigest()
			
			#indigo.server.log(u"Body C: {}".format(hash_c))
			#indigo.server.log(u"Token Key: {}".format(key))
			#indigo.server.log(u"Signature: {}".format(signature))
			#indigo.server.log(u"Nonce: {}".format(nonce))
			#indigo.server.log(u"Token: {}".format(token))
			
			if body == '':
				headers = {'Signature': signature, 'Nonce': nonce, 'Token': token}
				ret = requests.get(u"http://{}".format(url), headers=headers)
			else:
				headers = {'Signature': signature, 'Nonce': nonce, 'Token': token, 'Content-Type': 'application/json'}
				ret = requests.put(u"http://{}".format(url), data=body, headers=headers)
				#headers = {'Signature': signature, 'Nonce': nonce, 'Token': token}
				#ret = requests.put(u"http://{}".format(url), json=body, headers=headers)
				
			#ret = urlopen(Request(url, headers))
			#ret = requests.get(u"http://{}".format(url), headers=headers)
			#ret = requests.get(url, headers=headers, auth=HTTPBasicAuth('101','12345')) # change 12345 to the known 29 password
			#ret = requests.get(url, headers=headers, auth=HTTPDigestAuth('101','12345'))
			
			#indigo.server.log(url)
			
			if ret.status_code == 200:
				self.logger.debug (u"Success on FreePBX RestAPI on {}: {}".format(dev.name, ret.text))
				if not ret.text == '':
					results = json.loads(ret.text)
					return results
				else:
					return {'status': 'no response, successful operation'}
				
				#for r in results:
				#	for extension, status in r.iteritems():
				#		extdata = extension.split("/")
				#		indigo.server.log(unicode(extdata))
				
			elif ret.status_code == 403:
				self.logger.error (u"Access forbidden to FreePBX RestAPI on {}: {}".format(dev.name, ret.text))
			elif ret.status_code == "404":
				self.logger.error (u"Invalid response to FreePBX RestAPI on {}: {}".format(dev.name, ret.text))
			else:
				self.logger.error (u"Invalid response to FreePBX RestAPI on {}: {}".format(dev.name, ret.text))
				
			
			#indigo.server.log(u"{}".format(ret))
		
		except Exception as e:
			self.logger.error (ex.stack_trace(e))

		return False





















