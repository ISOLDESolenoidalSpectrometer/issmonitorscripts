#!/bin/bash -ef
#
# Send an email alert
# 20190719 - Joonas Konki (joonas.konki@cern.ch)
#
if [ $# -ne 2 ]; then
	exit 1
fi

EMAIL_LIST=$( cat $( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/.email_list )

TO="${EMAIL_LIST}"

/usr/sbin/sendmail -i $TO <<MAIL_END
Subject: ISSMONITORPI alert
To: $TO
This is an automatic alert email from ISSMONITORPI
Device: $1
Status has changed to: $2
MAIL_END
