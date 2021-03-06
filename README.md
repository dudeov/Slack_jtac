# How it works
#get_data.py

There is a script 'get_data.py' that should be followed by inline args such as:
- FW name (must be present in d_list.py)
- JTAC case number
- Slack channel_id

Example:
```
/root/jtac/get_data.py LB3-CFW 2017-1117-25252 --#network-active
```

The order of the args doesn't matter. Only FW name is a mandatory arg. Script will get the IP address of the device from d_list.py, username = cne, password from /root/.cne and will get the logs and RSI and will download them to /root/data_to_upload/<FW name>

If a case number is provided as an arg, the script will try upload collected logs and rsi to the corresponding JTAC case using SFTP.

If Slack channel_id is provided, the script will try upload its execution log to the corresponding slack channel, using netmonkey credentials. Netmonkey password is stored in /root/.netrc

#slack_bot.py

'slack_bot.py' runs in the background listening the particular command across all the Slack channels: '@netmonkey jtac jtac_case_number fw_name'. The order of the args after 'jtac' doesn't matter.
Then 'slack_bot.py' just runs the script 'get_data.py' giving args: jtac_case_number fw_name channel_id, where the channel_id is the Slack channel where the command was given. 'get_data.py' will try to get logs and rsi, upload them to the case and update the corresponding Slack channel with its execution log.

Usually, 'slack_bot.py' runs something like this on the server:
```
/root/jtac/get_data.py LB3-EFW 2017-1121-0901 --G0A2TS325 > /dev/null 2>&1 &
```
Note. 'slack_bot.py' only listens the Slack and kicks the 'get_data.py' with the args. 'get_data.py' updates the Slack channel on it's own in accordance with channel_id provided to it by 'slack_bot.py'.


#server

1) Everything was tested on Centos 7.

Basically, we need to make sure that 'slack_bot.py' always runs, Python3 and the required modules are installed and HDD doesn't get overwhelmed with the data downloaded from the FWs.

Current server credentials:
```
- IP address: 10.124.15.117
- IP address: 10.225.163.222
- Username: root
```

No password login, only with my SSH keys.

2) Create the directory /root/jtac and copy everything to there

3) Create two password files in the /root directory:

```
$ cat /root/.cne
some_password_string
$ cat /root/.netrc
machine slackbot login netmonkey password some_password_string
```

4) Create the directory /root/data_to_upload
All logs and RSI will be stored there.
Copy the script /root/jtac/copy_to_cron/clean.sh to /etc/cron.daily and restart crond. The script deletes all the files from /root/data_to_upload older than 2 days.

5) Install Python3 and all modules importing in the scripts:
```
/root/jtac/get_data.py
/root/jtac/landscape.py
/root/jtac/slack_bot.py
/root/jtac/copy_to_cron/check_if_listening.py
```

6) Copy /root/jtac/copy_to_usr_lib_systemd_system/slack_bot.service /usr/lib/systemd/system/
This file creates the slack_bot service starting slock_bot.py script. Now make it run upon system boot:
```
$ systemctl enable slack_bot
$ systemctl start slack_bot
```

7) Copy from /root/jtac/copy_to_cron:
- check_if_listening.py to /etc/cron.hourly - this script checks if slack_bot.py is running and restarts it if not
- clean.sh to /etc/cron.daily - this script deletes all the files from /root/data_to_upload older than 2 days.

8) This is not mandatory, but highly desired. Copy /root/jtac/copy_to_etc_profile.d/login_2.sh to /etc/profile.d/
login_2.sh calls another script 'landscape.py' which gives very useful system info each time the user logs in. 
