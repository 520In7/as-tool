# -*- coding: utf-8 -*-
# !/usr/bin/python
import re
import os
import os.path
import time
import gzip
import sys

'''
2019.1.9
How to use it?
as_tomba.py tombstone_file_path symbol_file_path
example:
python  ~/as_tomba.py    ~/ne_log_crash.txt     ~/Documents/f3b/symbol/out/target/product/pyxis/symbols/out file :
'''
tombstone_file_path = sys.argv[1]
symbols_dir_path = sys.argv[2]

def get_filePath_fileName_fileExt(filename):
    (filepath,tempfilename) = os.path.split(filename);
    (shotname,extension) = os.path.splitext(tempfilename);
    return filepath,shotname,extension

def get_process_pid_name(filename):
    f = open(filename)
    for line in f:
        pattern = re.compile(r"pid:\s([0-9]+?),.+>>> (.+?) <<<")
        rst = pattern.search(line)
        if rst :
            pid = rst.group(1)
            name = rst.group(2).lstrip('/').replace('/','#')
            return pid,name
    return "null","null"

def tomba_dir(ptombstone_file_dir,psymbols_dir_path):
    for file_name in os.listdir(tombstone_file_path):
        target_file = os.path.join(tombstone_file_path,file_name)
        tomba_file(target_file,symbols_dir_path)

def tomba_file(ptombstone_file_path,psymbols_dir_path):
    psymbols_dir_path = psymbols_dir_path.rstrip('/')
    (pid,pname) = get_process_pid_name(ptombstone_file_path)
    f = open(ptombstone_file_path);
    (file_p,file_s,file_e) = get_filePath_fileName_fileExt(ptombstone_file_path)
    out_file_name = file_s+"_"+pid+"_"+pname+".out"
    fp = open(file_p+'/'+out_file_name,'a+')
    fp.truncate()
    for line in f:
        line = line.lstrip()
        line = line.strip('\n')
        if  line.startswith("stack:"):
            break
        else:
            # pattern = re.compile('(#[0-9]{2})(?#调用栈帧数)\s+pc\s+([0-9a-z]{16})(?#pc地址)\s(.+?)\s')
            # 64位和32位机器的pc地址长度不同,64位为16位PC地址，32位为8位PC地址
            pattern = re.compile('(#[0-9]{2})(?#调用栈帧数)\s+pc\s+([0-9a-z]*)(?#pc地址)\s(.+?)\s')
            rst = pattern.search(line)
            if rst:
                symbol_path = psymbols_dir_path + rst.group(3).strip()
                shift_code = rst.group(2)
                analysis_result = tomba_so(symbol_path,shift_code)
                print "result:\n"+analysis_result
                fp.write(line)
                fp.write(analysis_result)
                fp.write('\n')
                f.flush()

def tomba_so(symbol_so_path,shift_code):
    if(os.path.exists(symbol_so_path)):
        cmd_line = "addr2line -i -Cfe %s %s" %(symbol_so_path,shift_code)
        f = os.popen(cmd_line)
        result = f.read()
        return result
    else:
        return "no symbol file!!!"

is_file = 0
if os.path.isdir(tombstone_file_path):
    is_file = 1
elif os.path.isfile(tombstone_file_path):
    is_file = 2
else:
    print("Wrong Tombstone File Name！")
    sys.exit()

if is_file == 1:
    print(tombstone_file_path + " is a dir")
    tomba_dir(tombstone_file_path,symbols_dir_path)
elif is_file == 2:
    print(tombstone_file_path + " is a file")
    tomba_file(tombstone_file_path,symbols_dir_path)
else:
    print("Wrong Tombstone File Name！")
