import matplotlib

matplotlib.use('Agg')

import io
import matplotlib.pyplot as plt
import numpy as np
from pprint import pprint


def save_to_mime_img(filename):
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    binary_img = buf.getvalue()
    buf.close()
    # if JiraInfo().instance.is_debug():
    #     save_image(filename, binary_img)
    # plt.show()
    return binary_img


def generate_bar_chart(label, data, filename=None):
    ind = np.arange(len(data))
    fig, ax = plt.subplots()
    rects = ax.bar(ind, data, width=0.5)

    ax.set_title('Online Bug Summary')
    ax.set_ylabel("Count", fontsize=8)
    ax.set_xticks(ind)
    ax.set_xticklabels(label, fontsize=8)

    highest = max(data)
    for rect, i in zip(rects, data):
        ax.text(rect.get_x() + rect.get_width() / 2, i + highest * 0.02, str(i), color='black', ha='center',
                fontweight='bold', fontsize=8)
    return save_to_mime_img(filename)


def generate_barh_chart(label, data, filename=None):
    ind = np.arange(len(data))
    fig, ax = plt.subplots()
    rects = ax.barh(ind, data, height=0.5)

    ax.set_title('Priority')
    ax.set_xlabel("Count", fontsize=8)
    ax.set_ylabel("Level", fontsize=8)
    ax.set_yticks(ind)
    ax.set_yticklabels(label, fontsize=8)

    highest = max(data)
    for rect, i in zip(rects, data):
        ax.text(i + highest * 0.03, rect.get_y() + rect.get_height() / 2, str(i), color='black', ha='center',
                fontweight='bold', fontsize=8)
    return save_to_mime_img(filename)

def generate_barsuperpose_chart(label, data, colors, title, filename=None):
    data_original = data
    plt.clf()
    plt.title(title)
    classify_pre = None
    #先正排序
    data = dict(sorted(data.items(), key=lambda x: x[0]))
    for classify in data:
        if classify_pre is None:  
            data[classify] = np.array(data[classify]);
        else : 
            data[classify] = data[classify_pre] + np.array(data[classify]);
        classify_pre = classify
        ymax = max(data[classify]);
    width=0.5;
    x = np.array(label);
    
    #再反排序
    total_number=True
    data = dict(sorted(data.items(), key=lambda x: x[0], reverse=True))
    for classify in data:
        plt.bar(x,data[classify],width=width,color=colors[classify],label=classify,align='center');
        #打数字到bar上
        i = 0
        for a,b in zip(x,data[classify]):
            #打总数到Bar
            if total_number:
                plt.text(a, b+0.05, '%.0f' % b, ha='center', va= 'bottom',fontsize=12, color="blue")
            if data_original[classify][i] > 0 :
                #打每一个分段数字到bar
                plt.text(a, b-1.3, '%.0f' % data_original[classify][i], ha='center', va= 'bottom',fontsize=11)
            i = i + 1
        total_number=False #总数只打一次
    #设置x轴label
    axis = plt.gca().xaxis
    for label in axis.get_ticklabels():
        #label.set_color('blue')          # 设置每个刻度标签的颜色;
        label.set_rotation(30)            # 旋转45度;
        label.set_fontsize(6)             # 设置字体大小;
    plt.legend(loc='upper right');        #   
    return save_to_mime_img(filename)

def generate_pie_chart(label, data, filename=None, title='No-Title'):
    plt.clf()
    plt.title(title)

    label_with_num = [str(label[i]) + "(" + str(data[i]) + ")" for i in range(len(label))]
    patches, texts, autotexts = plt.pie(data, labels=label_with_num, autopct='%1.1f%%')
    [_.set_fontsize(8) for _ in texts]
    [_.set_fontsize(8) for _ in autotexts]

    plt.axis('equal')
    return save_to_mime_img(filename)


def bug_data_and_label_classified_in_catalog(bug_list, bug_label, bug_catalog):
    bug_data_in_catalog = []
    bug_classified_data_in_catalog = []
    for bug in bug_list.bugs:
        if bug[bug_catalog] is None:
            continue
        bug_data_in_catalog.append(bug[bug_catalog])
    for var in bug_label:
        bug_classified_data_in_catalog.append(bug_data_in_catalog.count(var))
    return bug_classified_data_in_catalog, bug_label

def bug_data_and_label_classified_in_catalog_pro(bug_list, bug_catalog_classify, bug_catalog_team):
    bug_data_in_catalog = {}
    data_return = {}
    bug_label_team = []
    bug_label_classify = []

    for bug in bug_list.bugs:
        #get classify keys 
        if bug[bug_catalog_classify] is None:
            key_class = "Others"
        else : 
            key_class = bug[bug_catalog_classify]
        # get team keys
        if bug[bug_catalog_team] is None:
            key_team = "Others"
        else :
            key_team = bug[bug_catalog_team]

        # # collect key team
        bug_label_team.append(key_team)
        
        
        if key_class not in bug_data_in_catalog:
            bug_data_in_catalog[key_class] = {}

        if key_team not in bug_data_in_catalog[key_class]:
            bug_data_in_catalog[key_class][key_team] = 0
        #increase the number
        bug_data_in_catalog[key_class][key_team] += 1

    #de-duplication 
    bug_label_team = list(set(bug_label_team))

    #format the result
    for key_cl in bug_data_in_catalog:
        if key_cl not in data_return :
            data_return[key_cl] = []

        for key_t in bug_label_team:
            num = 0
            if key_t in bug_data_in_catalog[key_cl]:
                num = bug_data_in_catalog[key_cl][key_t]
            data_return[key_cl].append(num)
            
    return data_return, bug_label_team






