import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

sys.path.insert(0, "")
from nacwrap import *



def test_user_delete():
    pass
    # nacwrap.user_delete(id="auth0|651424b1c67d3f1447d32190")

def test_user_list():
    usr_dict = nacwrap.users_list()
    pprint(usr_dict)

    usr_objs = nacwrap.users_list_pd()
    pprint(usr_objs)


test_user_list()
