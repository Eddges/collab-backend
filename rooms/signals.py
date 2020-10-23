from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import requests
import time
import json 
from celery import current_app

from rooms.models import RunRequest
from rooms.tasks import save_run_output


@receiver(post_save, sender=RunRequest)
def dispatch_run_task(sender, instance, created, **kwargs):
    if created:
        f = open("/home/shekhar/Lab/Projects/asynamite_back/pair_fork/back/codeinterview-backend/rooms/input.txt", "r")
        fx = open("/home/shekhar/Lab/Projects/asynamite_back/pair_fork/back/codeinterview-backend/rooms/output.txt", "r")
        inp = f.read()
        outp = fx.read()
        # res = current_app.send_task(
        #     'tasks.sandbox.run_user_code',
        #     (instance.language.code, instance.code, instance.stdin),
        #     chain=[
        #         # Without the .set() this request goes to the default queue
        #         # instead of the queue defined in settings. WHY?!
        #         save_run_output.s(instance.id).set(queue='callbacks')
        #     ])
        # instance.celery_task_id = res.task_id
        url = "https://judge0.p.rapidapi.com/submissions"
        #payload = "{ \"language_id\": 50, \"source_code\": \"#include <stdio.h>\\n\\nint main(void) {\\n  char name[10];\\n  scanf(\\\"%s\\\", name);\\n  printf(\\\"hello %s\\\\n\\\", name);\\n  return 0;\\n}\", \"stdin\": \"world\"}"
        jsonData = {
            "language_id" : 70,
            "source_code" : instance.code,
            "stdin" : inp,
            "expected_output" : outp
        }
        
        headers = {
            'x-rapidapi-host': "judge0.p.rapidapi.com",
            'x-rapidapi-key': "ea353caa41mshc63e90bf38f8ff8p17b707jsn8d093a6be47e",
            'content-type': "application/json",
            'accept': "application/json",
        }
        response = requests.request("POST", url, json= jsonData, headers=headers)
        
        x= json.loads(response.text)
        print(x['token'])
        url1 = "https://judge0.p.rapidapi.com/submissions/" + str(x['token'])  
        print(url1)
        headers1 = {
            'x-rapidapi-host': "judge0.p.rapidapi.com",
            'x-rapidapi-key': "ea353caa41mshc63e90bf38f8ff8p17b707jsn8d093a6be47e",
        }
        response1 = requests.request("GET", url1, headers=headers1)
        print(type(response.text))
        print(response1.text)
        y=json.loads(response1.text)
        print(type(y['status']['description']))
        
        result={
            "error" : 0,
            "error_msg" : "",
            # "output": y['status']['description'],
            "output": y['stdout'],
            "exec_time" : y['time']
        }
        
        
        save_run_output(result,instance.id)
        instance.save()
