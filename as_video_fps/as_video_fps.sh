#!/bin/bash

#使用方法
#./as_video_fps.sh video_file_name
#or
#./as_video_fps.sh file_dir_name

analysis_out_fps_from_single_file(){
    path_2_file_name=$1
    avg_frame_rate=$(ffprobe -select_streams v -v quiet -print_format json -show_format -show_streams $path_2_file_name |awk -F "[avg_frame_rate]" '/avg_frame_rate/{print$0}')
    str=$(echo $avg_frame_rate | awk -F "[:]" '/avg_frame_rate/{print$2}')
    #echo $str,上一步得到字符串'"39060000/1362709",'
    #去除行头的"号
    str1=$(echo ${str#*\"})
    #接着去除行末"号及之后的,号
    final_str=$(echo ${str1%\"*})
    #分割取出地一个数值
    first_value=`echo $final_str|awk -F "[/]" '{print$1}' `
    #取出第二个数值
    second_value=`echo $final_str|awk -F "[/]" '{print$2}' `
    #echo $first_value
    #echo $second_value
    #保留两位小数输出帧率,四舍五入与windows上保持一致
    awk 'BEGIN{printf "%.2f\n",'$first_value'/'$second_value'}'
}

function analysis_out_fps_from_dir(){
    path_2_dir=$1
    for element in `ls $path_2_dir`
    do
        dir_or_file=$path_2_dir"/"$element
        if [ -d $dir_or_file ]
        then
            analysis_out_fps_from_dir $dir_or_file
        else
            echo ${dir_or_file}
            analysis_out_fps_from_single_file $dir_or_file
        fi
    done
}

file_value="$1"
if [ -d $file_value ]; then
    final_str=$(echo ${file_value%\/*})
    analysis_out_fps_from_dir $final_str
elif [ -f $file_value ]; then
    analysis_out_fps_from_single_file $file_value
fi