from funcx.sdk.client import FuncXClient
import argparse
from funcx.serialize import FuncXSerializer
# from funcx.queues import RedisQueue
from forwarder.queues import RedisQueue
import time
import sqlite3
import subprocess
from utils import dlhub_test, template, inputs
import uuid

parser = argparse.ArgumentParser()
parser.add_argument("-y", "--endpoint_name", type=str,
                    default="dlhub-cooley-batching",
                    help="Endpoint_name")
parser.add_argument("-e", "--endpoint_id", type=str,
                    default="f5b5ff11-706e-4534-9a43-7eb5a1ae5a9e",
                    help="Endpoint_id")
parser.add_argument("-w", "--walltime",
                    type=str, default='00:20:00', help="walltime")
parser.add_argument("-c", "--container_type",
                    type=str, default='noop', help="container_type")
parser.add_argument("-t", "--tasks", type=int, default=1024,
                    help="Number of tasks")
parser.add_argument("-n", "--trials", type=int,
                    default=1, help="number of trials per batch submission")
args = parser.parse_args()


# Initiate the result database
db = sqlite3.connect('data.db')
db.execute("""create table if not exists tasks(
    platform text,
    start float,
    end float,
    completion_time float,
    num_tasks int,
    container_type text,
    failed int)"""
)
print("Database initiated")

# Get the input data
data = inputs[args.container_type]
print("Got the input data")

config = template.format(container_type=args.container_type,
                         walltime=args.walltime)
with open("/home/zzli/.funcx/{}/config.py".format(args.endpoint_name), 'w') as f:
    f.write(config)

# Start the endpoint
endpoint_name = args.endpoint_name
cmd = "funcx-endpoint start {}".format(endpoint_name)
try:
    subprocess.call(cmd, shell=True)
except Exception as e:
    print(e)
print("Started the endpoint {}".format(args.endpoint_id))
print("Wating 60 seconds for the endpoint to start")
time.sleep(60)

fxc = FuncXClient()
func_uuid = fxc.register_function(dlhub_test,
                                  description="A sum function")
print("The functoin uuid is {}".format(func_uuid))


fxs = FuncXSerializer()

def test(tasks=1, data=[1], timeout=float('inf'), endpoint_id=None, function_id=None, poll=0.1):
    
    res = fxc.run(data, endpoint_id=endpoint_id, function_id=function_id) 
    print("Task ID: {}".format(res))
    start = time.time()
    while time.time() - start <= timeout:
        a = fxc.get_task_status(res)
        if 'status' in a:
            continue
        elif 'result' in a:
            res = a['result']
            failed = False
            break
        elif 'exception' in a:
            res = a['exception']
            failed = True
            break
        time.sleep(poll)
    end = time.time()
    result = fxs.deserialize(res)[0]
    result_time = fxs.deserialize(res)[1]
    print("Result : {}".format((result, result_time)))

    if not failed:
        print("Time to complete {} tasks: {:8.3f} s".format(tasks, (end - start)))
        return start, end, result_time, failed
    else:
        return start, end, 0, failed

# Priming the endpoint with tasks
print("\nAll initialization done. Start priming the endpoint")
test(tasks=1, data=[data], endpoint_id=args.endpoint_id, function_id=func_uuid)
print("Finished priming")

for i in range(14):
    num_tasks = 2 ** i
    if num_tasks > args.tasks:
        break
    data = [data for t in range(num_tasks)]
    for j in range(args.trials):
        try:
            start, end, completion_time, failed = test(tasks=num_tasks, data=data, endpoint_id=args.endpoint_id, function_id=func_uuid)
            result_data = ('Cooley', start, end, completion_time, num_tasks, args.container_type, failed)
            print('inserting {}'.format(str(result_data)))
            db.execute("""
                insert into
                tasks (platform, start, end, completion_time, num_tasks, container_type, failed)
                values (?, ?, ?, ?, ?, ?, ?)""", result_data
            )
            db.commit()
        except Exception as e:
            print(e)         


# Stop the endpoint
cmd = "funcx-endpoint stop {}".format(endpoint_name)
try:
    # stop twice to make sure
    subprocess.call(cmd, shell=True)
    subprocess.call(cmd, shell=True)
except Exception as e:
    print(e)
print("\nStopped the endpoint {}".format(args.endpoint_id))
print("Wating 120 seconds for the endpoint to stop")
time.sleep(120)


