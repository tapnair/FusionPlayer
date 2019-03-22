# Importing sample Fusion Command
# Could import multiple Command definitions here
from .Demo1Command import Demo1Command
from .PlayerCommand import PlayerCommand, PlayFromHereCommand, PlayFromStartCommand
from .DemoPaletteCommand import DemoPaletteShowCommand, DemoPaletteSendCommand

commands = []
command_definitions = []

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Play From Begining',
    'cmd_description': 'Detailed View Playback',
    'cmd_id': 'cmdID_PlayFromHereCommand',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'Player',
    'command_promoted': False,
    'class': PlayFromStartCommand
}
command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Play From Here',
    'cmd_description': 'Detailed View Playback',
    'cmd_id': 'cmdID_PlayFromStartCommand',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'Player',
    'command_promoted': True,
    'class': PlayFromHereCommand
}
command_definitions.append(cmd)

# Define parameters for 1st command
cmd = {
    'cmd_name': 'Play Timeline Step',
    'cmd_description': 'Detailed View Playback',
    'cmd_id': 'cmdID_PlayerCommand',
    'cmd_resources': './resources',
    'workspace': 'FusionSolidEnvironment',
    'toolbar_panel_id': 'Player',
    'command_promoted': False,
    'command_visible': False,
    'class': PlayerCommand
}
command_definitions.append(cmd)

# # Define parameters for 2nd command
# cmd = {
#     'cmd_name': 'Fusion Palette Demo Command',
#     'cmd_description': 'Fusion Demo Palette Description',
#     'cmd_id': 'cmdID_palette_demo_1',
#     'cmd_resources': './resources',
#     'workspace': 'FusionSolidEnvironment',
#     'toolbar_panel_id': 'SolidScriptsAddinsPanel',
#     'command_visible': True,
#     'command_promoted': False,
#     'palette_id': 'demo_palette_id',
#     'palette_name': 'Demo Palette Name',
#     'palette_html_file_url': 'demo.html',
#     'palette_is_visible': True,
#     'palette_show_close_button': True,
#     'palette_is_resizable': True,
#     'palette_width': 500,
#     'palette_height': 600,
#     'class': DemoPaletteShowCommand
# }
# command_definitions.append(cmd)
#
# # Define parameters for 2nd command
# cmd = {
#     'cmd_name': 'Fusion Palette Send Command',
#     'cmd_description': 'Send info to Fusion 360 Palette',
#     'cmd_id': 'cmdID_palette_send_demo_1',
#     'cmd_resources': './resources',
#     'workspace': 'FusionSolidEnvironment',
#     'toolbar_panel_id': 'SolidScriptsAddinsPanel',
#     'command_visible': True,
#     'command_promoted': False,
#     'palette_id': 'demo_palette_id',
#     'class': DemoPaletteSendCommand
# }
# command_definitions.append(cmd)

# Set to True to display various useful messages when debugging your app
debug = False


# Don't change anything below here:
for cmd_def in command_definitions:
    command = cmd_def['class'](cmd_def, debug)
    commands.append(command)


def run(context):

    for run_command in commands:
        run_command.on_run()


def stop(context):
    for stop_command in commands:
        stop_command.on_stop()
