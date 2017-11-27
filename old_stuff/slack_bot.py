#!/usr/bin/env python3

from slackclient import SlackClient
from netrc import netrc
import os
import time
import re
import d_list
import subprocess





def get_creds():
    creds = netrc('/root/jtac/.netrc')
    return creds

def retreive_args(search_str, output_dic, mess_key):
  arg_str = re.search(search_str, output_dic[mess_key]).group(1)
  arg_list = [x  for x in arg_str.split(' ') if x]
  if len(arg_list) == 0:
    arg_dic = {'host': None, 'case': None}
    return arg_dic
  #print('#'*30)
  #print(arg_list)
  #print('#'*30)
  for i in arg_list:
    if i in d_list.devices:
      hn = i
    elif re.search(r'.*?([0-9]+-[0-9]+-[0-9]+).*', i):
      sr_num = re.search(r'.*?([0-9]+-[0-9]+-[0-9]+).*', i).group(1)
    else:
      arg_dic = {'host': None, 'case': None}
      return arg_dic
  arg_dic = {'host': hn, 'case': sr_num}
  #print('#'*30)
  #print(arg_dic)
  #print('#'*30)
  return arg_dic


##################################################################################################

def monitor_slack():
    creds = get_creds()

    username, account, password = creds.authenticators('slackbot')
    sc = SlackClient(password)
######   connecting...   ###########################
    if sc.rtm_connect():
      while True:
        output = ['Empty']
        output = sc.rtm_read()
        #print(output)
                  
        mess_key = 'content'
        command_str = r'@netmonkey jtac '
        ch_id_key = 'channel'
        search_str = r'.*?' + command_str + r'(.*)'
        
        # if output has key 'text' ###############        
        if len(output) > 0 and mess_key in output[0]:
         # print('in first if')
          output_dic = output[0]
          # if output has '@netmonkey jtac ...' #############
          if command_str in output_dic[mess_key]:
            channel_id = output_dic[ch_id_key]
            #print('insecond if')
            #print('#'*30)
            #print(output_dic[mess_key])
            #print('#'*30)
            if re.search(search_str, output_dic[mess_key]):
              #print('In 3-rd if')
              sc.api_call("chat.postMessage", channel=channel_id, text='Oh, wait... I think I get that...', as_user=True)
              arg_dic = retreive_args(search_str, output_dic, mess_key)
              if arg_dic['host'] == None or arg_dic['case'] == None:
                sc.api_call("chat.postMessage", channel=channel_id, text='Wrong args... Ignoring...', as_user=True)
                continue
              exec_string = r'./get_data.py ' + arg_dic['host'] + ' ' + arg_dic['case'] + ' ' + '--' + channel_id + r' &'
              
              sc.api_call("chat.postMessage", channel=channel_id, text = 'Running comand: %s' % exec_string, as_user=True)
              #os.system(exec_string)
              #p = subprocess.Popen(exec_string, shell=True, stdout=subprocess.PIPE)
              #(res, stat) = p.communicate()
              #if stat: sc.api_call("chat.postMessage", channel=channel_id, text = 'Got an error, nothing happened', as_user=True)
              #if not stat: print(res)
#sc.api_call("chat.postMessage", channel=channel_id, text = res, as_user=True)


        time.sleep(1)
    else:
      print("Connection faled!")
      os.exit(2)

############   main   ##################


def main():
  monitor_slack()

########################################

if __name__ == "__main__":
  main()

#######################################
