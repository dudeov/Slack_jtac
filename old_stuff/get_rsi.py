#!/usr/bin/env python3
import pexpect
import getpass
import os
import time
import d_list
import sys
import re
#######################################     get_sysargv()      #################################

def get_sysargv():

  UN = 'cne'
  PW = getpass.getpass("Password for %s: "% UN)
  if len(sys.argv)<2:
    print('Please, specify at least one FWs hostname as an argument. Example: ./get_logs.py LB3-CFW')
    sys.exit(1)
  elif len(sys.argv) == 2 and sys.argv[1] in d_list.devices:
    device_cred = {'device_hn': sys.argv[1], 'device_ip': d_list.devices[sys.argv[1]], 'device_un': UN, 'device_pw': PW, 'case_num': None}
    print('#'*30)
    print('Case number was not provided, files will be dumped locally')
    print('Working with %s, %s' % (sys.argv[1], d_list.devices[sys.argv[1]] ))
  elif len(sys.argv) == 3:
    for i in sys.argv[1:]:
      if i in d_list.devices:
        hn = i
      elif re.search(r'[0-9]+-[0-9]+-[0-9]+', i):
        sr_num = i
      else:
        print('Cannot recognize args. Example: ./get_logs.py LB3-CFW 2017-1117-25252')
        sys.exit(1)
    device_cred = {'device_hn': hn, 'device_ip': d_list.devices[hn], 'device_un': UN, 'device_pw': PW, 'case_num': sr_num}
    print('#'*30)
    print('Case number is {}, files will be uploaded automatically'.format(sr_num))
    print('Working with %s, %s' % (hn, d_list.devices[hn]))
  else:
    print('No match, specify at least a correct FWs hostname as an argument. Example: ./get_logs.py LB3-CFW')
    sys.exit(1)
  return device_cred

##################################################################################################


###################################  which one is Primary??? #####################################

def determine_prim(prompt):
  if re.search(r'{primary:node([0-1])}', str(prompt)):
    node_num = re.search(r'{primary:node([0-1])}', str(prompt)).group(1)
  else:
    print("don't see the prompts, exiting")
    sys.exit(1)
  if node_num == '0':
    prim_node = 'node0'
    sec_node = 'node1'
  elif node_num == '1':
    prim_node = 'node1'
    sec_node = 'node0'
  else:
    print("don't recoznize the node num, exiting")
    sys.exit(1)
  print("Primary node is {}".format(prim_node))
  print('#'*30)

  return prim_node, sec_node

#################################################################################################





##############   clean unicode string from /r/n/r and crap like that        ######################

def clean_unicode(uni_str):
  str_tmp = re.sub(r'\\r\\n\\r', '\n', uni_str)
  str_pretty = re.sub(r'\\r', '\n', str_tmp)
  return str_pretty

#################################################################################################


#########################################        tgz_logs         ################################
######  leaves 2 archived files on the box and returns their names for further scp-ing ###########

def tgz_logs(device_cred):
  print('#'*30)
  time_str = time.strftime('%Y-%m-%d_%H-%M', time.localtime())  

  child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' + device_cred['device_un'] + '@' + device_cred['device_ip'])
  try:  
    child.expect('Password:')
    child.sendline(device_cred['device_pw'])
    user_at_host_string = device_cred['device_un'] + '@' + device_cred['device_hn']
    child.expect(user_at_host_string)

    prim_node, sec_node = determine_prim(child.before)
    
    fn_sec = device_cred['device_hn'] + '_var_log_' + sec_node + '_' + time_str + '.tgz'
    fn_prim = device_cred['device_hn'] + '_var_log_' + prim_node + '_' + time_str + '.tgz'
    any_node = 'node*'
    fn_scp = device_cred['device_hn'] + '_var_log_' + any_node  + '_' + time_str + '.tgz'
    child.sendline('file archive compress source /var/log/ destination /var/tmp/' + fn_prim)
    child.expect(user_at_host_string)
    child.sendline('start shell')
    child.expect('%')

######### in case if Secondary is dead #########
    try:  
      child.sendline('rlogin -T ' + sec_node)
      child.expect('secondary', timeout = 5)
      child.sendline('file archive compress source /var/log/ destination /var/tmp/' + fn_sec)
      child.expect('secondary')
      child.sendline('file copy /var/tmp/' + fn_sec + ' ' + prim_node + ':/var/tmp/')
      child.expect('secondary')
      return fn_prim, fn_sec, fn_scp
    except:
      print('########\nException was raised\nSecondary is unavailable!\n###########')
      return fn_prim, fn_prim, fn_scp
###############################################
  except Exception as var:
    print(var)
    print('Exception was raised!')
    sys.exit(1)

################################################################################################



########################    get_logs! ########################################################
####### scp-s files left by previous function to the box   ####################################

def get_logs(fn_prim, fn_sec, fn_scp, device_cred):
  dird = device_cred['device_hn']
####  creating directory #####
  if not os.path.exists(dird):
    os.mkdir(dird)
#############################
  dest_path = device_cred['device_un'] + '@' + device_cred['device_ip'] + r':/var/tmp/'
  scp_str = 'scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' + dest_path +  fn_scp + r' ./' + dird
  print(scp_str)
  print('#'*30)
  child = pexpect.spawn(scp_str)
  try:
    child.expect('Password:')
    child.sendline(device_cred['device_pw'])
    child.expect([pexpect.TIMEOUT, pexpect.EOF], timeout = 900)
    download_str =clean_unicode(str(child.before)[2:-1])
    print(download_str)
    if fn_prim != fn_sec: ls_str = 'ls -l ' + dird + ' | grep "' + fn_prim + r'\|' + fn_sec + '"'
    else: ls_str = 'ls -l ' + dird + ' | grep ' + fn_prim
    print('#'*30)
    print(ls_str)
    print('#'*30)
    os.system(ls_str)
  except Exception as var:
    print(var)
    print('Exception was raised!')
    sys.exit(1)
  
##################################################################################################



###############################   upload to the casemanager    ###################################

def upload(dev_cred, fn_prim, fn_sec):
  print('#'*30)
  print('Connecting to JTAC server')
  print('#'*30)
  child = pexpect.spawn('sftp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no anonymous@sftp.juniper.net')
  try:
    child.expect('assword:')
    child.sendline('anonymous')
    child.expect('sftp>')
    print('Got in!!')
    child.sendline('mkdir pub/incoming/' + dev_cred['case_num'])
    child.expect('sftp>', timeout = 900)
    child.sendline('cd pub/incoming/' + dev_cred['case_num'])
    child.expect('sftp>', timeout = 900)
    child.sendline('put ' + dev_cred['device_hn'] + '/' + fn_prim)
    child.expect('sftp>', timeout = 900)
    download_str_1 = clean_unicode(str(child.before)[2:-1])
    if fn_prim != fn_sec:
      child.sendline('put ' + dev_cred['device_hn'] + '/' + fn_sec)
      child.expect('sftp>', timeout = 900)
      download_str_2 = clean_unicode(str(child.before)[2:-1])
    else: download_str_2 = ''
    if 'Permission denied' in download_str_1 or 'Permission denied' in download_str_2:
      print('###########\n\n\n\n\nSomething went wrong! Files were not copied \n\n\n########')
      sys.exit(1)
    else: 
      print(download_str_1)
      print(download_str_2)
  except Exception as var:
    print('###########\n\n\n\n\nSomething went wrong! Files were not copied \n\n\n########')
    print(var)
################################################################################################

######################################      get RSI   #########################################
def get_rsi(device_cred):
  print('#'*30)
  time_str = time.strftime('%Y-%m-%d_%H-%M', time.localtime())

  child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' + device_cred['device_un'] + '@' + device_cred['device_ip'])
  try:
    child.expect('Password:')
    child.sendline(device_cred['device_pw'])
    user_at_host_string = device_cred['device_un'] + '@' + device_cred['device_hn']
    child.expect(user_at_host_string)

    prim_node, sec_node = determine_prim(child.before)

    rsi_name = device_cred['device_hn'] + '_RSI_' + prim_node + '_' + time_str + '.txt'
    print("Now waiting for RSI to complete... Up to 90 min")
    print('#'*30)
    child.sendline('request support information | save /var/tmp/' + rsi_name)
    try:
      child.expect('lines of output to', timeout = 5400)
      print('RSI completed: /var/tmp/%s' % rsi_name)
      print('#'*30)
      return rsi_name, rsi_name, rsi_name
    except pexpect.TIMEOUT:
      print('###########\n\n\n\n\nIt takes too long! Timeout received. Will be uploading what I have... \n\n\n########')
      return rsi_name, rsi_name, rsi_name
    except Exception as var:
      print('###########\n\n\n\n\nSomething went wrong! Files were not copied \n\n\n########')
      print(var)
      sys.exit(1)
  except Exception as var:
    print('###########\n\n\n\n\nSomething went wrong! Files were not copied \n\n\n########')
    print(var)
    sys.exit(1)


###############################    main   ######################################################
def fetch_logs(device_cred):
  fn_prim, fn_sec, fn_scp = tgz_logs(device_cred)
  get_logs(fn_prim, fn_sec, fn_scp, device_cred)

  if device_cred['case_num'] != None:
    upload(device_cred, fn_prim, fn_sec)
#######################

def fetch_rsi(device_cred):
  fn_prim, fn_sec, fn_scp = get_rsi(device_cred) 
  get_logs(fn_prim, fn_sec, fn_scp, device_cred)
  
  if device_cred['case_num'] != None:
    upload(device_cred, fn_prim, fn_sec)
#################################################################################################

##################   main   #####################################################################

def main():
  device_cred = get_sysargv()
  #fetch_logs(device_cred)
  fetch_rsi(device_cred)
#################################################################################################


if __name__ == '__main__':
  main()
