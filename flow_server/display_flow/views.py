import time
import io
import base64
import datetime
import pytz
import random

from collections import OrderedDict

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

import django.db.models as models 
from .models import Flow

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from matplotlib.font_manager import FontProperties

def createGraph(data, period, dateFormat):
    timezoneOffset = -datetime.timedelta(hours=8)
    y = list(map(lambda a: a.val, data))
    x = list(map(lambda a: datetime.datetime.utcfromtimestamp(a.timestamp) + timezoneOffset, data))

    fig = Figure()
    ax = fig.add_subplot(111)


    reps = OrderedDict([('%',''), ('H','Hour'), ('M','Minute'), ('S', 'Second'), ('a','Day')])
    formattedDate = dateFormat
    for i, j in reps.items():
        formattedDate = formattedDate.replace(i, j)
    
    ax.plot_date(x,y,'-')
    ax.xaxis.set_major_formatter(DateFormatter(dateFormat))
    labelProperties = {'font_properties' : FontProperties(size='large', weight='bold')}
    titleProperties = {'font_properties' : FontProperties(size='x-large', weight='bold')}
    ax.set_xlabel('Time ({})'.format(formattedDate), labelProperties)
    ax.set_ylabel('Flow Rate (L/Min)', labelProperties)
    ax.set_title('Flow Rate Over The Past ' + period, titleProperties)
    ax.set_ylim(bottom=0)
    ax.grid(color='k', linestyle='--')
    fig.autofmt_xdate()

    canvas = FigureCanvas(fig)

    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def getMaxFlow(seconds):
    return Flow.objects.filter(timestamp__gt=int(time.time())-seconds).aggregate(models.Max('val', output_field=models.FloatField()))

def current(request):
    latest = Flow.objects.latest('timestamp')
    return render(request, 'display_flow/current.html', {'latest_flow':latest.val})

def minute(request):
    return render(request, 'display_flow/minute.html', getMaxFlow(60))

def minute_image(request):
    past_minute = Flow.objects.filter(timestamp__gt=int(time.time())-60)
    return createGraph(past_minute, 'Minute', '%H:%M:%S')

def hour(request):
    return render(request, 'display_flow/hour.html', getMaxFlow(3600))

def hour_image(request):
    past_hour = Flow.objects.filter(timestamp__gt=int(time.time())-3600)
    return createGraph(past_hour, 'Hour', '%H:%M:%S')

def day(request):
    return render(request, 'display_flow/day.html', getMaxFlow(3600*24))

def day_image(request):
    past_day = Flow.objects.filter(timestamp__gt=int(time.time())-3600*24)
    return createGraph(past_day, 'Day', '%a-%H')

def week(request):
    return render(request, 'display_flow/week.html', getMaxFlow(3600*24*7))

def week_image(request):
    past_week = Flow.objects.filter(timestamp__gt=int(time.time())-3600*24*7)
    return createGraph(past_week, 'Week', '%a-%H')

def test(request):
    fig = Figure()
    ax = fig.add_subplot(111)
    x=[]
    y=[]
    now = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now += delta
        y.append(random.randint(0, 1000))

    ax.plot_date(x,y,'-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)

    return response

