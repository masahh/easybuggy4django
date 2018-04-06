import time
import os
import psutil
import numpy as np

from time import sleep
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from .models import User


a = []


def index(request):
    d = {'title': 'EasyBuggy Django'}
    return render(request, 'index.html', d)


def deadlock2(request):
    d = {
        'title': _('title.deadlock2.page'),
        'note': _('msg.note.deadlock2'),
    }
    order = get_order(request)
    if request.method == 'POST':
        with transaction.atomic():
            number = 0
            while True:
                number += 1
                uid = request.POST.get("uid_" + str(number))
                if uid is None:
                    break
                user = User.objects.get(id=uid)
                user.name = request.POST.get(uid + "_name")
                user.phone = request.POST.get(uid + "_phone")
                user.mail = request.POST.get(uid + "_mail")
                user.save()
                sleep(1)

    d['users'] = User.objects.raw("SELECT * FROM easybuggy_user WHERE ispublic = 'true' ORDER BY id " + order)
    d['order'] = order
    return render(request, 'deadlock2.html', d)


def infiniteloop(request):
    i = 1
    while 0 < i:
        i += 1


def redirectloop(request):
    return redirect("/redirectloop")


def memoryleak(request):
    leak_memory()
    d = {
        'title': _('title.memoryleak.page'),
        'note': _('msg.note.memoryleak'),
    }
    try:
        ps = psutil.Process(os.getpid())
        mem = ps.memory_full_info()
        d = {
            'title': _('title.memoryleak.page'),
            'note': _('msg.note.memoryleak'),
            'pid': ps.pid,
            'rss': convert_bytes(mem.rss),
            'pcnt_rss': round(ps.memory_percent(memtype='rss'), 2),
            # 'vms': mem.vms,
            # 'shared': mem.shared,
            # 'text': mem.text,
            # 'lib': mem.lib,
            # 'data': mem.data,
            # 'dirty': mem.dirty,
            'uss': convert_bytes(mem.uss),
            'pcnt_uss': round(ps.memory_percent(memtype='uss'), 2),
            'pss': convert_bytes(mem.pss),
            'pcnt_pss': round(ps.memory_percent(memtype='pss'), 2),
            'swap': convert_bytes(mem.swap),
            'info': ps.as_dict(attrs=["cmdline", "username"]),
        }
    except psutil.AccessDenied:
        pass
    except psutil.NoSuchProcess:
        pass
    return render(request, 'memoryleak.html', d)


def commandinjection(request):
    d = {
        'title': _('title.commandinjection.page'),
        'note': _('msg.note.commandinjection'),
    }
    if request.method == 'POST':
        address = request.POST.get("address")
        cmd = 'echo "This is for testing." | mail -s "Test Mail" -r from@example.com ' + address
        if os.system(cmd) == 0:
            d['result'] = _('msg.send.mail.success')
        else:
            d['result'] = _('msg.send.mail.failure')
    return render(request, 'commandinjection.html', d)


def iof(request):
    d = {
        'title': _('title.intoverflow.page'),
        'note': _('msg.note.intoverflow'),
    }
    if request.method == 'POST':
        str_times = request.POST.get("times")

        if str_times is not None and str_times is not '':
            times = int(str_times)
            if times >= 0:
                # TODO Change a better way
                thickness = int(np.array([2 ** times, ], dtype=int)) / 10  # mm
                thickness_m = int(thickness) / 1000  # m
                thickness_km = int(thickness_m) / 1000  # km

                d['description'] = times + 1

                if times >= 0:
                    d['times'] = str_times
                    description = str(thickness) + " mm"
                    if thickness_m is not None and thickness_km is not None:
                        if thickness_m >= 1 and thickness_km < 1:
                            description = description + " = " + str(thickness_m) + " m"
                        if thickness_km >= 1:
                            description = description + " = " + str(thickness_km) + " km"
                    if times == 42:
                        description = description + " : " + _('msg.answer.is.correct')
                    d['description'] = description

    return render(request, 'intoverflow.html', d)


def lotd(request):
    d = {
        'title': _('title.lossoftrailingdigits.page'),
        'note': _('msg.note.lossoftrailingdigits'),
    }
    if request.method == 'POST':
        number = request.POST["number"]
        d['number'] = number
        if number is not None and -1 < float(number) < 1:
            d['result'] = float(number) + 1
    return render(request, 'lossoftrailingdigits.html', d)


def roe(request):
    d = {
        'title': _('title.roundofferror.page'),
        'note': _('msg.note.roundofferror'),
    }
    if request.method == 'POST':
        number = request.POST["number"]
        d['number'] = number
        if number is not None and number is not "0" and number.isdigit():
            d['result'] = float(number) - 0.9
    return render(request, 'roundofferror.html', d)


def te(request):
    d = {
        'title': _('title.truncationerror.page'),
        'note': _('msg.note.truncationerror'),
    }
    if request.method == 'POST':
        number = request.POST["number"]
        d['number'] = number
        if number is not None and number is not "0" and number.isdigit():
            d['result'] = 10.0 / float(number)
    return render(request, 'truncationerror.html', d)


def xss(request):
    d = {
        'title': _('title.xss.page'),
        'msg': _('msg.enter.string'),
        'note': _('msg.note.xss'),
    }
    if request.method == 'POST':
        input_str = request.POST["string"]
        if input_str is not None:
            d['msg'] = input_str[::-1]

    return render(request, 'xss.html', d)


def sqlijc(request):
    d = {
        'title': _('title.sqlijc.page'),
        'note': _('msg.note.sqlijc'),
    }
    if request.method == 'POST':
        name = request.POST["name"]
        password = request.POST["password"]
        d['users'] = User.objects.raw("SELECT * FROM easybuggy_user WHERE ispublic = 'true' AND name='" + name +
                                      "' AND password='" + password + "' ORDER BY id")

    return render(request, 'sqlijc.html', d)


# -------- private method
def get_order(request):
    order = request.GET.get("order")
    if order == 'asc':
        order = 'desc'
    else:
        order = 'asc'
    return order


def leak_memory():
    global a
    for i in range(100000):
        a.append(time.time())


def convert_bytes(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n
