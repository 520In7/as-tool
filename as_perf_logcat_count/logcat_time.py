# -*- coding: utf-8 -*-
# !/usr/bin/python
import re
import sys
import xlwt
import os

'''
python logcat_time.py config_file logcat_file
'''

config_file = sys.argv[1]
logcat_file = sys.argv[2]

turns_time = 0
turn_compelete_flag = 0

def get_filePath_fileName_fileExt(filename):
    (filepath, tempfilename) = os.path.split(filename);
    (shotname, extension) = os.path.splitext(tempfilename);
    return filepath, shotname, extension

#时间字串模板09:52:24.761
def time_str_distance(old_time_str, new_time_str):
    rst1 = map(int, re.split(':|\.', old_time_str))
    rst2 = map(int, re.split(':|\.', new_time_str))
    distance = (rst2[0] * 60 * 60 * 1000 + rst2[1] * 60 * 1000 + rst2[2] * 1000 + rst2[3]) - (
            rst1[0] * 60 * 60 * 1000 + rst1[1] * 60 * 1000 + rst1[2] * 1000 + rst1[3])
    return distance

def read_tag_pair_config(file_path):
    f = open(file_path)
    pair_count = 0
    pair_list = []
    for line in f:
        line = line.strip()
        config_list = line.split('@')
        pair_list.append(config_list)
        pair_count = pair_count + 1
    return pair_list,pair_count

def caculate_tag_distance(str1, str2):
    f = open(logcat_file)
    finish_time = ''
    start_time = ''
    turn_times = 0
    for line in f:
        turn_compelete_flag = False
        if str1 in line:
            turn_compelete_flag = False
            start_time = line.split()[1]
        if str2 in line:
            turn_compelete_flag = True
            finish_time = line.split()[1]
        if turn_compelete_flag:
            turn_times = turn_times + 1
            str_distance = time_str_distance(start_time, finish_time)
            print str_distance

def generate_excel(plist_time_pair,pair_count):
    result_sheet = xlwt.Workbook(encoding='utf-8')
    sheet = result_sheet.add_sheet('result')
    # 生成表头
    i = 0
    for pair in tag_pair_list:
        sheet.write(0, i, pair[0])
        i = i + 1
    sheet.write(0, i, "总时间")
    # 生成数据
    j = 1
    c = 0
    for time_pair in plist_time_pair:
        print "----------------------------"
        m = 0
        #print time_pair, c
        for tag_time_pair in time_pair:
            time_distance = time_str_distance(tag_time_pair[0], tag_time_pair[1])
            sheet.write(j, m, time_distance)
            m = m + 1
            print "---->",time_distance
        start_time_point = time_pair[0][0]
        finish_time_point = time_pair[pair_count - 1][1]
        all_time = time_str_distance(start_time_point, finish_time_point)
        sheet.write(j, m, all_time)
        c = c + 1
        j = j + 1
    (file_p, file_s, file_e) = get_filePath_fileName_fileExt(logcat_file)
    result_sheet.save(file_s + '_out.xls')
    print ("Finished save output to excel!")


(tag_pair_list,pair_count) = read_tag_pair_config(config_file)
time_stamp = [[0 for _ in range(2)] for _ in range(pair_count)]

f = open(logcat_file)
list_time_pair = []
for line in f:
    i = 0
    if line == '\n':
        continue
    for pair in tag_pair_list:
        if pair[1].strip() in line:
            time_stamp[i][0] = line.split()[1]
        if pair[2].strip() in line:
            time_stamp[i][1] = line.split()[1]
        if i == pair_count - 1:
            compeled_flag = False
            for tm_st in time_stamp:
                if tm_st[0] == 0 or tm_st[1] == 0:
                    compeled_flag = False
                    break
                else:
                    compeled_flag = True
            if compeled_flag:
                list_time_pair.append(time_stamp)
                all_time = time_str_distance(time_stamp[0][0], time_stamp[pair_count - 1][1])
                #print "all time:", all_time
                time_stamp = [[0 for _ in range(2)] for _ in range(pair_count)] # 二位数组置空
        i = i + 1
print '=================='

generate_excel(list_time_pair,pair_count)