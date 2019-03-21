import adsk.core
import adsk.fusion
import traceback

from .Fusion360Utilities.Fusion360Utilities import AppObjects, get_default_dir
from .Fusion360Utilities.Fusion360CommandBase import Fusion360CommandBase

import json
from collections import defaultdict

display_state_object = {}


def show_all_occurrences():
    ao = AppObjects()

    for occurrence in ao.root_comp.allOccurrences:
        occurrence.isLightBulbOn = True


def hide_all_bodies():
    ao = AppObjects()

    for component in ao.design.allComponents:
        component.isBodiesFolderLightBulbOn = True
        for body in component.bRepBodies:
            body.isLightBulbOn = False


def revert_last():
    pass


def isolate():
    show_all_occurrences()
    hide_all_bodies()
    revert_last()


def make_component_visible(component):
    ao = AppObjects()
    occurrences = ao.root_comp.allOccurrencesByComponent(component)

    for occurrence in occurrences:
        if not occurrence.isVisible:
            occurrence.isLightBulbOn = True


def make_body_visible(body: adsk.fusion.BRepBody):
    parent_component = body.parentComponent

    was_on = parent_component.isBodiesFolderLightBulbOn

    parent_component.isBodiesFolderLightBulbOn = True

    body.isLightBulbOn = True


def get_body(this_body: adsk.fusion.BRepBody):
    body = {
        "name": this_body.name,
        "body": this_body,
        "light_bulb": this_body.isLightBulbOn,
        "visible": this_body.isVisible

    }
    return body


def get_component(feature):
    component = {
        "name": feature.parentComponent.name,
        "component": feature.parentComponent,
        "bodies": []
    }

    for this_body in feature.bodies:
        component["bodies"].append(get_body(this_body))
        if not this_body.isVisible:
            make_body_visible(this_body)

    make_component_visible(feature.parentComponent)

    return component


def build_display_state_object():
    global display_state_object
    ao = AppObjects()
    root_comp = ao.root_comp

    display_state_object = {
        "components": {}
    }

    if root_comp is not None:

        all_occurrences = ao.root_comp.allOccurrences

        for occurrence in all_occurrences:
            display_state_object[occurrence.fullPathName] = occurrence.isLightBulbOn

        for component in ao.design.allComponents:
            display_state_object["components"][component.name] = component.isBodiesFolderLightBulbOn

            for body in component.bRepBodies:
                display_state_object["components"][component.name + "_" + body.name] = body.isLightBulbOn

    # return display_state_object


def reset_display_state():
    global display_state_object

    ao = AppObjects()
    root_comp = ao.root_comp

    if root_comp is None:
        return False

    all_occurrences = root_comp.allOccurrences

    for occurrence in all_occurrences:
        state = display_state_object.get(occurrence.fullPathName, None)

        if state is not None:
            occurrence.isLightBulbOn = state

    for component in ao.design.allComponents:

        state = display_state_object["components"].get(component.name, None)

        if state is not None:
            component.isBodiesFolderLightBulbOn = state

        for body in component.bRepBodies:

            state = display_state_object["components"].get(component.name + "_" + body.name, None)

            if state is not None:
                body.isLightBulbOn = state


def make_message(result):

    timeline_message = "<b>Feature Information</b><br /><br />"
    timeline_message += "<b>Name: &nbsp;&nbsp; </b>" + result["name"] + "<br />"
    timeline_message += "<b>Type: &nbsp;&nbsp; </b>" + result["type"] + "<br />"

    health_state = result.get("health_state", None)

    if health_state is not None:
        timeline_message += "<b>Health: &nbsp;&nbsp; </b>"
        health = next(name for name, value in vars(adsk.fusion.FeatureHealthStates).items() if value == health_state)

        if health_state == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            health = "Healthy"

        timeline_message += health + "<br />"

    components = result.get("components", [])

    if len(components) > 0:
        timeline_message += "<br /><b>Affected Components: </b>"

        for component in components:
            timeline_message += "<br /><b> &nbsp;&nbsp;&nbsp;&nbsp;" + component["name"] + "</b><br />"

            bodies = component.get("bodies", [])

            if len(bodies) > 0:
                timeline_message += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
                timeline_message += "Affected Bodies:<br />"

                for body in bodies:
                    timeline_message += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; "
                    timeline_message += body["name"] + "<br />"

    warning = result.get("error_message", "")

    if len(warning) > 0:
        timeline_message += "<br /><b>Error or Warning Message: </b><br />"
        timeline_message += warning

    return timeline_message


def play_feature():
    ao = AppObjects()
    timeline = ao.time_line

    if timeline is None:
        return False

    elif timeline.markerPosition == timeline.count:
        return False

    timeline_object = timeline.item(timeline.markerPosition)

    result = {}

    if timeline_object.isGroup:
        timeline_object.isCollapsed = False
        result["type"] = "group"

    else:

        timeline.movetoNextStep()
        feature = adsk.fusion.Feature.cast(timeline_object.entity)

        result["entity"] = timeline_object.entity
        result["index"] = timeline_object.index
        result["suppressed"] = timeline_object.isSuppressed
        result["name"] = timeline_object.name

        if feature is not None:
            isolate()
            result["error_message"] = timeline_object.errorOrWarningMessage
            result["health_state"] = timeline_object.healthState
            result["type"] = "feature"
            result["feature"] = feature
            result["components"] = []
            result["components"].append(get_component(feature))

            if feature.linkedFeatures.count > 0:
                for this_feature in feature.linkedFeatures:
                    result["components"].append(get_component(this_feature))

        else:
            result["type"] = "other"

    return result


def more_features():
    ao = AppObjects()
    timeline = ao.time_line

    if timeline is None:
        return False

    elif timeline.markerPosition == timeline.count:
        return False

    else:
        return True


# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says "pass" for any method you want to use
class PlayerCommand(Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        if reason == adsk.core.CommandTerminationReason.CancelledTerminationReason or \
                reason == adsk.core.CommandTerminationReason.PreEmptedTerminationReason:
            reset_display_state()

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, changed_input,
                         input_values):
        # ao = AppObjects()
        # if changed_input.id == "play_controls_id":
        #     button = changed_input.selectedItem
        #     if button is not None:
        #         if button.name == "play":
        #             if more_features():
        #                 ao.ui.commandDefinitions.itemById("cmdID_PlayerCommand").execute()
                    # button.isSelected = False

        pass

    # Run when the user presses OK
    # This is typically where your main program logic would go
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        ao = AppObjects()
        if more_features():
            ao.ui.commandDefinitions.itemById("cmdID_PlayerCommand").execute()

    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    # The following is a basic sample of a dialog UI
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        result = play_feature()

        if result:
            message = make_message(result)
            command.okButtonText = "Next"
            command.cancelButtonText = "Done"

        else:
            message = "You are already at the end of the timeline.  " \
                      "Rollback to use Player to step through the features in the timeline"

        inputs.addTextBoxCommandInput("message_id", "", message, 20, True)

        # button_row = inputs.addButtonRowCommandInput("play_controls_id", "Controls: ", False)
        # button_row.listItems.add("play", False, "./resources", -1)
        # button_row.listItems.add("stop", False, "./resources", -1)

        # inputs.addTextBoxCommandInput("message_id", "", str(result), 20, True)



class FirstPlayerCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        global display_state_object

        ao = AppObjects()

        build_display_state_object()

        ao.ui.commandDefinitions.itemById("cmdID_PlayerCommand").execute()
