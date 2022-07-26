from .flowCommandDialog import entry as flowCommandDialog
# from .paletteShow import entry as paletteShow
# from .paletteSend import entry as paletteSend

# Fusion will automatically call the start() and stop() functions.
commands = [
    flowCommandDialog,
    # paletteShow,
    # paletteSend
]

# The start function will be run when the add-in is started.
def start():
    for command in commands:
        command.start()


# The stop function will be run when the add-in is stopped.
def stop():
    for command in commands:
        command.stop()