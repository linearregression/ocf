from django.shortcuts import get_object_or_404, render_to_response
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponseServerError
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from egeni.clearinghouse.models import *
from django.forms.models import inlineformset_factory
import os

LINK_ID_FIELD = "link_id"
NODE_ID_FIELD = "node_id"

def home(request):
    '''Show the list of slices, and form for creating new slice'''

    if request.method == 'POST':
        slice = Slice(owner=request.user, committed=False)
        form = SliceForm(request.POST, instance=slice)
        print "<0>"
        if form.is_valid():
            print "<1>"
            slice = form.save()
            print "<2>"
            return HttpResponseRedirect(slice.get_absolute_url())
        print "<3>"
    else:
        # get reserved and unreserved slices
        form = SliceForm()
        
    reserved_slices = request.user.slice_set.filter(committed=True)
    reserved_ids = reserved_slices.values_list('id', flat=True)
    unreserved_slices = request.user.slice_set.exclude(id__in=reserved_ids)
    
    return render_to_response("clearinghouse/home.html",
                              {'reserved_slices': reserved_slices,
                               'unreserved_slices': unreserved_slices,
                               'form': form})

def slice_detail(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    agg_list = AggregateManager.objects.all()
    
    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, FlowSpace)
    
    print "<xx>"
    
    if request.method == "POST":
        print "<yy>"
        # get all the selected nodes
        for am in agg_list:
            # remove from slice the nodes that are not in the post
            nodes = slice.nodes.exclude(
                nodeId__in=request.POST.getlist("am_%s" % am.id))
            [slice.nodes.remove(n) for n in nodes]
            
            # add to slice nodes that are in post but not in slice
            nodes = am.local_node_set.filter(
                nodeId__in=request.POST.getlist("am_%s" % am.id))
            nodes = nodes.exclude(
                nodeId__in=slice.nodes.values_list('nodeId', flat=True))
            print "nodes: %s" % nodes
            [slice.nodes.add(n) for n in nodes]
            
        formset = FSFormSet(request.POST, request.FILES, instance=slice)
        if formset.is_valid():
            formset.save()
            
            slice.committed = True
            slice.save()
            
            # TODO: Do reservation here
            
            return HttpResponseRedirect(reverse('home'))
        
    else:
        print "<zz>"
        for am in agg_list:
            print "<aa>"
            am.updateRSpec()
        formset = FSFormSet(instance=slice)
        print "Slice nodeIds: %s" % slice.nodes.values_list('nodeId', flat=True)
    
#        print "Formset: "
#        print formset
#        print "forms: "
#        for form in formset.forms:
#            print form.as_table()
        
    return render_to_response("clearinghouse/slice_detail.html",
                              {'aggmgr_list': agg_list,
                               'slice': slice,
                               'fsformset': formset,
                               })

def slice_flash_detail(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    
    # create a formset to handle all flowspaces
    FSFormSet = inlineformset_factory(Slice, FlowSpace)
    
    print "<xx>"
    
    if request.method == "POST":
#        if NODE_ID_FIELD not in request.POST or LINK_ID_FIELD not in request.POST:
#            return HttpResponseBadRequest("Missing fields %s or %s" 
#                                          % (LINK_ID_FIELD, NODE_ID_FIELD))
        
        formset = FSFormSet(request.POST, request.FILES, instance=slice)
        if not formset.is_valid():
            return HttpResponseBadRequest("Form is invalid")
        
        link_ids = request.POST.getlist(LINK_ID_FIELD)
        node_ids = request.POST.getlist(NODE_ID_FIELD)
        
        # delete old links and nodes
        LinkSliceStatus.objects.filter(
            slice=slice).exclude(link__pk__in=link_ids).delete()
        NodeSliceStatus.objects.filter(
            slice=slice).exclude(node__pk__in=node_ids).delete()
        
        # create new links and ids
        for id in link_ids:
            print "Link: %s" % id;
            link = get_object_or_404(Link, pk=id)
            through, created = LinkSliceStatus.objects.get_or_create(
                                    slice=slice,
                                    link=link,
                                    defaults={'reserved': False,
                                              'removed': False,
                                              'has_error': False,
                                              }
                                    )
            
        for id in node_ids:
            print "Node: %s" % id;
            node = get_object_or_404(Node, pk=id)
            through, created = NodeSliceStatus.objects.get_or_create(
                                    slice=slice,
                                    node=node,
                                    defaults={'reserved': False,
                                              'removed': False,
                                              'has_error': False,
                                              }
                                    )

        # get the RSpec of the Slice
        rspec = render_to_string("rspec/egeni-rspec.xml",
                                 {"node_set": slice.nodes.all(),
                                  "slice": slice})
            
        formset.save()
        slice.committed = False
        slice.save()
        
        # TODO: Do actual reservation    
        slice.committed = False
        return HttpResponseRedirect(reverse('slice_flash_detail', args=[slice_id]))

    elif request.method == "GET":
#        for am in agg_list:
#            print "<aa>"
#            am.updateRSpec()
        formset = FSFormSet(instance=slice)
        print "Slice nodeIds: %s" % slice.nodes.values_list('nodeId', flat=True)
        return render_to_response("clearinghouse/slice_flash_detail.html",
                                  {'slice': slice,
                                   'fsformset': formset,
                                   })
    else:
        return HttpResponseNotAllowed("GET", "POST")

def slice_get_img(request, slice_id, img_name):
    image_data = open("../../img/%s" % img_name, "rb").read()
    return HttpResponse(image_data, mimetype="image/png")

def slice_get_plugin(request, slice_id):
    jar = open("../../plugin.jar", "rb").read()
    return HttpResponse(jar, mimetype="application/java-archive")

def slice_get_xsd(request, slice_id):
    xsd = open("../plugin.xsd", "rb").read()
    return HttpResponse(xsd, mimetype="application/xml")    

def slice_get_topo(request, slice_id):
    slice = get_object_or_404(Slice, pk=slice_id)
    print "Doing topo view"
    
    if request.method == "GET":
        for am in AggregateManager.objects.all():
            am.updateRSpec()
        print "Done update"
        # get all the local nodes
        nodes = Node.objects.all().exclude(is_remote=True)
        
        # get all the local links
        links = Link.objects.filter(
                    src__ownerNode__is_remote=False,
                    dst__ownerNode__is_remote=False)

        print "rendering xml"

        xml = render_to_string("plugin/flash-xml.xml",
                               {'nodes': nodes,
                                'links': links,
                                'slice': slice})
        print xml
        return HttpResponse(xml, mimetype="text/xml")
    else:
        return HttpResponseNotAllowed("GET")




def am_create(request):
    error_msg = u"No POST data sent."
    if(request.method == "POST"):
        post = request.POST.copy()
        if(post.has_key('name') and post.has_key('url')):
            # Get info
            name = post['name']
            url = post['url']
            
            new_am = AggregateManager.objects.create(name=name,
                                                     url=url,
                                                     )
            return HttpResponseRedirect(new_am.get_absolute_url())
        else:
            error_msg = u"Insufficient data. Need at least name and url"
            return HttpResponseBadRequest(error_msg)
    else:
        return HttpResponseNotAllowed("GET")

def am_detail(request, am_id):
    # get the aggregate manager object
    am = get_object_or_404(AggregateManager, pk=am_id)
    if(request.method == "GET"):
        return render_to_response("clearinghouse/aggregatemanager_detail.html",
                                  {'object':am})
        
    elif(request.method == "POST"):
        try:
            am.updateRSpec()
        except Exception, e:
            print "Update RSpec Exception"; print e
            return render_to_response("clearinghouse/aggregatemanager_detail.html",
                                      {'object':am,
                                       'error_message':"Error Parsing/Updating the RSpec: %s" % e,
                                       })
        else:
            am.save()
            return HttpResponseRedirect(am.get_absolute_url())
    else:
        return HttpResponseNotAllowed("GET", "POST")

