# SGE Documentation
Collection of tools for using PBS, a job scheduler for high-performance
computing environments on SGE. The command is usually `qsub <options>` on most systems.

## Usage & Examples
The main class under sge is `SGEJob`, which provides functionality to use the
job sceduling system on a high performance computing (HPC) cluster.

The `Qstat` class is also available for parsing the output of the `qstat`
command.

The class currently provides a template, `temp.pbs`, file to be modified and used
when submitting a job as well as default job attributes.

### Using SGEJob with Multiprocess

```python
from OrthoEvol.Tools.sge import SGEJob
```

### Submitting multiple jobs

```python
from OrthoEvol.Tools.sge import SGEJob
```

### Get Job Info

```python
from OrthoEvol.Tools.sge import SGEJob
```

### Running a simple job
```python
from OrthoEvol.Tools.sge import SGEJob

myjob = SGEJob(email_address='shutchins2@umc.edu')

code = "test.py" # A python file with code to be run.
myjob.submit_pycode(code)
```

### Using `SGEPipelineTask`

```python
import logging
import luigi
import os
from OrthoEvol.Tools.sge import SGEPipelineTask

# TIP Works on linux but not Windows
logger = logging.getLogger('luigi-interface')

SGEPipelineTask.shared_tmp_dir = os.getcwd()
SGEPipelineTask.parallel_env = None


class TestPipelineTask(SGEPipelineTask):
    """Example pipeline task."""

    i = luigi.Parameter()

    def work(self):  # Use work instead of run to DEBUG
        logger.info('Running test job...')
        with open(self.output().path, 'w') as f:
            f.write('This is a test job.')
            f.close()

    def output(self):
        return luigi.LocalTarget(path=os.path.join(os.getcwd(), 'testjob_' + str(self.i) + '.txt'))


if __name__ == '__main__':
    tasks = [TestPipelineTask(i=str(i), select=i+1) for i in range(3)]
    luigi.build(tasks, local_scheduler=True, workers=3)
```


## Software Dependencies
Ensure that you have at least pbs version `14.1.0`

## Thanks
Thanks to [@jfeala](https://github.com/jfeala) for his work on Luigi's SGEJobTask.

