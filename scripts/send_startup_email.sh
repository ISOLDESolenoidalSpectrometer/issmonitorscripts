#!/bin/bash -ef
#
# Send an email when the Raspberry Pi is started.
# This is to monitor possible power cuts in the ISOLDE hall.
# 20190219 - Joonas Konki (joonas.konki@cern.ch)
#

TO=liam.gaffney@cern.ch,patrick.macgregor@cern.ch,samuel.reeve@postgrad.manchester.ac.uk
#TO=joonas.konki@cern.ch,liam.gaffney@cern.ch

/usr/sbin/sendmail -i $TO <<MAIL_END
Subject: ISSMONITORPI rebooted
To: $TO

This is an automatic email to let you know that issmonitorpi has just rebooted!
Was it due to a power cut??
MAIL_END
