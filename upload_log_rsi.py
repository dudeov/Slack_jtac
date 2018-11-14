#!/usr/bin/env python3
import pexpect
import getpass
import os
import time
import d_list
import sys
import re
import subprocess
from slacker import Slacker
from netrc import netrc

#######################################     get_sysargv()      #################################

def get_sysargv():
  log = []
  tmp_30 = '#'*30
  UN = 'cne'
  #PW = getpass.getpass("Password for %s: "% UN)
  with open('%s/.cne' % os.path.expanduser('~'), 'rU') as fd: PW = fd.read()
  if len(sys.argv)<2:
    tmp_str = 'Please, specify at least one FWs hostname as an argument. Example: ./get_data.py LB3-CFW'
    print(tmp_str)
    sys.exit(1)

  elif len(sys.argv) == 2 and sys.argv[1] in d_list.devices:
    hn = sys.argv[1]
    device_cred = {'device_hn': hn, 'device_ip': d_list.devices[hn], 'device_un': UN, 'device_pw': PW, 'case_num': None, 'slack_ch': None}
    sr_num = '--ABSENT--'
   
    log.append(tmp_30)
    tmp_str_1 = 'Case number was not provided, files will be dumped locally'
    log.append(tmp_str_1)
    tmp_str_2 = 'Working with %s, %s' % (sys.argv[1], d_list.devices[sys.argv[1]] )
    log.append(tmp_str_2)
    return device_cred, log

  elif len(sys.argv) == 3:
    for i in sys.argv[1:]:
      if i in d_list.devices:
        hn = i
      elif re.search(r'[0-9]+-[0-9]+-[0-9]+', i):
        sr_num = i
      else:
        tmp_str = 'Cannot recognize args. Example: ./get_data.py LB3-CFW 2017-1117-25252'
        print(tmp_str)
        sys.exit(1)
    device_cred = {'device_hn': hn, 'device_ip': d_list.devices[hn], 'device_un': UN, 'device_pw': PW, 'case_num': sr_num, 'slack_ch': None}

  elif len(sys.argv) == 4:
    for i in sys.argv[1:]:
      if i in d_list.devices:
        hn = i
      elif re.search(r'[0-9]+-[0-9]+-[0-9]+', i):
        sr_num = i
      elif re.search(r'--', i):
        sl_str = re.search(r'--(.*)', i).group(1)
        sl_ch = sl_str
      else:
        tmp_str = 'Cannot recognize args. Example: ./get_data.py LB3-CFW 2017-1117-25252 --#network-active'
        print(tmp_str)
        sys.exit(1)
    device_cred = {'device_hn': hn, 'device_ip': d_list.devices[hn], 'device_un': UN, 'device_pw': PW, 'case_num': sr_num, 'slack_ch': sl_ch}

  else:
    tmp_str = 'No match, specify at least a correct FWs hostname as an argument. Example: ./get_data.py LB3-CFW'
    print(tmp_str)
    sys.exit(1)
  

  tmp_str_4 = 'Case number is {}, files will be uploaded automatically'.format(sr_num)
  tmp_str_5 = 'Working with %s, %s' % (hn, d_list.devices[hn])
  log.append(tmp_30)
  log.append(tmp_str_4)
  log.append(tmp_str_5)
  return device_cred, log

##################################################################################################


###################################  which one is Primary??? #####################################

def determine_prim(prompt, log_file):
  if re.search(r'{primary:node([0-1])}', str(prompt)):
    node_num = re.search(r'{primary:node([0-1])}', str(prompt)).group(1)
  else:
    with open(log_file, 'a') as fd: fd.write("\ndon't see the prompts, exiting")
    sys.exit(1)
  if node_num == '0':
    prim_node = 'node0'
    sec_node = 'node1'
  elif node_num == '1':
    prim_node = 'node1'
    sec_node = 'node0'
  else:
    with open(log_file, 'a') as fd: fd.write("\ndon't recoznize the node num, exiting")
    sys.exit(1)
  with open(log_file, 'a') as fd: fd.write("\nPrimary node is {}".format(prim_node))
  with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
  with open(log_file, 'rU') as fd: print(fd.read())
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

def tgz_logs(device_cred, time_str, log_file):
  with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
  with open(log_file, 'a') as fd: fd.write('\n' + 'Working on getting logs\n')
  with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
  child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' + device_cred['device_un'] + '@' + device_cred['device_ip'])
  try:  
    child.expect('Password:')
    child.sendline(device_cred['device_pw'])
    user_at_host_string = device_cred['device_un'] + '@' + device_cred['device_hn']
    child.expect(user_at_host_string)

    prim_node, sec_node = determine_prim(child.before, log_file)
    
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
      child.close()
      return fn_prim, fn_sec, fn_scp
    except:
      with open(log_file, 'a') as fd: fd.write('\n########\nException was raised\nSecondary is unavailable!\n###########')
      child.close()
      with open(log_file, 'rU') as fd: print(fd.read())
      return fn_prim, fn_prim, fn_scp
###############################################
  except Exception as var:
    with open(log_file, 'a') as fd: fd.write('\n' + str(var))
    with open(log_file, 'a') as fd: fd.write('\nException was raised!')
    sys.exit(1)

################################################################################################



########################    get_logs! ########################################################
####### scp-s files left by previous function to the box   ####################################

def get_logs(fn_prim, fn_sec, fn_scp, device_cred, log_file):
  dird = '/root/data_to_upload/' + device_cred['device_hn']
####  creating directory #####
  if not os.path.exists(dird):
    os.mkdir(dird)
#############################
  dest_path = device_cred['device_un'] + '@' + device_cred['device_ip'] + r':/var/tmp/'
  scp_str = 'scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' + dest_path +  fn_scp + r' ' + dird
  with open(log_file, 'a') as fd: fd.write('\n' + scp_str)
  with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
  child = pexpect.spawn(scp_str)
  try:
    child.expect('Password:')
    child.sendline(device_cred['device_pw'])
    child.expect([pexpect.TIMEOUT, pexpect.EOF], timeout = 1200)
    download_str =clean_unicode(str(child.before)[2:-1])
    child.close()
    with open(log_file, 'a') as fd: fd.write('\n' + download_str)
    if fn_prim != fn_sec: ls_str = 'ls -l ' + dird + ' | grep "' + fn_prim + r'\|' + fn_sec + '"'
    else: ls_str = 'ls -l ' + dird + ' | grep ' + fn_prim
    with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
    with open(log_file, 'a') as fd: fd.write('\n' + ls_str)
    with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
    #os.system(ls_str)
    ls = subprocess.Popen(ls_str, stdout=subprocess.PIPE, shell=True)
    byte_output = ls.communicate()[0]
    str_output = byte_output.decode('ASCII')
    with open(log_file, 'a') as fd: fd.write('\n' + str_output)
    with open(log_file, 'rU') as fd: print(fd.read())
  except Exception as var:
    with open(log_file, 'a') as fd: fd.write('\n' + str(var))
    with open(log_file, 'a') as fd: fd.write('\n' + 'Exception was raised!')
    sys.exit(1)
  
##################################################################################################



###############################   upload to the casemanager    ###################################

def upload(dev_cred, fn_prim, fn_sec, log_file):
  dird = '/root/data_to_upload/' + dev_cred['device_hn']
  with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
  with open(log_file, 'a') as fd: fd.write('\n' + 'Connecting to JTAC server')
  with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
  child = pexpect.spawn('sftp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no anonymous@sftp.juniper.net')
  try:
    child.expect('assword:')
    child.sendline('anonymous')
    child.expect('sftp>')
    with open(log_file, 'a') as fd: fd.write('\n' + 'Got in!!')
    child.sendline('mkdir pub/incoming/' + dev_cred['case_num'])
    child.expect('sftp>', timeout = 900)
    child.sendline('cd pub/incoming/' + dev_cred['case_num'])
    child.expect('sftp>', timeout = 900)
    child.sendline('put ' + dird + '/' + fn_prim)
    child.expect('sftp>', timeout = 1200)
    download_str_1 = clean_unicode(str(child.before)[2:-1])
    if fn_prim != fn_sec:
      child.sendline('put ' + dird + '/' + fn_sec)
      child.expect('sftp>', timeout = 1200)
      download_str_2 = clean_unicode(str(child.before)[2:-1])
      child.close()
    else: 
      download_str_2 = ''
      child.close()
    if 'Permission denied' in download_str_1 or 'Permission denied' in download_str_2:
      with open(log_file, 'a') as fd: fd.write('\n' + '###########\n\n\n\n\nSomething went wrong! Files were not copied \n\n\n########')
      sys.exit(1)
    else: 
      with open(log_file, 'a') as fd: fd.write('\n' + download_str_1)
      with open(log_file, 'a') as fd: fd.write('\n' + download_str_2)
    with open(log_file, 'rU') as fd: print(fd.read())
  except Exception as var:
    with open(log_file, 'a') as fd: fd.write('\n' + '###########\n\n\n\n\nSomething went wrong! Files were not copied \n\n\n########')
    with open(log_file, 'a') as fd: fd.write('\n' + str(var))
################################################################################################

######################################      get RSI   #########################################
def get_rsi(device_cred, time_str, log_file):
  with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
  with open(log_file, 'a') as fd: fd.write('\n' + 'Working on getting RSI, be patient :-)\n')
  with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
  child = pexpect.spawn('ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' + device_cred['device_un'] + '@' + device_cred['device_ip'])
  try:
    child.expect('Password:')
    child.sendline(device_cred['device_pw'])
    user_at_host_string = device_cred['device_un'] + '@' + device_cred['device_hn']
    child.expect(user_at_host_string)

    prim_node, sec_node = determine_prim(child.before, log_file)

    rsi_name = device_cred['device_hn'] + '_RSI_' + prim_node + '_' + time_str + '.txt'
    rsi_name_arch = device_cred['device_hn'] + '_RSI_' + prim_node + '_' + time_str + '.tgz'
    with open(log_file, 'a') as fd: fd.write('\n' + "Now waiting for RSI to complete... Up to 90 min")
    with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
    child.sendline('request support information | save /var/tmp/' + rsi_name)
    try:
      child.expect('lines of output to', timeout = 5400)
      with open(log_file, 'a') as fd: fd.write('\n' + 'RSI completed: /var/tmp/%s' % rsi_name)
      with open(log_file, 'a') as fd: fd.write('\n' + '#'*30)
      child.close()
      with open(log_file, 'rU') as fd: print(fd.read())
      return rsi_name, rsi_name, rsi_name
    except pexpect.TIMEOUT:
      with open(log_file, 'a') as fd: fd.write('\n' + '###########\n\n\n\n\nIt takes too long! Timeout received. Will be uploading what I have... \n\n\n########')
      return rsi_name, rsi_name, rsi_name
    except Exception as var:
      with open(log_file, 'a') as fd: fd.write('\n' + '###########\n\n\n\n\nSomething went wrong! Files were not copied \n\n\n########')
      with open(log_file, 'a') as fd: fd.write('\n' + str(var))
      sys.exit(1)
  except Exception as var:
    with open(log_file, 'a') as fd: fd.write('\n' + '###########\n\n\n\n\nSomething went wrong! Files were not copied \n\n\n########')
    with open(log_file, 'a') as fd: fd.write('\n' + str(var))
    sys.exit(1)


###############################    main   ######################################################
def fetch_logs(device_cred, time_str, log_file):
  fn_prim, fn_sec, fn_scp = tgz_logs(device_cred, time_str, log_file)
  get_logs(fn_prim, fn_sec, fn_scp, device_cred, log_file)

  if device_cred['case_num'] != None:
    upload(device_cred, fn_prim, fn_sec, log_file)
#######################

def fetch_rsi(device_cred, time_str, log_file):
  fn_prim, fn_sec, fn_scp = get_rsi(device_cred, time_str, log_file) 
  get_logs(fn_prim, fn_sec, fn_scp, device_cred, log_file)
  
  if device_cred['case_num'] != None:
    upload(device_cred, fn_prim, fn_sec, log_file)
#################################################################################################


def get_creds():
  creds = netrc('%s/.netrc' % os.path.expanduser('~'))
  return creds

def send_slack(message, channel_id, log_file):
  creds = get_creds()
  username, account, password = creds.authenticators('slackbot')
  #slack = Slacker(password)
  #response = slack.chat.post_message(as_user = True, text=message, channel = channel_id)
  curl_str = 'curl -F file=@%s -F token=%s -F channels=%s https://slack.com/api/files.upload' % (log_file, password, channel_id)
  print(curl_str)
  os.system(curl_str)


##################   main   #####################################################################

def main():

  time_str = time.strftime('%Y-%m-%d_%H-%M', time.localtime())
    
  device_cred, log = get_sysargv()
  
  dird = '/root/data_to_upload/' + device_cred['device_hn']
####  creating directory #####
  if not os.path.exists(dird):
    os.mkdir(dird)
#############################
  log_file = dird + '/' + device_cred['device_hn']+ '_execution-log_' + time_str + '.log'
  print('Execution log:  %s' % log_file)
  try: os.remove(log_file)
  except: pass
  log_string = '\n'.join(log)
  with open(log_file, 'a') as fd: fd.write(log_string)
  print(log_string)
  fetch_logs(device_cred, time_str, log_file)
  fetch_rsi(device_cred, time_str, log_file)
  
  with open(log_file, 'rU') as fd: log_message = fd.read()
  
  print(log_message)
  

  if device_cred['slack_ch'] != None:
    channel_id = device_cred['slack_ch']
    send_slack(log_message, channel_id, log_file)

#################################################################################################


if __name__ == '__main__':
  main()
