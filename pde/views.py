import django_otp
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.shortcuts import render
from django.template.defaultfilters import register
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey
from two_factor.views import OTPRequiredMixin
from two_factor.views.mixins import TemplateResponse
from encrypted_files.base import EncryptedFile
from .models import PDE
from rest_framework.decorators import api_view
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django_otp.decorators import otp_required
import hashlib
from django.dispatch import receiver

from two_factor.signals import user_verified
# Create your views here.
import subprocess
from django.core.exceptions import SuspiciousOperation
import os
import magic
from django.conf import settings
from django.http import HttpResponse
from profile import profile


@login_required
@csrf_protect
def index(request):

    dis = PDE.objects.order_by('date').all().reverse()
    admin = request.user.is_staff
    username = request.user.get_username()
    search = request.GET.get('search', '')
    dis = dis.filter(user__icontains=search)

    combined = []
    for x in dis:
        there = False
        for c in combined:
            if x.user == c.user:
                there = True
        if not there:
            combined.append(x)

    paginator = Paginator(combined, 15)
    page = request.GET.get('page')
    combined = paginator.get_page(page)

    context = {
        # 'pde': data,
        'dfi': request.user,
        'dis': combined,
        'admin': admin,
        'username': username,
        'len': len(combined),
        'search': search
        # 'last_updated': last_updated,
    }
    return render(request, 'pde/index.html', context)


@login_required
@csrf_protect
def details(request, user):
    username = request.user.get_username()
    admin = request.user.is_staff
    data = []
    if user == username or admin:
        data = PDE.objects.filter(user=user).order_by('date').reverse()

    info = subprocess.check_output(["borg", "info", os.path.join(settings.BORG_PATH, data[0].machine)], text=True, input=data[0].api.prefix, stderr=subprocess.STDOUT)

    search = request.GET.get('search', '')
    if search.isdigit():
        data1 = data.filter(filename__icontains=search)
        # data2 = data.filter(hash__icontains=search)
        data3 = data.filter(ip__contains=search)
        data4 = data.filter(rank__gt=search)
        data = data1 | data3 | data4
    else:
        data1 = data.filter(rank__icontains=search)
        # data2 = data.filter(hash__icontains=search)
        data3 = data.filter(ip__contains=search)
        data4 = data.filter(filename__icontains=search)
        data = data1 | data3 | data4

    for d in data:
        d.meta = d.meta.replace("Malicious", "<span class='text-danger'>Malicious</span>")
    paginator = Paginator(data, 9)
    page = request.GET.get('page')
    data = paginator.get_page(page)

    context = {
        'dfi': request.user,
        'pde': data,
        'user': user,
        'admin': admin,
        'username': username,
        'len': len(data),
        'search': search,
        'info': "<br/>".join(info.split("\n")[8:]).replace("\n", "<br/><br/>").replace(" ", "&nbsp;") + "&nbsp;Number of entries: " + str(len(data)) + "<br/>------------------------------------------------------------------------------<br/>" 
    }
    return render(request, 'pde/details.html', context)


# @otp_required
# def serve(request, path):
#     response = FileResponse(open(settings.MEDIA_ROOT+'\\pde\\files\\'+path, 'rb'))
#     return response


@register.filter(name='trim')
def trim(value):
    if '/' in value:
        return value.split('/')[-1]
    else:
        return value.split('\\')[-1]


@api_view(['POST', ])
@profile
@csrf_exempt
def add(request):
    """Endpoints for listing and retrieving PDE."""
    try:
        parser_classes = (FileUploadParser,)
        ip = strip_tags(request.POST.get("ip", False))
        machine = strip_tags(request.POST.get("machine", False))
        user = strip_tags(request.POST.get("user", False))
        rank = float(strip_tags(request.POST.get("rank", False)))
        filename = strip_tags(request.POST.get("filename", False))
        meta = strip_tags(request.POST.get("meta", False))
        pde = request.FILES.get('pde', False)
        originHash = strip_tags(request.POST.get('md5sum', False))
        key = request.META.get('HTTP_X_API_KEY', False).split(" ")[-1]
        api = APIKey.objects.get(prefix=key.split(".")[0])

        response = {"status": 'Error', "message": "Something went wrong"}
        if request.META["HTTP_MD5SUM"] != originHash:
            raise SuspiciousOperation("Hash digest different from header and post data")
        out = ""
        if ip and machine and user and rank != "" and filename and pde and originHash and api:
            n = PDE.objects.create(ip=ip, machine=machine, user=user, rank=rank,
                                filename=filename, hash=originHash, api=api, meta=meta)
            response = {"status": 'Success'}
            try:
                if not os.path.exists(os.path.join(settings.BORG_PATH, machine)): 
                    if not os.path.exists(settings.BORG_PATH):
                        os.mkdir(settings.BORG_PATH)
                    out = subprocess.check_output(["borg", "init", "--encryption", "repokey-blake2", os.path.join(settings.BORG_PATH, machine)], text=True, input=api.prefix+"\n"+api.prefix, stderr=subprocess.STDOUT)
                    print(out)
                # borg create --compression zlib,N /path/to/repo::arch ~
                out = subprocess.check_output(["borg", "create", "--compression", "obfuscate,3,auto,zstd,10", os.path.join(settings.BORG_PATH, machine)+"::"+originHash, pde.temporary_file_path()], text=True, input=api.prefix, stderr=subprocess.STDOUT)
                print(out)
                if "already exists" in out:
                    response = {"status": "Success", "message": "File already stored, not storing again."}
                n.snapshot_name = pde.temporary_file_path()
                n.save()
            except subprocess.CalledProcessError as ee:
                print(ee.output)
                if "already exists" in ee.output:
                    response = {"status": "Success", "message": "File already stored, not storing again."}
                else:
                    response = {"status": "Error", "message": "Failed to store PDE file with Borg: " + str(ee)}

    except SuspiciousOperation as e:
            response = {"status": 'Error', "message": str(e)}
    permission_classes = (HasAPIKey,)
    return Response(response)


@receiver(user_verified)
def test_receiver(request, user, device, **kwargs):
    current_site = get_current_site(request)
    if device.name == 'backup':
        message = 'Hi %(username)s,\n\n'\
                'You\'ve verified yourself using a backup device '\
                'on %(site_name)s. If this wasn\'t you, your '\
                'account might have been compromised. You need to '\
                'change your password at once, check your backup '\
                'phone numbers and generate new backup tokens.'\
                % {'username': user.get_username(),
                'site_name': current_site.name}
        user.email_user(subject='Backup token used', message=message)


@login_required
@otp_required
@csrf_protect
def get(request, h):
    msg = ""
    if request.method == "POST":
        token = request.POST.get("token", None)
        msg = ""
        print(token)
        if token:  # token
            if django_otp.match_token(request.user, token):
                if request.user.is_staff:
                    pde = PDE.objects.all().select_related("api")
                else:
                    pde = PDE.objects.filter(user=request.user.get_username()).select_related("api")
                
                for p in pde:
                    if p.hash == h:
                        pde = p
                        break
                if pde:
                    if not os.path.exists("tmp"):
                        os.mkdir("tmp")
                    if not os.path.exists("tmp/"+h):
                        os.mkdir("tmp/"+h)
                    api = pde.api.prefix 
                    print(api)
                    p = subprocess.check_output(["borg", "extract", os.path.join("/SecureRS/"+settings.BORG_PATH, pde.machine)+"::"+pde.hash], cwd="tmp/"+h, input=api.encode('utf-8'))
                    
                    with open("./tmp/"+h + pde.snapshot_name, 'rb') as f:  
                        content = f.read()
                        m = hashlib.md5()
                        m.update(content)
                        message = 'Hi %(username)s,\n\n' \
                                'You\'ve verified yourself and just downloaded a PDE file with the following details: \n\n' \
                                'File: %(path)s\n' \
                                'MD5: %(md5)s\n' \
                                % {'username': request.user.get_username(), 'path': pde.filename, 'md5': m.hexdigest()}
                        request.user.email_user(
                            subject='PDE Download Success', message=message)

                        response = HttpResponse(content, content_type=magic.Magic(
                            mime=True).from_buffer(content))
                        response['Content-Disposition'] = 'attachment; filename=' + pde.filename
                        # os.remove("./tmp/"+h + "/" + pde.snapshot_name)
                        return response

                return HttpResponse(status=404)
            else:
                msg = "Invalid token, please try again."
        else:
            msg = "Invalid token, please try again."
    
    context = {
        'dfi': request.user,
        'message': msg,
    }
    return render(request, 'pde/otp.html', context) 
