#!/usr/bin/env python

import re
import subprocess

def get_output(command):
  tmp=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)    
  return tmp.communicate()[0]


if __name__ == '__main__':
  
  print('###\nThis is landscape.py\n###\n/etc/profile.d/login_2.sh --> /root/jtac/landscape.py\n###\n\n')
  
  cpu_string = get_output("top -b -n 1 | grep 'Cpu(s)'")

  i = 0
  print('CPU:')
  for line in cpu_string.split('\n'):
    cpu_search_string = r'(.*?)(,\s?)(\S+)( id)(.*)'
    if line:
      i+= 1
      if re.search(cpu_search_string, line):    
        idle_Pattern = float(re.search(r'(.*?)(,\s?)(\S+)( id)(.*)', line).group(3))
        cpu_Util = 100.0 - idle_Pattern
        print('CPU{}: {}%\n'.format(i, cpu_Util))
  


    
  mem_string = get_output("free -m | grep Mem")
  
  mem_search_string = r'(.*?)(\d+)(.*?)(\d+)(.*?)(\d+)(.*?)(.*)' 
  if re.search(mem_search_string, mem_string.decode('utf-8')) and mem_string:
   
    mem_Pattern = re.search(mem_search_string, mem_string.decode('utf-8'))
    used_percent = (1.0-float(mem_Pattern.group(6))/float(mem_Pattern.group(2)))*100
    print('Memory (total: {} MB):\nUsed: {:.1f}%\n\n'.format(mem_Pattern.group(2),used_percent))
  



  
  space_string = get_output("df -h /")
  
  disk_search_string = r'(.*)(\n)(\S+)(\s+)(\S+)(\s+)(\S+)(\s+)(\S+)(\s+)(\S+)(.*)' 
  if space_string and re.search(disk_search_string, space_string):
    print space_string 
    space_Pattern = re.search(disk_search_string, space_string)
    print('/ space (total: {}):\nUsed: {}\n'.format(space_Pattern.group(5), space_Pattern.group(11)))


  int_string = get_output("ifconfig | grep inet | grep -v inet6 | grep -v 127.0.0.")
  
  int_search_string = r'(\s+inet\s+)(\S+)(.*)'
    
  if int_string:
    for line in int_string.split('\n'):
      if 'inet' in line and re.search(int_search_string, line).group(2):
        print('IP address: '+ re.search(int_search_string, line).group(2))
  
  os_string = get_output("grep -i release /etc/*release")
  
  if os_string:
    print('\n\n' + os_string.split('\n')[0])

  print('\n####\n')
