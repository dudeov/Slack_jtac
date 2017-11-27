Files get_log.py and get_rsi.py are almost identical, but call different functions at the very end.

Usage: ./get_log.py hostname_from_file_d_list.py case_number

Hostname is mandatory, case_number is optional - files will be stored locally. Order of arguments doesn't matter.

Directory with name = hostname will be created on the local machine.

Example:

```

[root@UC1T3NJUNIPER01 jtac]# ./get_rsi.py LB3-EFW 2017-1102-0888
##############################
Case number is 2017-1102-0888, files will be uploaded automatically
Working with LB3-EFW, 10.225.32.117
##############################
Primary node is node0
##############################
Now waiting for RSI to complete... Up to 1 hour
##############################
RSI completed: /var/tmp/LB3-EFW_RSI_node0_2017-11-19_23-14.txt
##############################
scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no cne@10.225.32.117:/var/tmp/LB3-EFW_RSI_node0_2017-11-19_23-14.txt ./LB3-EFW
##############################

LB3-EFW_RSI_node0_2017-11-19_23-14.txt          0%    0     0.0KB/s   --:-- ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt          4%  448KB 448.0KB/s   00:19 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         11% 1120KB 470.4KB/s   00:17 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         19% 1792KB 490.5KB/s   00:15 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         26% 2528KB 515.1KB/s   00:13 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         34% 3264KB 537.2KB/s   00:11 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         42% 3968KB 553.8KB/s   00:09 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         50% 4704KB 572.1KB/s   00:08 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         57% 5440KB 588.4KB/s   00:06 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         66% 6208KB 606.4KB/s   00:05 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         73% 6912KB 616.2KB/s   00:04 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         81% 7648KB 628.1KB/s   00:02 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         89% 8384KB 638.9KB/s   00:01 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt         96% 9088KB 645.4KB/s   00:00 ETA
LB3-EFW_RSI_node0_2017-11-19_23-14.txt        100% 9383KB 702.4KB/s   00:13
\n
##############################
ls -l LB3-EFW | grep LB3-EFW_RSI_node0_2017-11-19_23-14.txt
##############################
-rw-r--r-- 1 root root 9607864 Nov 19 23:18 LB3-EFW_RSI_node0_2017-11-19_23-14.txt
##############################
Connecting to JTAC server
##############################
Got in!!
 put /root/jtac/LB3-EFW/LB3-EFW_RSI_node0_2017-11-19_23-14.txt
\nUploading /root/jtac/LB3-EFW/LB3-EFW_RSI_node0_2017-11-19_23-14.txt to /pub/incoming/2017-1102-0888/LB3-EFW_RSI_node0_2017-11-19_23-14.txt
/root/jtac/LB3-EFW/LB3-EFW_RSI_node0_2017-11-   0%    0     0.0KB/s   --:-- ETA
/root/jtac/LB3-EFW/LB3-EFW_RSI_node0_2017-11- 100% 9383KB  26.9MB/s   00:00
\n

[root@UC1T3NJUNIPER01 jtac]#

```

