#!/bin/bash -ef
#
# Send an email when the Raspberry Pi is started.
# This is to monitor possible power cuts in the ISOLDE hall.
# 20190219 - Joonas Konki (joonas.konki@cern.ch)
#

EMAIL_LIST=$( cat $( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/.email_list )

TO="${EMAIL_LIST}"

/usr/sbin/sendmail -i $TO <<MAIL_END
Subject: ISSMONITORPI rebooted
To: $TO

This is an automatic email to let you know that issmonitorpi has just rebooted!
Was it due to a power cut??
MAIL_END
