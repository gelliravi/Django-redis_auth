# Copyright 2012 Mark Vismonte
# Author: Mark Vismonte
# Date: 4/16/2012
from calendar import timegm
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sessions.models import Session
from django.dispatch import receiver

# Import redis
import redis
redisClient = redis.Redis(settings.REDIS_HOST)

# Register userLoggedIn signal
@receiver(user_logged_in)
def userLoggedIn(sender, **kwargs):
  user = kwargs['user']
  session = kwargs['request'].session
  sessionKey = session.session_key
  print "%s(%s) logged in" % (user, sessionKey)

  # Create new session variable
  try:
    session = Session.objects.get(session_key=sessionKey)
  except:
    return False

  # Add session to redis
  storeDict = {
    'uid': int(user.id),
    'username': str(user.username),
    'fullname': str(user.get_full_name()),
  }

  expireTime = timegm(session.expire_date.timetuple())
  redisStoreKey = "auth:%s" % sessionKey  
  return (redisClient.hmset(redisStoreKey, storeDict)) and (
      redisClient.expireat(redisStoreKey, expireTime))
 
# Register userLoggedOut signal
@receiver(user_logged_out)
def userLoggedOut(sender, **kwargs):
  session = kwargs['request'].session
  user = kwargs['user']
  print "%s(%s) logged out" % (user, session.session_key)

  # Find the key and then remove it if it's there.
  redisStoreKey = "auth:%s" % session.session_key
  redisClient.delete(redisStoreKey)
