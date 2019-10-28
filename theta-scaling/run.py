import argparse
from funcx.serialize import FuncXSerializer
# from funcx.queues import RedisQueue
from forwarder.queues import RedisQueue
import time
import sqlite3
import subprocess
from utils import dlhub_test, template, inputs


parser = argparse.ArgumentParser()
parser.add_argument("-r", "--redis_hostname", type=str, default='127.0.0.1',
                    help="Hostname of the Redis server")
parser.add_argument("-e", "--endpoint_id", type=str,
                    default="5dc807eb-da52-4979-8210-1835c7280e76",
                    help="Endpoint_id")
parser.add_argument("-y", "--endpoint_name", type=str,
                    default="dlhub-theta-remote",
                    help="Endpoint_name")
parser.add_argument("-t", "--tasks", type=int, default=1000,
                    help="Number of tasks")
parser.add_argument("-p", "--priming", type=int, default=1000,
                    help="Number of priming tasks")
parser.add_argument("-i", "--num_workers", default=64,
                    type=int, help="maximum workers")
parser.add_argument("-a", "--workers_per_node",
                    type=int, default=64, help="number of workers per node")
parser.add_argument("-w", "--walltime",
                    type=str, default='00:20:00', help="walltime")
parser.add_argument("-c", "--container_type",
                    type=str, default='noop', help="container_type")
parser.add_argument("-n", "--trials", type=int,
                    default=1, help="number of trials per batch submission")
args = parser.parse_args()

# Initiate the result database
db = sqlite3.connect('data.db')
db.execute("""create table if not exists tasks(
    platform text,
    start_submit float,
    end_submit float,
    returned float,
    num_workers int,
    tasks_per_trial int,
    container_type text)"""
)
print("Database initiated")

# Get the input data
data = inputs[args.container_type]
print("Got the input data")

# Change the config
if args.num_workers <= args.workers_per_node:
    nodes = 1
    max_workers_per_node = args.num_workers
else:
    nodes = int(args.num_workers / args.workers_per_node)
    max_workers_per_node = args.workers_per_node

print("Starting an endpoint with {} nodes, {} workers per node, container {}, with walltime {}"
      .format(nodes, max_workers_per_node, args.container_type, args.walltime))

# Create the config for the endpoint
config = template.format(nodes=nodes,
                         max_workers_per_node=max_workers_per_node,
                         container_type=args.container_type,
                         walltime=args.walltime)
with open("/home/zzli/.funcx/dlhub-theta-remote/config.py", 'w') as f:
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
time.sleep(0)

# Connect to the task and result redis queue
endpoint_id = args.endpoint_id
tasks_rq = RedisQueue(f'task_{endpoint_id}', args.redis_hostname)
results_rq = RedisQueue(f'results', args.redis_hostname)
tasks_rq.connect()
results_rq.connect()
print("Redis queue connected")

# Create an instance of funcx serializer and serialize the function
fxs = FuncXSerializer()
ser_code = fxs.serialize(dlhub_test)
fn_code = fxs.pack_buffers([ser_code])
print("Code serialized")

# Make sure there is no previous result left
while True:
    try:
        x = results_rq.get(timeout=1)
    except:
        print("No more results left")
        break

# Define the test function
def test(tasks=5000, data=[1], timeout=None):
    start_submit = time.time()
    for i in range(tasks):
        ser_args = fxs.serialize([i])
        ser_kwargs = fxs.serialize({'data': data})
        input_data = fxs.pack_buffers([ser_args, ser_kwargs])
        payload = fn_code + input_data
        # container_id = "odd" if i%2 else "even"
        container_id = "RAW"
        tasks_rq.put(f"0{i};{container_id}", 'task', payload)
    end_submit = time.time()
    print("Launched {} tasks in {}".format(tasks, end_submit - start_submit))

    for i in range(tasks):
        if timeout:
            res = results_rq.get('result', timeout=timeout)
        else:
            res = results_rq.get('result', timeout=None)

    returned = time.time()
    delta = returned - start_submit
    print("Printing result once for validation")
    print("Result : ", res)
    try:
        print("Result : ", fxs.deserialize(res[1]['result']))
    except:
        print("Result : ", fxs.deserialize(res[1]['exception']))

    print("Time to complete {} tasks: {:8.3f} s".format(tasks, delta))
    print("Throughput : {:8.3f} Tasks/s".format(tasks / delta))
    return start_submit, end_submit, returned

# Priming the endpoint with tasks
print("\nAll initialization done. Start priming the endpoint")
test(tasks=args.priming, data=data)

# Testing -- repeat for `trials` times
print("\nStart testing")
for trial in range(args.trials):
    print("Testing trial {}/{}".format(trial+1, args.trials))
    try:
        start_submit, end_submit, returned = test(tasks=args.tasks, data=data, timeout=300)
        # Recording results to db
        data = ('Theta', start_submit, end_submit, returned,
                args.num_workers, args.tasks, args.container_type)
        print('inserting {}'.format(str(data)))
        db.execute("""
            insert into
            tasks (platform, start_submit, end_submit, returned, num_workers, tasks_per_trial, container_type)
            values (?, ?, ?, ?, ?, ?, ?)""", data
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
print("Wating 180 seconds for the endpoint to stop")
time.sleep(180)

