import base64

def dlhub_test(data):
    import sys, time, os
    sys.path.append("/app")
    os.chdir("/app")
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")
    os.environ["PYTHONWARNINGS"]= "ignore::DeprecationWarning"
    start = time.time()
    global shim
    if 'shim' not in globals():
        import dlhub_shim
        shim = dlhub_shim
    x = shim.run(data)
    end = time.time()
    return (x, (end-start) * 1000)

template = """
from funcx.config import Config
from parsl.providers import LocalProvider
from parsl.providers import KubernetesProvider
from parsl.launchers import MpiRunLauncher, AprunLauncher

config = Config(
    scaling_enabled=True,
    heartbeat_period=10,
    heartbeat_threshold=30,
    worker_debug=True,
    provider=KubernetesProvider(
        image='{image}',
        namespace='dlhub-privileged',
        nodes_per_block=1,
        init_blocks={max_workers_per_node},
        min_blocks={max_workers_per_node},
        max_blocks={max_workers_per_node},
        max_mem='3000Mi',
        init_mem='500Mi',
        worker_init="pip install parsl==0.9.0 mdf_toolbox==0.5.0;export PYTHONPATH=$PYTHONPATH:/app;pip install git+https://github.com/funcx-faas/funcX.git@funcx-kube",
        secret='ryan-kube-secret',
        pod_name="dlhub-funcx-{container_type}",
    ),
    max_workers_per_node=1,
)
"""

images = {'matminer-featurize': '039706667969.dkr.ecr.us-east-1.amazonaws.com/ddb722f9-2b02-44e1-8346-3e7a966b15a5',
          'matminer-util': '039706667969.dkr.ecr.us-east-1.amazonaws.com/50358d8c-be7a-41bf-af76-a460223907fe',
          'cifar10': '039706667969.dkr.ecr.us-east-1.amazonaws.com/a77881c7-8c01-4ecb-9134-5b4eeb202c4f',
          'mnist': '039706667969.dkr.ecr.us-east-1.amazonaws.com/088196a4-14f0-11e9-826c-acde48001122',
          'oqmd': '039706667969.dkr.ecr.us-east-1.amazonaws.com/2d360461-aeec-483e-81db-18f25ec18376',
          'noop': '039706667969.dkr.ecr.us-east-1.amazonaws.com/f0f2bca0-23e3-436e-af9c-50875acbf0c7',
          'inception': '039706667969.dkr.ecr.us-east-1.amazonaws.com/d8f4512d-dfb4-4fda-ae92-a569cd6d8fc2',}

inputs = {
    'noop':
    [1, 2, 3],
    'matminer-featurize':
    [{'composition_object': 'gANjcHltYXRnZW4uY29yZS5jb21wb3NpdGlvbgpDb21wb3NpdGlvbgpxACmBcQF9cQIoWA4AAABh\nbGxvd19uZWdhdGl2ZXEDiVgHAAAAX25hdG9tc3EER0AUAAAAAAAAWAUAAABfZGF0YXEFfXEGKGNw\neW1hdGdlbi5jb3JlLnBlcmlvZGljX3RhYmxlCkVsZW1lbnQKcQdYAgAAAEFscQiFcQlScQpHQAAA\nAAAAAABoB1gBAAAAT3ELhXEMUnENR0AIAAAAAAAAdXViLg==\n'}], 
    'matminer-util': 
    [{'composition': 'Al2O3'}],
    'oqmd':
    [{'features': [8.0, 13.0, 5.0, 10.0, 2.4, 8.0, 73.0, 87.0, 14.0, 81.4, 6.719999999999999, 87.0, 15.9994, 26.9815386, 10.9821386, 20.39225544, 5.271426528000001, 15.9994, 54.8, 933.47, 878.6700000000001, 406.26800000000003, 421.7616, 54.8, 13.0, 16.0, 3.0, 14.8, 1.44, 16.0, 2.0, 3.0, 1.0, 2.4, 0.48, 2.0, 66.0, 121.0, 55.0, 88.0, 26.4, 66.0, 1.61, 3.44, 1.8299999999999998, 2.708, 0.8783999999999998, 3.44, 2.0, 2.0, 0.0, 2.0, 0.0, 2.0, 1.0, 4.0, 3.0, 2.8, 1.44, 4.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 6.0, 3.0, 4.8, 1.44, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 5.0, 3.0, 3.2, 1.44, 2.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 2.0, 5.0, 3.0, 3.2, 1.44, 2.0, 9.105, 16.48, 7.375, 12.055000000000001, 3.5400000000000005, 9.105, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 12.0, 225.0, 213.0, 97.2, 102.24000000000001, 12.0]}],
    'inception':
    base64.b64encode(open('cat.jpg','rb').read()).decode("utf-8"),
    'cifar10':
    base64.b64encode(open('cat.jpg','rb').read()).decode("utf-8")
}
