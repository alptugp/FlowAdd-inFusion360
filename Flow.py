from . import commands
from .lib import fusion360utils as futil

def run(context):
    try:
        # Runs the start function in each of the commands as defined in commands/__init__.py
        commands.start()

    except:
        futil.handle_error('run')


def stop(context):
    try:
        # Removes all of the created event handlers 
        futil.clear_handlers()

        # Runs the start function in each of the commands as defined in commands/__init__.py
        commands.stop()

    except:
        futil.handle_error('stop')