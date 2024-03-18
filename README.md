# Email-based 2FA for SSH on Linux-Servers
Implementing email-based 2FA for SSH on Linux servers enhances security. Users undergo a two-step verification process via email, bolstering SSH access and safeguarding against unauthorized entry.

## Features 

*   You can set the 2fa function for a specific user group
*   If a user login with 2fa one time on the same day then it won't ask security code again for the same day. 
*   The script will send the security code via SMTP

## Installation

1 - Put main python file to /usr/bin/
    /usr/bin/mailsec2fa.py
2 - Add followinf code in the /etc/ssh/sshd_config file. 2fa is the usergroup in your linux server. 
    Match group 2fa
        ForceCommand /usr/bin/mailsec2fa.py
    
    if you want to create a user group;
        groupadd group_name
    add it on a User
        usermod -aG group_name username
3 - Create a database file for mailsec2fa in /var/log/2fa
    /var/log/2fa/mailsec_access.db

    db file must contain User:UserEmail:UserExpiredate 

    if you want to disable user just remove user group from user. or remove the user from mailsec_access.db file. 
    examples;
    bar:bar@mxxxx.com:20240424   // the user is active and expiration date will end 20240424
    kemal:kemal.yildirim@aaa.com:never // the user is active and expiration date will not end

    code;
    echo -e  "kyi:kemal@xxx.com:never\nbar:foo@xxx.com:20240102" > /var/log/2fa/mailsec_access.db

4 - Create logs and temp files
    echo "" > /var/log/2fa/templogin;
    echo "" > /var/log/2fa/tempseccode;
    echo "" > /var/log/2fa/mailsec.log;

5 - The usergroup should read these files
    /usr/bin/mailsec2fa.py
    /var/log/2fa/templogin
    /var/log/2fa/tempseccode
    /var/log/2fa/mailsec.log


## TO DO

1 - create a script that add user with 2fa user group on Linux server and then add it to mailsec2fa DB file with expiration date.


