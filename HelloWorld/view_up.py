# -*- coding: utf-8 -*-
 
from django.shortcuts import render
from django.views.decorators import csrf
import os
import sys
from BackEnd import UserGuide_BE

def index(request):
    context = {}
    return render(request, 'index.html', context)
	
def problem_type(request):
    context = {}
    return render(request, 'problem_type.html', context)

def submit_data(request,problem_type):
    context = {}
    if (problem_type=='1'):
        context['pt']='分类'
    if (problem_type=='2'):
        context['pt']='回归'
    if (problem_type=='3'):
        context['pt']='排序'

    #Define the problem class    
    global problem
    problem = context['pt']

    return render(request, 'submit_data.html', context)

def submit_label(request):
    context = {}
    global UG_BE 
    UG_BE = UserGuide_BE()
    feature_list = UG_BE.GetHeader()
    feature_list.append('None')
    context['feature_list'] = feature_list #请将你的feature_name_list替换到这个变量里,您的训练和测试文件存储到了static/train.csv,static/test.csv
    return render(request, 'submit_label.html', context)

def save_train_data(request):
    context = {}
    if request.method == "POST":
        f = request.FILES.get('train_data')
        baseDir = os.path.dirname(os.path.abspath(__name__));
        jpgdir = os.path.join(baseDir,'static');
    
        filename = os.path.join(jpgdir,'train.csv');
        fobj = open(filename,'wb');
        for chrunk in f.chunks():
            fobj.write(chrunk);
        fobj.close();
    
        f = request.FILES.get('test_data')
        baseDir = os.path.dirname(os.path.abspath(__name__));
        jpgdir = os.path.join(baseDir,'static');
    
        filename = os.path.join(jpgdir,'test.csv');
        fobj = open(filename,'wb');
        for chrunk in f.chunks():
            fobj.write(chrunk);
        fobj.close();

        return submit_label(request);
        
    else:
        return submit_label(request);


def submit_type(request,context):
    #您的id为context['id_name'], 您的target为context['target_name']
    #以下请您填充header以及数据第一行和第二行
    global UG_BE
    context['sample'] = UG_BE.GetSamples(context['id_name'], context['target_name'])

    #context['sample']=[{'header_line':'usersiid','first_line':'06055167','second_line':'08055108'},{'header_line':'sex','first_line':'male','second_line':'female'},{'header_line':'age','first_line':'23','second_line':'19'},{'header_line':'job','first_line':'doctor','second_line':'engineer'}]
    return render(request, 'submit_type.html', context)

def save_id_target(request):
    global UG_BE
    context = {}
    if request.method == "POST":
        id_name=request.POST['id_name']
        target_name=request.POST['target_name']
    context['id_name']=id_name;
    context['target_name']=target_name;
    UG_BE.AddParam('ID', id_name)
    UG_BE.AddParam('Label', target_name)
    return submit_type(request, context)


def save_feature_type(request):
    global UG_BE
    ID = UG_BE.GetParam('ID')
    Label = UG_BE.GetParam('Label')

    context = {}
    if request.method == "POST":
        header = UG_BE.GetFeatureHeader(ID, Label)
        feature_type = list()
        error_col_list = list()
        for elm in header:
            type_from_user = request.POST[elm].encode('u8')
            if (UG_BE.check_type(elm, type_from_user)):
                feature_type.append((elm, type_from_user))
            else:
                error_col_list.append(elm)
 
    if (len(error_col_list) > 0):
        context['error'] = "一部分列数据格式有问题，请再次检测，有问题的列如下:\n" 
        for i in error_col_list:
            context['error'] += str(i) + ','
        context['error'] = context['error'][:-1]
        #Error change the way  from here

    for elm, elm_type in feature_type:
        context[elm] = elm_type
    
    UG_BE.AddParam('DataType', context)

    #Assign Problem Param
    global problem
    UG_BE.AddParam('Problem', problem)

    # print "This problem is %s" %(UG_BE.param['Problem'])
    # print "This ID is %s" %(UG_BE.param['ID'])
    # print "This Label is %s" %(UG_BE.param['Label'])
    # for key, value in UG_BE.param['DataType'].iteritems():
    #     print key, value

    UG_BE.TriggerModel()
    UG_BE.WritePredictResults()

    return render(request, 'finished.html', context)
