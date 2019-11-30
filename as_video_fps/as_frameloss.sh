#!/bin/bash

TMP_PTS_FILE="pkt_pts_time_tmp.txt"

VIDEO_REAL_FPS=0 #视频文件实际帧率
FPS_DEMANDED=0 #视频文件要求达到的帧率

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
    VIDEO_REAL_FPS=`awk 'BEGIN{printf "%.2f\n",'$first_value'/'$second_value'}'`
}

analysis_frameloss(){
    pc_tmp_video_file_full_path=$1
    #取出参数中的文件的目录,这里不带最后一个斜杠后面需要在补上
    path_of_video_dir=`echo ${pc_tmp_video_file_full_path%/*}`
    path_of_tmp_file=$path_of_video_dir/$TMP_PTS_FILE

    str_result=""
    time1=$(date)
    str_result=`ffprobe  -show_frames -select_streams v $pc_tmp_video_file_full_path  |  grep pkt_pts_time`
    echo "$str_result" >  $path_of_tmp_file
    time2=$(date)

    frame_count=0
    string_final=""
    last_frame=0

    frame_count_demanded_per_0_1s=`expr $FPS_DEMANDED / 10`
    echo "analysis_frameloss-VIDEO_REAL_FPS:FPS_DEMANDED:frame_count_demanded_per_0_1s [$VIDEO_REAL_FPS:$FPS_DEMANDED:$frame_count_demanded_per_0_1s]"
    while read line
    do
        time_str=${line:13}
        tmp_str=`echo ${time_str::-5}` #从字符串尾部删掉5个字符
        let time_str_final=`echo 10#$tmp_str | sed 's/\.\+//g'` #保证10进制打印
        if [ $time_str_final == $last_frame ];then
            let "frame_count++"
        else
            loss_frame_no=`expr $frame_count_demanded_per_0_1s - $frame_count`
            echo "--->$last_frame:$loss_frame_no"
            #开始新的0.1s计数
            last_frame=$time_str_final
            frame_count=1
        fi

        if [ "$string_final" == "" ];then
            string_final="$time_str_final"
        else
            string_final="$string_final;$time_str_final"
        fi
    done <  $path_of_tmp_file

    time3=$(date)
}

figout_fps_demanded(){
    local_fps=$1
    real_int_fps=`echo $local_fps | awk -F '\.' '{print $1}'`
    echo "figout_fps_demanded-local_fps:real_int_fps[$local_fps:$real_int_fps]"
    if [[ $real_int_fps -gt 150 ]];then
        FPS_DEMANDED=240
    elif [[ $real_int_fps -gt 80 ]];then
        FPS_DEMANDED=120
    elif [[ $real_int_fps -gt 40 ]];then
        FPS_DEMANDED=60
    else   
        FPS_DEMANDED=30
    fi
}

file_value="$1"
pc_video_file_path=""
if [ -d $file_value ]; then
    pc_tmp_video_dir="$1"
    device_video_file_full_path="/storage/emulated/0/DCIM/Camera/$2"
    #新视频文件导入到ubuntu电脑中
    adb pull $device_video_file_full_path $pc_tmp_video_dir
    pc_video_file_path=$pc_tmp_video_dir/$2
elif [ -f $file_value ]; then
   pc_video_file_path=$file_value
fi

echo "pc_video_file_path:$pc_video_file_path"

analysis_out_fps_from_single_file $pc_video_file_path
figout_fps_demanded $VIDEO_REAL_FPS
analysis_frameloss $pc_video_file_path


