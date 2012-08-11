from subprocess import Popen, PIPE
import json
import time
import urllib2

from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson

import jsonrpclib
import oauth2 as oauth
from baculaUI.freenas import forms, models, utils


class OAuthTransport(jsonrpclib.jsonrpc.SafeTransport):
    def __init__(self, host, verbose=None, use_datetime=0, key=None,
            secret=None):
        jsonrpclib.jsonrpc.SafeTransport.__init__(self)
        self.verbose = verbose
        self._use_datetime = use_datetime
        self.host = host
        self.key = key
        self.secret = secret

    def oauth_request(self, url, moreparams={}, body=''):
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time())
        }
        consumer = oauth.Consumer(key=self.key, secret=self.secret)
        params['oauth_consumer_key'] = consumer.key
        params.update(moreparams)

        req = oauth.Request(method='POST',
            url=url,
            parameters=params,
            body=body)
        signature_method = oauth.SignatureMethod_HMAC_SHA1()
        req.sign_request(signature_method, consumer, None)
        return req

    def request(self, host, handler, request_body, verbose=0):
        request = self.oauth_request(url=self.host, body=request_body)
        req = urllib2.Request(request.to_url())
        req.add_header('Content-Type', 'text/json')
        req.add_data(request_body)
        f = urllib2.urlopen(req)
        return(self.parse_response(f))


class JsonResponse(HttpResponse):
    """
    This is a response class which implements FreeNAS GUI API

    It is not required, the user can implement its own
    or even open/code an entire new UI just for the plugin
    """

    error = False
    type = 'page'
    force_json = False
    message = ''
    events = []

    def __init__(self, request, *args, **kwargs):

        self.error = kwargs.pop('error', False)
        self.message = kwargs.pop('message', '')
        self.events = kwargs.pop('events', [])
        self.force_json = kwargs.pop('force_json', False)
        self.type = kwargs.pop('type', None)
        self.template = kwargs.pop('tpl', None)
        self.form = kwargs.pop('form', None)
        self.node = kwargs.pop('node', None)
        self.formsets = kwargs.pop('formsets', {})
        self.request = request

        if self.form:
            self.type = 'form'
        elif self.message:
            self.type = 'message'
        if not self.type:
            self.type = 'page'

        data = dict()

        if self.type == 'page':
            if self.node:
                data['node'] = self.node
            ctx = RequestContext(request, kwargs.pop('ctx', {}))
            content = render_to_string(self.template, ctx)
            data.update({
                'type': self.type,
                'error': self.error,
                'content': content,
            })
        elif self.type == 'form':
            data.update({
                'type': 'form',
                'formid': request.POST.get("__form_id"),
                'form_auto_id': self.form.auto_id,
                })
            error = False
            errors = {}
            if self.form.errors:
                for key, val in self.form.errors.items():
                    if key == '__all__':
                        field = self.__class__.form_field_all(self.form)
                        errors[field] = [unicode(v) for v in val]
                    else:
                        errors[key] = [unicode(v) for v in val]
                error = True

            for name, fs in self.formsets.items():
                for i, form in enumerate(fs.forms):
                    if form.errors:
                        error = True
                        for key, val in form.errors.items():
                            if key == '__all__':
                                field = self.__class__.form_field_all(form)
                                errors[field] = [unicode(v) for v in val]
                            else:
                                errors["%s-%s" % (
                                    form.prefix,
                                    key,
                                    )] = [unicode(v) for v in val]
            data.update({
                'error': error,
                'errors': errors,
                'message': self.message,
            })
        elif self.type == 'message':
            data.update({
                'error': self.error,
                'message': self.message,
            })
        else:
            raise NotImplementedError

        data.update({
            'events': self.events,
        })
        if request.is_ajax() or self.force_json:
            kwargs['content'] = json.dumps(data)
            kwargs['content_type'] = 'application/json'
        else:
            kwargs['content'] = ("<html><body><textarea>"
                + json.dumps(data) +
                "</textarea></boby></html>")
        super(JsonResponse, self).__init__(*args, **kwargs)

    @staticmethod
    def form_field_all(form):
        if form.prefix:
            field = form.prefix + "-__all__"
        else:
            field = "__all__"
        return field


def _generic_delete(request, oid, model):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    instance = model.objects.get(id=oid)
    if request.method == "POST":
        instance.delete()
        return JsonResponse(request,
            message="%s deleted" % (model._meta.verbose_name, ),
            events=["refreshTree()"],
            )

    return render(request, "generic_delete.html", {
        'instance': instance,
    })


def start(request):
    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()

    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)

    server = jsonrpclib.Server(url, transport=trans)
    auth = server.plugins.is_authenticated(
        request.COOKIES.get("sessionid", ""))
    jail = json.loads(server.plugins.jail.info())[0]
    assert auth

    try:
        bacula = models.BaculaSDStorage.objects.order_by('-id')[0]
        bacula.enable = True
        bacula.save()
    except IndexError:
        bacula = models.BaculaSDStorage.objects.create(enable=True)

    try:
        form = forms.BaculaSDStorageForm(bacula.__dict__, instance=bacula)
        form.is_valid()
        form.save()
    except ValueError:
        return HttpResponse(simplejson.dumps({
            'error': True,
            'message': 'Bacula data did not validate, configure it first.',
            }), content_type='application/json')

    cmd = "%s onestart" % utils.bacula_control
    pipe = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
        shell=True, close_fds=True)

    out = pipe.communicate()[0]
    return HttpResponse(simplejson.dumps({
        'error': False,
        'message': out,
        }), content_type='application/json')


def stop(request):
    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)

    server = jsonrpclib.Server(url, transport=trans)
    auth = server.plugins.is_authenticated(
        request.COOKIES.get("sessionid", ""))
    jail = json.loads(server.plugins.jail.info())[0]
    assert auth

    try:
        bacula = models.BaculaSDStorage.objects.order_by('-id')[0]
        bacula.enable = False
        bacula.save()
    except IndexError:
        bacula = models.BaculaSDStorage.objects.create(enable=False)

    try:
        form = forms.BaculaSDStorageForm(bacula.__dict__, instance=bacula)
        form.is_valid()
        form.save()
    except ValueError:
        pass

    cmd = "%s onestop" % utils.bacula_control
    pipe = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE,
        shell=True, close_fds=True)

    out = pipe.communicate()[0]
    return HttpResponse(simplejson.dumps({
        'error': False,
        'message': out,
        }), content_type='application/json')


def edit(request):
    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)

    """
    Get the Bacula object
    If it does not exist create a new entry
    """
    try:
        bacula = models.BaculaSDStorage.objects.order_by('-id')[0]
    except IndexError:
        bacula = models.BaculaSDStorage.objects.create()

    try:
        server = jsonrpclib.Server(url, transport=trans)
        jail = json.loads(server.plugins.jail.info())[0]
        auth = server.plugins.is_authenticated(
            request.COOKIES.get("sessionid", ""))
        assert auth
    except Exception:
        raise

    if request.method == "GET":
        form = forms.BaculaSDStorageForm(instance=bacula,
            jail=jail)
        return render(request, "edit.html", {
            'form': form,
        })

    if not request.POST:
        return JsonResponse(request, error=True, message="A problem occurred.")

    form = forms.BaculaSDStorageForm(request.POST,
        instance=bacula,
        jail=jail)
    if form.is_valid():
        form.save()
        return JsonResponse(request,
            error=True,
            message="Bacula settings successfully saved.")

    return JsonResponse(request, form=form)


def treemenu(request):
    """
    This is how we inject nodes to the Tree Menu

    The FreeNAS GUI will access this view, expecting for a JSON
    that describes a node and possible some children.
    """

    daemons = []
    for obj in models.BaculaSDStorage.objects.all():
        daemons.append({
            'name': unicode(obj),
            'type': 'pluginsfcgi',
            'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_storage_daemon.png'}),
            'url': reverse('bacula_daemons_edit', kwargs={'oid': obj.id}),
            })
    daemons.append({
        'name': 'Add Daemon',
        'type': 'pluginsfcgi',
        'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_add_storage.png'}),
            'url': reverse('bacula_daemons_new'),
    })

    directors = []
    for obj in models.BaculaSDDirector.objects.all():
        directors.append({
            'name': unicode(obj),
            'type': 'pluginsfcgi',
            'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_director.png'}),
            'url': reverse('bacula_directors_edit', kwargs={'oid': obj.id}),
            })
    directors.append({
        'name': 'Add Director',
        'type': 'pluginsfcgi',
        'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_add_director.png'}),
            'url': reverse('bacula_directors_new'),
    })

    directorassigns = []
    for obj in models.BaculaSDDirectorAssignment.objects.all():
        directorassigns.append({
            'name': unicode(obj),
            'type': 'pluginsfcgi',
            'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_director_map.png'}),
            'url': reverse('bacula_directorassigns_edit', kwargs={'oid': obj.id}),
            })
    directorassigns.append({
        'name': 'Add Director Assignment',
        'type': 'pluginsfcgi',
        'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_add_director_map.png'}),
            'url': reverse('bacula_directorassigns_new'),
    })

    devices = []
    for obj in models.BaculaSDDevice.objects.all():
        devices.append({
            'name': unicode(obj),
            'type': 'pluginsfcgi',
            'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_device.png'}),
            'url': reverse('bacula_devices_edit', kwargs={'oid': obj.id}),
            })
    devices.append({
        'name': 'Add Device',
        'type': 'pluginsfcgi',
        'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_add_device.png'}),
            'url': reverse('bacula_devices_new'),
    })

    deviceassigns = []
    for obj in models.BaculaSDDeviceAssignment.objects.all():
        deviceassigns.append({
            'name': unicode(obj),
            'type': 'pluginsfcgi',
            'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_device_map.png'}),
            'url': reverse('bacula_deviceassigns_edit', kwargs={'oid': obj.id}),
            })
    deviceassigns.append({
        'name': 'Add Device Assignment',
        'type': 'pluginsfcgi',
        'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_add_device_map.png'}),
            'url': reverse('bacula_deviceassigns_new'),
    })

    messages = []
    for obj in models.BaculaSDMessages.objects.all():
        messages.append({
            'name': unicode(obj),
            'type': 'pluginsfcgi',
            'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_messages.png'}),
            'url': reverse('bacula_messages_edit', kwargs={'oid': obj.id}),
            })
    messages.append({
        'name': 'Add Message',
        'type': 'pluginsfcgi',
        'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_add_messages.png'}),
            'url': reverse('bacula_messages_new'),
    })

    messagesassigns = []
    for obj in models.BaculaSDMessagesAssignment.objects.all():
        messagesassigns.append({
            'name': unicode(obj),
            'type': 'pluginsfcgi',
            'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_messages_map.png'}),
            'url': reverse('bacula_messagesassigns_edit', kwargs={'oid': obj.id}),
            })
    messagesassigns.append({
        'name': 'Add Message Assignment',
        'type': 'pluginsfcgi',
        'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_add_messages_map.png'}),
            'url': reverse('bacula_messagesassigns_new'),
    })

    plugin = {
        'name': 'Bacula Storage',
        'append_to': 'services.PluginsJail',
        'icon': reverse('treemenu_icon'),
        'type': 'pluginsfcgi',
        'url': reverse('bacula_edit'),
        'children': [
            {
                'name': 'Storage Daemons',
                'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_storage_daemon.png'}),
                'children': daemons,
            },
            {
                'name': 'Directors',
                'children': directors,
                'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_director.png'}),
            },
            {
                'name': 'Director Assignments',
                'children': directorassigns,
                'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_director_map.png'}),
            },
            {
                'name': 'Devices',
                'children': devices,
                'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_device.png'}),
            },
            {
                'name': 'Device Assignments',
                'children': deviceassigns,
                'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_device_map.png'}),
            },
            {
                'name': 'Messages',
                'children': messages,
                'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_messages.png'}),
            },
            {
                'name': 'Messages Assignment',
                'children': messagesassigns,
                'icon': reverse('bacula_media', kwargs={'path': 'images/tree/bacula_messages_map.png'}),
            },
        ],
    }

    return HttpResponse(json.dumps([plugin]), content_type='application/json')


def status(request):
    """
    Returns a dict containing the current status of the services

    status can be one of:
        - STARTING
        - RUNNING
        - STOPPING
        - STOPPED
    """
    pid = None

    proc = Popen(["/usr/bin/pgrep", "bacula-sd"], stdout=PIPE, stderr=PIPE)

    stdout = proc.communicate()[0]

    if proc.returncode == 0:
        status = 'RUNNING'
        pid = stdout.split('\n')[0]
    else:
        status = 'STOPPED'

    return HttpResponse(json.dumps({
            'status': status,
            'pid': pid,
        }),
        content_type='application/json')


def treemenu_icon(request):

    with open(utils.bacula_icon, 'rb') as f:
        icon = f.read()

    return HttpResponse(icon, content_type='image/png')


def devices_new(request):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    if request.method == "POST":
        form = forms.BaculaSDDeviceForm(request.POST, jail=jail)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Device added",
                events=["refreshTree()"],
                )
        return JsonResponse(request, tpl="devices_new.html", ctx={
            'form': form,
        })
    else:
        form = forms.BaculaSDDeviceForm(jail=jail)

    return render(request, "devices_new.html", {
        'form': form,
    })


def devices_view(request):
    return render(request, "devices_view.html", {})


def devices_edit(request, oid):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    instance = models.BaculaSDDevice.objects.get(id=oid)
    delete_url = reverse('bacula_devices_delete', kwargs={'oid': instance.id})
    if request.method == "POST":
        form = forms.BaculaSDDeviceForm(request.POST, instance=instance, jail=jail)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Device assignment updated",
                events=["refreshTree()"],
                )
        return JsonResponse(request, tpl="devices_edit.html", ctx={
            'form': form,
            'delete_url': delete_url,
        })
    else:
        form = forms.BaculaSDDeviceForm(instance=instance, jail=jail)

    return render(request, "devices_edit.html", {
        'form': form,
        'delete_url': delete_url,
    })


def devices_delete(request, oid):
    return _generic_delete(request, oid, model=models.BaculaSDDevice)


def deviceassigns_new(request):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    if request.method == "POST":
        form = forms.BaculaSDDeviceAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Device assignment added",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="deviceassigns_new.html", ctx={
            'form': form,
        })
    else:
        form = forms.BaculaSDDeviceAssignmentForm()

    return render(request, "deviceassigns_new.html", {
        'form': form,
    })


def deviceassigns_view(request):
    return render(request, "deviceassigns_view.html", {})


def deviceassigns_edit(request, oid):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    instance = models.BaculaSDDeviceAssignment.objects.get(id=oid)
    delete_url = reverse('bacula_deviceassigns_delete', kwargs={'oid': oid})
    if request.method == "POST":
        form = forms.BaculaSDDeviceAssignmentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Device assignment updated",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="deviceassigns_edit.html", ctx={
            'form': form,
            'delete_url': delete_url,
        })
    else:
        form = forms.BaculaSDDeviceAssignmentForm(instance=instance)

    return render(request, "deviceassigns_edit.html", {
        'form': form,
        'delete_url': delete_url,
    })


def deviceassigns_delete(request, oid):
    return _generic_delete(request, oid, model=models.BaculaSDDeviceAssignment)


def directors_new(request):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    if request.method == "POST":
        form = forms.BaculaSDDirectorForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Director added",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="directors_new.html", ctx={
            'form': form,
        })
    else:
        form = forms.BaculaSDDirectorForm()

    return render(request, "directors_new.html", {
        'form': form,
    })


def directors_edit(request, oid):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    instance = models.BaculaSDDirector.objects.get(id=oid)
    delete_url = reverse('bacula_directors_delete', kwargs={'oid': oid})
    if request.method == "POST":
        form = forms.BaculaSDDirectorForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Director updated",
                events=["refreshTree()"],
                )
        return JsonResponse(request, tpl="directors_edit.html", ctx={
            'form': form,
            'delete_url': delete_url,
        })
    else:
        form = forms.BaculaSDDirectorForm(instance=instance)

    return render(request, "directors_edit.html", {
        'form': form,
        'delete_url': delete_url,
    })


def directors_view(request):
    return render(request, "devices_view.html", {})


def directors_delete(request, oid):
    return _generic_delete(request, oid, model=models.BaculaSDDirector)


def directorassigns_new(request):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    if request.method == "POST":
        form = forms.BaculaSDDirectorAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Director assignment added",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="directorassigns_new.html", ctx={
            'form': form,
        })
    else:
        form = forms.BaculaSDDirectorAssignmentForm()

    return render(request, "directorassigns_new.html", {
        'form': form,
    })


def directorassigns_edit(request, oid):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    instance = models.BaculaSDDirectorAssignment.objects.get(id=oid)
    delete_url = reverse('bacula_directorassigns_delete', kwargs={'oid': oid})
    if request.method == "POST":
        form = forms.BaculaSDDirectorAssignmentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Director assignment updated",
                events=["refreshTree()"],
                )
        return JsonResponse(request, tpl="directorassigns_edit.html", ctx={
            'form': form,
            'delete_url': delete_url,
        })
    else:
        form = forms.BaculaSDDirectorAssignmentForm(instance=instance)

    return render(request, "directorassigns_edit.html", {
        'form': form,
        'delete_url': delete_url,
    })


def directorassigns_view(request):
    return render(request, "devices_view.html", {})


def directorassigns_delete(request, oid):
    return _generic_delete(request, oid, model=models.BaculaSDDirectorAssignment)


def daemons_new(request):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    if request.method == "POST":
        form = forms.BaculaSDStorageForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Daemon added",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="daemons_new.html", ctx={
            'form': form,
        })
    else:
        form = forms.BaculaSDStorageForm()

    return render(request, "daemons_new.html", {
        'form': form,
    })


def daemons_edit(request, oid):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    instance = models.BaculaSDStorage.objects.get(id=oid)
    delete_url = reverse('bacula_daemons_delete', kwargs={'oid': oid})
    if request.method == "POST":
        form = forms.BaculaSDStorageForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Daemon updated",
                events=["refreshTree()"],
                )
        return JsonResponse(request, tpl="daemons_edit.html", ctx={
            'form': form,
            'delete_url': delete_url,
        })
    else:
        form = forms.BaculaSDStorageForm(instance=instance)

    return render(request, "daemons_edit.html", {
        'form': form,
        'delete_url': delete_url,
    })


def daemons_view(request):
    return render(request, "daemons_view.html", {})


def daemons_delete(request, oid):
    return _generic_delete(request, oid, model=models.BaculaSDStorage)


def messages_new(request):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    if request.method == "POST":
        form = forms.BaculaSDMessagesForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Message added",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="messages_new.html", ctx={
            'form': form,
        })
    else:
        form = forms.BaculaSDMessagesForm()

    return render(request, "messages_new.html", {
        'form': form,
    })


def messages_view(request):
    return render(request, "messages_view.html", {})


def messages_edit(request, oid):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    instance = models.BaculaSDMessages.objects.get(id=oid)
    delete_url = reverse('bacula_messages_delete', kwargs={'oid': oid})
    if request.method == "POST":
        form = forms.BaculaSDMessagesForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Message updated",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="messages_edit.html", ctx={
            'form': form,
            'delete_url': delete_url,
        })
    else:
        form = forms.BaculaSDMessagesForm(instance=instance)

    return render(request, "messages_edit.html", {
        'form': form,
        'delete_url': delete_url,
    })


def messages_delete(request, oid):
    return _generic_delete(request, oid, model=models.BaculaSDMessages)


def messagesassigns_new(request):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    if request.method == "POST":
        form = forms.BaculaSDMessagesAssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Message added",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="messagesassigns_new.html", ctx={
            'form': form,
        })
    else:
        form = forms.BaculaSDMessagesAssignmentForm()

    return render(request, "messagesassigns_new.html", {
        'form': form,
    })


def messagesassigns_view(request):
    return render(request, "messagesassigns_view.html", {})


def messagesassigns_edit(request, oid):

    bacula_key, bacula_secret = utils.get_bacula_oauth_creds()
    url = utils.get_rpc_url(request)
    trans = OAuthTransport(url, key=bacula_key,
        secret=bacula_secret)
    server = jsonrpclib.Server(url, transport=trans)

    jail = json.loads(server.plugins.jail.info())[0]
    instance = models.BaculaSDMessagesAssignment.objects.get(id=oid)
    delete_url = reverse('bacula_messagesassigns_delete', kwargs={'oid': oid})
    if request.method == "POST":
        form = forms.BaculaSDMessagesAssignmentForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse(request,
                message="Message updated",
                events=["refreshTree()"],
            )
        return JsonResponse(request, tpl="messagesassigns_edit.html", ctx={
            'form': form,
            'delete_url': delete_url,
        })
    else:
        form = forms.BaculaSDMessagesAssignmentForm(instance=instance)

    return render(request, "messagesassigns_edit.html", {
        'form': form,
        'delete_url': delete_url,
    })


def messagesassigns_delete(request, oid):
    return _generic_delete(request, oid, model=models.BaculaSDMessagesAssignment)
