#!/usr/bin/env python3

import subprocess
import re

process_string='ps aux | grep -v grep | grep -w /root/jtac/slack_bot.py | awk "{print \$2, \$NF}"'
run_proc_string='/root/jtac/slack_bot.py > /dev/null 2>&1 &'

def get_the_process(process_string):
  p = subprocess.Popen(process_string, shell = True, stdout=subprocess.PIPE)
  proc_b_string = p.communicate()[0]
  proc_string = proc_b_string.decode('UTF8')
  proc_list = proc_string.split('\n')
  if '' in proc_list: proc_list.remove('')
  print(proc_list)
  return proc_list

def check_proc(proc_list, run_proc_string):
  if len(proc_list) == 1:
    print('Only one slack_bot.py process is running, everything is OK')
  if len(proc_list) == 0:
    print('No one slack_bot.py process is running, starting /root/jtac/slack_bot.py')
    p = subprocess.Popen(run_proc_string, shell = True, stdout=subprocess.PIPE)
    p.communicate()[0]
  if len(proc_list) > 1:
    print('More than one slack_bot.py process is running, killing all working process and starting a new /root/jtac/slack_bot.py')
    for line in proc_list:
      pid = line.split()[0]
      if not re.search(r'\d+', line):
        print("Don't see PID, exiting...")
        exit
      kill_string = 'kill -9 {}'.format(pid)
      print(kill_string)
      p1 = subprocess.Popen(kill_string, shell = True, stdout=subprocess.PIPE)
      kill_b_string = p1.communicate()[0]
    p2 = subprocess.Popen(run_proc_string, shell = True, stdout=subprocess.PIPE)
    p2.communicate()[0]

if __name__ == '__main__':
  proc_list = get_the_process(process_string)
  check_proc(proc_list, run_proc_string)
