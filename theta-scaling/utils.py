import base64

def dlhub_test(i, data=[1, 2, 3]):
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
from parsl.providers import CobaltProvider
from parsl.launchers import MpiRunLauncher, AprunLauncher

config = Config(
    scaling_enabled=True,
    heartbeat_period=30,
    heartbeat_threshold=120,
    provider=CobaltProvider(
        queue='debug-flat-quad',
        # queue='analysis',
        account='CSC249ADCD01',  # project name to submit the job
        # account='APSDataAnalysis',
        launcher=AprunLauncher(overrides="-d 64"),
        worker_init='source activate dlhub-JPDC-theta',
        nodes_per_block={nodes},
        init_blocks=1,
        min_blocks=1,
        max_blocks=1,
        cmd_timeout=300,
        walltime='{walltime}',
    ),
    worker_mode="singularity",
    container_image='/projects/CSC249ADCD01/JPDC/dlhub-{container_type}.simg',
    max_workers_per_node={max_workers_per_node},
)
"""

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
