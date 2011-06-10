from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import simple
from vt_manager.common.messaging.models import DatedMessage
from django.views.generic import list_detail, simple
from django.views.generic.create_update import apply_extra_context
from vt_manager.models import *
from vt_manager.communication.utils.XmlHelper import XmlHelper
import uuid, time, logging
from django.template import loader, RequestContext
from django.core.xheaders import populate_xheaders
from django.contrib import messages

#News
from vt_manager.controller.drivers.VTDriver import VTDriver
from vt_manager.utils.HttpUtils import HttpUtils
from vt_manager.models.NetworkInterface import NetworkInterface
from vt_manager.models.MacRange import MacRange
from vt_manager.controller.dispatchers.forms.NetworkInterfaceForm import MgmtBridgeForm
from django.db import transaction

def userIsIslandManager(request):

	if (not request.user.is_superuser):
        
		return simple.direct_to_template(request,
							template = 'not_admin.html',
							extra_context = {'user':request.user},
						)

@transaction.commit_on_success
def servers_crud(request, server_id=None):

	"""Show a page for the user to add/edit an  VTServer """

	if (not request.user.is_superuser):
        
		return simple.direct_to_template(request,
						template = 'not_admin.html',
						extra_context = {'user':request.user},
					)
	vmProjects = {}
	vmSlices = {}
	try:
		for vm in VTDriver.getVMsInServer(VTDriver.getServerById(server_id)):
			if vm.projectName not in vmProjects:
				vmProjects[vm.projectName] = vm.projectId
			if vm.sliceName not in vmSlices:
				vmSlices[vm.sliceName] = vm.sliceId
	except Exception as e:
		pass

	

	serverFormClass = HttpUtils.getFormFromModel(VTServer)
	ifaceFormClass = HttpUtils.getFormFromModel(NetworkInterface)
	IfaceFormSetClass = modelformset_factory(NetworkInterface)

	if server_id != None:
		server = get_object_or_404(VTServer, pk=server_id)
	else:
		server = None
	
	if request.method == "GET":
		serverForm = serverFormClass(instance=server)

		if server  != None:
			print "[LEODEBUG] GET con server (edit)"
			mgmt = server.getNetworkInterfaces().filter(isMgmt = True)
			if mgmt:
				mgmt = mgmt.get()
				mgmtIfaceForm = MgmtBridgeForm({'mgmtBridge-name':mgmt.getName(), 'mgmtBridge-mac':mgmt.getMacStr()}, prefix ="mgmtBridge")
			else:
				mgmtIfaceForm = MgmtBridgeForm(prefix ="mgmtBridge")
			
			data = server.getNetworkInterfaces().filter(isMgmt = False)
			if data:
				IfaceFormSetClass = modelformset_factory(NetworkInterface,extra = 0)
			ifaceformset = IfaceFormSetClass(queryset= data)

		else:
			mgmtIfaceForm = MgmtBridgeForm(prefix ="mgmtBridge")
			ifaceformset = IfaceFormSetClass(queryset= NetworkInterface.objects.none())
			print ifaceformset
			

	elif request.method == "POST":
		print "[LEODEBUG]"
		print request.POST
		serverForm = serverFormClass(request.POST, instance=server)
		ifaceformset = IfaceFormSetClass(request.POST)
		mgmtIfaceForm = MgmtBridgeForm(request.POST, prefix ="mgmtBridge")
		
		if serverForm.is_valid() and ifaceformset.is_valid() and mgmtIfaceForm.is_valid():
			ifaces = ifaceformset.save(commit = False)
			if server == None:
				server = serverForm.save(commit = False)
			try:
				server = VTDriver.crudServerFromInstance(server)
				VTDriver.setMgmtBridge(request, server)
				VTDriver.crudDataBridgeFromInstance(server, ifaces,request.POST.getlist("DELETE"))
			except Exception as e:
				print e
				raise e
				#return a alguna pagina y volver atras las transacciones
				
			return HttpResponseRedirect('/servers/admin/')
	else:
		return HttpResponseNotAllowed("GET", "POST")

	context = {"serverForm": serverForm, 'vmProjects': vmProjects, 'vmSlices': vmSlices,'ifaceformset' : ifaceformset, 'mgmtIfaceForm' : mgmtIfaceForm}
	if server_id != None: context["server"] = server

	return simple.direct_to_template(
		request,
		template="servers/servers_crud.html",
		extra_context=context,
		#form=form,
	)


def admin_servers(request):
    
	if (not request.user.is_superuser):
        
		return simple.direct_to_template(request,
				template = 'not_admin.html',
				extra_context = {'user':request.user},
			) 
	
	servers = VTDriver.getAllServers()

	return simple.direct_to_template(
		request, template="servers/admin_servers.html",
		extra_context={"servers_ids": servers})

def delete_server(request, server_id):

	if (not request.user.is_superuser):
        
		return simple.direct_to_template(request,
				template = 'not_admin.html',
				extra_context = {'user':request.user},
		)
	if request.method == 'POST':
		try:
			VTDriver.deleteServer(VTDriver.getServerById(server_id))
			return HttpResponseRedirect(reverse('dashboard'))

		except Exception as e:
			logging.error(e)
	elif request.method == 'GET':
		return simple.direct_to_template(request,
				template = 'servers/delete_server.html',
				extra_context = {'user':request.user, 'next':reverse("admin_servers")},
		)
	
def action_vm(request, server_id, vm_id, action):

	if (not request.user.is_superuser):
        
		return simple.direct_to_template(request,
			template = 'not_admin.html',
			extra_context = {'user':request.user},
		)

	if(action == 'list'):
          
		return simple.direct_to_template(
				request, template="servers/list_vm.html",
				extra_context={"vm": VTDriver.getVMbyId(vm_id)}
		)

	elif(action == 'check_status'):
		#XXX: Do this function if needed
		return simple.direct_to_template(
				request, template="servers/list_vm.html",
				extra_context={"vm": VM.objects.get(id = vm_id)}
		)

	else:
		VTDriver.PropagateAction(vm_id, action)
		#vm = VM.objects.get(id = vm_id)
		#rspec = XmlHelper.getSimpleActionSpecificQuery(action)
		#Translator.PopulateNewAction(rspec.query.provisioning.action[0], vm)
		#ProvisioningDispatcher.processProvisioning(rspec.query.provisioning)
    
	return HttpResponseRedirect(reverse('edit_server', args = [server_id]))


def subscribeEthernetRanges(request, server_id):
	print "[LEODEBUG] EL SeRVER ID"
	print server_id
	if (not request.user.is_superuser):
		return simple.direct_to_template(request,
					template = 'not_admin.html',
					extra_context = {'user':request.user},
		)

	macRanges = MacRange.objects.all()

	if server_id != None:
		server = get_object_or_404(VTServer, pk=server_id)
	else:
		raise Exception ("NO SERVER")
	
	if request.method == "GET":
		return simple.direct_to_template(request,
				template = 'servers/servers_subscribeEthernetRanges.html',
				extra_context = {'server': server, 'macRanges':macRanges},
		)
	elif request.method=='POST':
		print "[LEODEBUG]: POSTTT"
		print request.POST
		VTDriver.manageEthernetRanges(request,server,macRanges)
		return HttpResponseRedirect(reverse('edit_server', args = [server_id]))
	else:
		return HttpResponseNotAllowed("GET", "POST")


def subscribeIp4Ranges(request, server_id):
	print "[LEODEBUG] EL SeRVER ID"
	print server_id
	if (not request.user.is_superuser):
		return simple.direct_to_template(request,
					template = 'not_admin.html',
					extra_context = {'user':request.user},
		)

	ipRanges = Ip4Range.objects.all()

	if server_id != None:
		server = get_object_or_404(VTServer, pk=server_id)
	else:
		raise Exception ("NO SERVER")
	
	if request.method == "GET":
		return simple.direct_to_template(request,
				template = 'servers/servers_subscribeIp4Ranges.html',
				extra_context = {'server': server, 'ipRanges':ipRanges},
		)
	elif request.method=='POST':
		print "[LEODEBUG]: POSTTT"
		print request.POST
		VTDriver.manageIp4Ranges(request,server,ipRanges)
		return HttpResponseRedirect(reverse('edit_server', args = [server_id]))
	else:
		return HttpResponseNotAllowed("GET", "POST")
def servers_net_settings(request):
	pass
#    """Show a page for the user to add/edit the Netoworking settings for a VTServer """
#
#    if (not request.user.is_superuser):
#
#        return simple.direct_to_template(request,
#                            template = 'not_admin.html',
#                            extra_context = {'user':request.user},
#                        )
#    settings = VTServerNetworkingSettings.objects.all()
#
#    if len(settings) == 0:
#        settings_id = None 
#    elif len(settings) == 1:
#        settings_id = settings[0].id
#    else:
#        for i,s in enumerate(settings):
#            if i != 0:
#                s.delete()
#        settings_id = settings[0].id
#
#    return generic_crud(
#        request,
#        obj_id=settings_id,
#        model=VTServerNetworkingSettings,
#        template_object_name="settings",
#        template="servers/servers_net.html",
#        redirect = lambda inst: '/servers/net/update/'
#    )

def servers_net_update(request):
	pass
#    if (not request.user.is_superuser): 
#
#        return simple.direct_to_template(request,
#               template = 'not_admin.html',
#               extra_context = {'user':request.user},
#               )
#
#    settings = VTServerNetworkingSettings.objects.all()
#    if len(settings) == 0:
#        try: 
#            raise Exception("No Settings to update")
#        except:
#            pass
#
#    elif len(settings) == 1:
#        settings = settings[0]
#    else:
#        for i,s in enumerate(settings):
#            if i != 0:
#                s.delete()
#        settings = settings[0]
#
#    for server in VTServer.objects.all():
#        server.ipRange = settings.ipRange
#        server.mask = settings.mask
#        server.gw = settings.gw
#        server.dns1  = settings.dns1
#        server.dns2  = settings.dns2   
#        server.save() 
#
#    return HttpResponseRedirect('/servers/admin/')




'''
Networking point of entry
'''
from vt_manager.controller.networking.EthernetController import EthernetController
from vt_manager.controller.networking.Ip4Controller import Ip4Controller
from vt_manager.models.MacRange import MacRange

NETWORKING_ACTION_ADD="add"
NETWORKING_ACTION_EDIT="edit"
NETWORKING_ACTION_DELETE="delete"
NETWORKING_ACTION_SHOW="show"
NETWORKING_ACTION_ADDEXCLUDED="addExcluded"
NETWORKING_ACTION_REMOVEXCLUDED="removeExcluded"
NETWORKING_POSSIBLE_ACTIONS=(NETWORKING_ACTION_ADD,NETWORKING_ACTION_DELETE,NETWORKING_ACTION_EDIT,NETWORKING_ACTION_SHOW,NETWORKING_ACTION_ADDEXCLUDED,NETWORKING_ACTION_REMOVEXCLUDED,None)

def networkingDashboard(request):#,rangeId):
	
	extra_context = {"section": "networking","subsection":"None"}
	extra_context["macRanges"] = EthernetController.listRanges()
	extra_context["MacRange"] = MacRange
	extra_context["ip4Ranges"] = Ip4Controller.listRanges()
	extra_context["Ip4Range"] = Ip4Range
	
	template = "networking/index.html"
	return simple.direct_to_template(
		request,
		extra_context=extra_context,
		template=template,
	)



def manageIp4(request,rangeId=None,action=None,ip4Id=None):
	if not action in NETWORKING_POSSIBLE_ACTIONS:
		raise Exception("Unknown action") 
	
	#Define context
	extra_context = {"section": "networking","subsection":"ip4"+str(action),}	
	
	#Add process	
	if (action == NETWORKING_ACTION_ADD):
		if request.method == "GET":
			#Show form
			extra_context["form"] = HttpUtils.getFormFromModel(Ip4Range)
			return simple.direct_to_template(
				request,
				extra_context = extra_context, 
				template="networking/ip4/rangeCrud.html",
			)
			return 
		
		elif request.method == "POST":
			try:
				instance = HttpUtils.getInstanceFromForm(request,Ip4Range)
				#Create Range
				Ip4Controller.createRange(instance)
			except Exception as e:
				print e
				extra_context["form"] = HttpUtils.processExceptionForm(e,request,Ip4Range)
				#Process creation query
				return simple.direct_to_template(
					request,
					extra_context = extra_context, 
					template="networking/ip4/rangeCrud.html",
				)
			
			
	#Show
	if ((action == None) or (action==NETWORKING_ACTION_SHOW)) and (not rangeId==None):

		instance = Ip4Controller.getRange(rangeId)
		extra_context["range"] = instance 

		return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template="networking/ip4/rangeDetail.html",
		)
		
			
	#Edit
	#TODO

	#Add excluded Ip
	if (action == NETWORKING_ACTION_ADDEXCLUDED) and (request.method == "POST"):
		if not request.method == "POST":
			raise Exception("Invalid method")
		try:	
			instance = Ip4Controller.getRange(rangeId)
			extra_context["range"] = instance 
		
			#Create excluded
			Ip4Controller.addExcludedIp4(instance,request)
		except Exception as e:
			print e
			extra_context["errors"] = HttpUtils.processException(e)
			pass	
					
		return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template="networking/ip4/rangeDetail.html",
		)
		
	#Release excluded Ip
	if (action == NETWORKING_ACTION_REMOVEXCLUDED) and (request.method == "POST"):

		try:	
			instance = Ip4Controller.getRange(rangeId)
			extra_context["range"] = instance 
		
			#Create excluded
			Ip4Controller.removeExcludedIp4(instance,ip4Id)
		except Exception as e:
			print e
			extra_context["errors"] = HttpUtils.processException(e)
			pass	
					
		return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template="networking/ip4/rangeDetail.html",
		)
	
	#Delete
	if (action == NETWORKING_ACTION_DELETE) and (request.method == "POST"):

		try:	
			Ip4Controller.deleteRange(rangeId)
		except Exception as e:
			print e
			extra_context["errors"] = HttpUtils.processException(e)
			pass	
	


	
	
	extra_context["ranges"] = Ip4Controller.listRanges()	

	template = "networking/ip4/index.html"
	return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template=template,
		)

def manageEthernet(request,rangeId=None,action=None,macId=None):

	if not action in NETWORKING_POSSIBLE_ACTIONS:
		raise Exception("Unknown action") 

	#Define context	
	extra_context = {"section": "networking","subsection":"ethernet",}	

	
	#Add process	
	if (action == NETWORKING_ACTION_ADD):
		if request.method == "GET":
			#Show form
			extra_context["form"] = HttpUtils.getFormFromModel(MacRange)
			return simple.direct_to_template(
				request,
				extra_context = extra_context, 
				template="networking/ethernet/rangeCrud.html",
			)
			return 
		
		elif request.method == "POST":
			try:
				instance = HttpUtils.getInstanceFromForm(request,MacRange)
				#Create Range
				EthernetController.createRange(instance)
			except Exception as e:
				print e
				extra_context["form"] = HttpUtils.processExceptionForm(e,request,MacRange)
				#Process creation query
				return simple.direct_to_template(
					request,
					extra_context = extra_context, 
					template="networking/ethernet/rangeCrud.html",
				)
			
			
	#Show
	if ((action == None) or (action==NETWORKING_ACTION_SHOW)) and (not rangeId==None):

		instance = EthernetController.getRange(rangeId)
		extra_context["range"] = instance 

		return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template="networking/ethernet/rangeDetail.html",
		)
		
			
	#Edit
	#TODO

	#Add excluded Ip
	if (action == NETWORKING_ACTION_ADDEXCLUDED) and (request.method == "POST"):
		if not request.method == "POST":
			raise Exception("Invalid method")
		try:	
			instance = EthernetController.getRange(rangeId)
			extra_context["range"] = instance 
		
			#Create excluded
			EthernetController.addExcludedMac(instance,request)
		except Exception as e:
			print e
			extra_context["errors"] = HttpUtils.processException(e)
			pass	
					
		return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template="networking/ethernet/rangeDetail.html",
		)
		
	#Release excluded Ip
	if (action == NETWORKING_ACTION_REMOVEXCLUDED) and (request.method == "POST"):

		try:	
			instance = EthernetController.getRange(rangeId)
			extra_context["range"] = instance 
		
			#Create excluded
			EthernetController.removeExcludedMac(instance,macId)
		except Exception as e:
			print e
			extra_context["errors"] = HttpUtils.processException(e)
			pass	
					
		return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template="networking/ethernet/rangeDetail.html",
		)
	
	#Delete
	if (action == NETWORKING_ACTION_DELETE) and (request.method == "POST"):

		try:	
			EthernetController.deleteRange(rangeId)
		except Exception as e:
			print e
			extra_context["errors"] = HttpUtils.processException(e)
			pass	
	

	#Listing ranges
	extra_context["ranges"] = EthernetController.listRanges()
	return simple.direct_to_template(
			request,
			extra_context = extra_context, 
			template = "networking/ethernet/index.html",
		)



