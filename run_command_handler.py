from statusbot import command_handler
repsonse = command_handler.call_command('help', None, None)
print(repsonse)