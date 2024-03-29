#!/usr/bin/env python3
# coding: utf-8

# This file is part of Adblock Plus <https://adblockplus.org/>,
# Copyright (C) 2006-2015 Eyeo GmbH
#
# Adblock Plus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Adblock Plus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Adblock Plus.  If not, see <http://www.gnu.org/licenses/>.

#############################################################################
# This is a reference script to add checksums to downloadable               #
# subscriptions. The checksum will be validated by Adblock Plus on download #
# and checksum mismatches (broken downloads) will be rejected.              #
#                                                                           #
# To add a checksum to a subscription file, run the script like this:       #
#                                                                           #
#   python addChecksum.py < subscription.txt > subscriptionSigned.txt       #
#                                                                           #
# Note: your subscription file should be saved in UTF-8 encoding, otherwise #
# the operation will fail.                                                  #
#                                                                           #
#############################################################################

import sys, re, io, hashlib, base64, pytz
from datetime import datetime

checksumRegexp = re.compile(r'^\s*!\s*checksum[\s\-:]+([\w\+\/=]+).*\n', re.I | re.M)
versionRegexp = re.compile(r'^\s*!\s*version[\s\-:]+(\d+).*\n', re.I | re.M)
modifiedRegexp = re.compile(r'^\s*!\s*last\smodified[\s\-:]+([\w: ]+).*\n', re.I | re.M)

def addChecksum(data):
  data = updateDates(data)
  checksum = calculateChecksum(data)
  data = re.sub(checksumRegexp, '', data)
  data = re.sub(r'(\r?\n)', r'\1! Checksum: %s\1' % checksum, data, 1)
  return data

def updateDates(data):
  now = datetime.now(pytz.utc)
  ver = now.strftime('%Y%m%d%H%M')
  modified = now.strftime('%d %b %Y %H:%M %Z')
  data = re.sub(versionRegexp, '! Version: %s\n' % ver, data, 1)
  data = re.sub(modifiedRegexp, '! Last modified: %s\n' % modified, data, 1)
  return data

def calculateChecksum(data):
  md5 = hashlib.md5()
  md5.update(normalize(data).encode('utf-8'))
  return base64.b64encode(md5.digest()).decode('utf-8').rstrip('=')

def normalize(data):
  data = re.sub(r'\r', '', data)
  data = re.sub(r'\n+', '\n', data)
  data = re.sub(checksumRegexp, '', data)
  return data

def readStream(stream):
  reader = io.TextIOWrapper(stream.buffer, encoding='utf-8')
  try:
    return reader.read()
  except Exception as e:
    raise Exception('Failed reading data, most likely not encoded as UTF-8:\n%s' % e)

if __name__ == '__main__':
  if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

  data = addChecksum(readStream(sys.stdin))
  sys.stdout.write(data)

