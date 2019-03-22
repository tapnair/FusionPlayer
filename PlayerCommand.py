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


def hide_all_occurrences():
    ao = AppObjects()

    for occurrence in ao.root_comp.allOccurrences:
        occurrence.isLightBulbOn = True


def show_occurrence(occurrence: adsk.fusion.Occurrence):
    occurrence.isLightBulbOn = True
    for body in occurrence.bRepBodies:
        make_body_visible(body)


def hide_all_bodies():
    ao = AppObjects()

    for component in ao.design.allComponents:
        component.isBodiesFolderLightBulbOn = True
        for body in component.bRepBodies:
            body.isLightBulbOn = False


def show_sketch(sketch):
    sketch.areDimensionsShown = True
    sketch.areConstraintsShown = True
    sketch.areProfilesShown = True
    sketch.isLightBulbOn = True


def show_construction(entity):
    entity.component.isConstructionFolderLightBulbOn = True
    entity.component.isOriginFolderLightBulbOn = True
    entity.isLightBulbOn = True


def show_joint(joint: adsk.fusion.Joint):
    joint.parentComponent.isJointsFolderLightBulbOn = True
    joint.isLightBulbOn = True


def hide_all_construction():
    ao = AppObjects()
    for component in ao.design.allComponents:
        for item in get_all_construction(component):
            item.isLightBulbOn = False


def hide_all_joints():
    ao = AppObjects()
    for component in ao.design.allComponents:
        for item in component.joints:
            if item.timelineObject.index < ao.time_line.markerPosition:
                item.isLightBulbOn = False


def get_all_construction(component: adsk.fusion.Component):

    construction_entities = []

    for plane in component.constructionPlanes:
        construction_entities.append(plane)
    for axis in component.constructionAxes:
        construction_entities.append(axis)
    for point in component.constructionPoints:
        construction_entities.append(point)

    construction_entities.append(component.xConstructionAxis)
    construction_entities.append(component.yConstructionAxis)
    construction_entities.append(component.zConstructionAxis)
    construction_entities.append(component.xYConstructionPlane)
    construction_entities.append(component.xZConstructionPlane)
    construction_entities.append(component.yZConstructionPlane)
    construction_entities.append(component.originConstructionPoint)

    return construction_entities


def hide_all_sketches():
    ao = AppObjects()
    for component in ao.design.allComponents:
        for sketch in component.sketches:
            sketch.isLightBulbOn = False


def isolate():
    show_all_occurrences()
    hide_all_bodies()
    hide_all_sketches()
    hide_all_construction()
    hide_all_joints()


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
        "components": {},
        "sketches": {},
        "bodies": {},
        "construction": {},
        "origin": {},
        "joints": {}
    }

    if root_comp is not None:

        all_occurrences = ao.root_comp.allOccurrences

        for occurrence in all_occurrences:
            display_state_object[occurrence.fullPathName] = occurrence.isLightBulbOn

        for component in ao.design.allComponents:
            display_state_object["components"][component.name] = component.isBodiesFolderLightBulbOn
            display_state_object["sketches"][component.name] = component.isSketchFolderLightBulbOn
            display_state_object["construction"][component.name] = component.isConstructionFolderLightBulbOn
            display_state_object["origin"][component.name] = component.isOriginFolderLightBulbOn
            display_state_object["joints"][component.name] = component.isJointsFolderLightBulbOn

            for sketch in component.sketches:
                display_state_object["sketches"][component.name + "_" + sketch.name] = sketch.isLightBulbOn

            for body in component.bRepBodies:
                display_state_object["bodies"][component.name + "_" + body.name] = body.isLightBulbOn

            for entity in get_all_construction(component):
                display_state_object["construction"][component.name + "_" + entity.name] = entity.isLightBulbOn

            for joint in component.joints:
                display_state_object["joints"][component.name + "_" + joint.name] = joint.isLightBulbOn

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

        body_folder_state = display_state_object["components"].get(component.name, None)
        if body_folder_state is not None:
            component.isBodiesFolderLightBulbOn = body_folder_state

        sketch_folder_state = display_state_object["sketches"].get(component.name, None)
        if sketch_folder_state is not None:
            component.isSketchFolderLightBulbOn = sketch_folder_state

        construction_folder_state = display_state_object["construction"].get(component.name, None)
        if construction_folder_state is not None:
            component.isConstructionFolderLightBulbOn = construction_folder_state

        origin_folder_state = display_state_object["origin"].get(component.name, None)
        if origin_folder_state is not None:
            component.isOriginFolderLightBulbOn = origin_folder_state

        joint_folder_state = display_state_object["joints"].get(component.name, None)
        if joint_folder_state is not None:
            component.isJointsFolderLightBulbOn = joint_folder_state

        for body in component.bRepBodies:
            body_state = display_state_object["bodies"].get(component.name + "_" + body.name, None)
            if body_state is not None:
                body.isLightBulbOn = body_state

        for sketch in component.sketches:
            sketch_state = display_state_object["sketches"].get(component.name + "_" + sketch.name, None)
            if sketch_state is not None:
                sketch.isLightBulbOn = sketch_state

        for entity in get_all_construction(component):
            construction_state = display_state_object["construction"].get(component.name + "_" + entity.name, None)
            if construction_state is not None:
                entity.isLightBulbOn = construction_state

        for joint in component.joints:
            joint_state = display_state_object["joints"].get(component.name + "_" + joint.name, None)
            if joint_state is not None:
                joint.isLightBulbOn = joint_state


def make_message(result):
    timeline_message = "<b>Feature Information</b><br />"
    timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Name: &nbsp;&nbsp; </b>" + result["name"] + "<br />"
    timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Type: &nbsp;&nbsp; &nbsp;</b>" + result["type"] + "<br />"

    health_state = result.get("health_state", None)

    if health_state is not None:
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Health: &nbsp; </b>"
        health = next(name for name, value in vars(adsk.fusion.FeatureHealthStates).items() if value == health_state)

        if health_state == adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
            health = "Healthy"

        timeline_message += health + "<br />"

    if result.get("type", "") == "Sketch":
        timeline_message += "<br /><b>Sketch Information</b><br />"
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Fully Constrained: &nbsp;&nbsp; </b>"
        timeline_message += str(result["fully_constrained"]) + "<br />"
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Parent Component: &nbsp;&nbsp; </b>"
        timeline_message += result["parent_component"] + "<br />"
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Sketch Plane: &nbsp;&nbsp; </b>"
        timeline_message += result["plane"] + "<br />"
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Plane Type: &nbsp;&nbsp; </b>"
        timeline_message += result["plane_type"] + "<br />"

    elif result.get("type", "") == "Make Component":
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Component: &nbsp;&nbsp; </b>"
        timeline_message += result["parent_component"] + "<br />"

    elif result.get("type", "") == "Construction Geometry":
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Parent Component: &nbsp;&nbsp; </b>"
        timeline_message += result["parent_component"] + "<br />"
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Type: &nbsp;&nbsp; </b>"
        timeline_message += result["construction_type"] + "<br />"

    elif result.get("type", "") == "Joint":
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Parent Component: &nbsp;&nbsp; </b>"
        timeline_message += result["parent_component"] + "<br />"
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Reference 1: &nbsp;&nbsp; </b>"
        timeline_message += result["part_1_name"] + "<br />"
        timeline_message += "<b>&nbsp;&nbsp;&nbsp;&nbsp; Reference 2: &nbsp;&nbsp; </b>"
        timeline_message += result["part_2_name"] + "<br />"

    elif result.get("type", "") == "Feature":
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

        result["entity"] = timeline_object.entity
        result["index"] = timeline_object.index
        result["suppressed"] = timeline_object.isSuppressed
        result["name"] = timeline_object.name

        feature = adsk.fusion.Feature.cast(timeline_object.entity)
        sketch = adsk.fusion.Sketch.cast(timeline_object.entity)
        occurrence = adsk.fusion.Occurrence.cast(timeline_object.entity)
        plane = adsk.fusion.ConstructionPlane.cast(timeline_object.entity)
        axis = adsk.fusion.ConstructionAxis.cast(timeline_object.entity)
        point = adsk.fusion.ConstructionPoint.cast(timeline_object.entity)
        joint = adsk.fusion.Joint.cast(timeline_object.entity)

        if plane is not None:
            construction_entity = plane
            construction_type = "Plane"
        elif axis is not None:
            construction_entity = axis
            construction_type = "Axis"
        elif point is not None:
            construction_entity = point
            construction_type = "Point"
        else:
            construction_entity = None
            construction_type = ""

        if feature is not None:
            isolate()
            result["error_message"] = timeline_object.errorOrWarningMessage
            result["health_state"] = timeline_object.healthState
            result["type"] = "Feature"
            result["feature"] = feature
            result["components"] = []
            result["components"].append(get_component(feature))

            if feature.linkedFeatures.count > 0:
                for this_feature in feature.linkedFeatures:
                    result["components"].append(get_component(this_feature))

        elif sketch is not None:
            isolate()
            show_sketch(sketch)
            make_component_visible(sketch.parentComponent)

            result["error_message"] = sketch.errorOrWarningMessage
            result["health_state"] = sketch.healthState
            result["type"] = "Sketch"
            result["sketch"] = sketch
            result["fully_constrained"] = sketch.isFullyConstrained
            result["parent_component"] = sketch.parentComponent.name
            reference_plane = sketch.referencePlane

            face = adsk.fusion.BRepFace.cast(reference_plane)
            plane = adsk.fusion.ConstructionPlane.cast(reference_plane)

            if face is not None:
                result["plane"] = "Face ID: " + str(face.tempId)
                result["plane_type"] = "Planar Face"
                result["plane_entity"] = face
                make_body_visible(face.body)

            elif plane is not None:
                result["plane"] = plane.name
                result["plane_type"] = "Construction Plane"
                result["plane_entity"] = plane

            else:
                result["plane"] = "Unknown Sketch Plane"
                result["plane_type"] = "unknown"
                result["plane_entity"] = reference_plane

        elif occurrence is not None:
            isolate()
            show_occurrence(occurrence)
            result["type"] = "Make Component"
            result["occurrence"] = occurrence
            result["parent_component"] = occurrence.component.name

        elif construction_entity is not None:
            isolate()
            show_construction(construction_entity)
            make_component_visible(construction_entity.component)

            result["error_message"] = construction_entity.errorOrWarningMessage
            result["health_state"] = construction_entity.healthState
            result["type"] = "Construction Geometry"
            result["construction_type"] = construction_type
            result["construction_entity"] = construction_entity
            result["parent_component"] = construction_entity.component.name

        elif joint is not None:
            isolate()
            show_joint(joint)
            show_occurrence(joint.occurrenceOne)
            show_occurrence(joint.occurrenceTwo)

            result["error_message"] = joint.errorOrWarningMessage
            result["health_state"] = joint.healthState
            result["type"] = "Joint"
            result["joint"] = joint
            result["part_1"] = joint.occurrenceOne
            result["part2"] = joint.occurrenceTwo
            result["part_1_name"] = joint.occurrenceOne.name
            result["part_2_name"] = joint.occurrenceTwo.name
            result["parent_component"] = joint.parentComponent.name

        else:
            result["type"] = timeline_object.entity.objectType

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
        else:
            reset_display_state()

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


class PlayFromHereCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        global display_state_object

        ao = AppObjects()

        build_display_state_object()

        ao.ui.commandDefinitions.itemById("cmdID_PlayerCommand").execute()


class PlayFromStartCommand(Fusion360CommandBase):

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        global display_state_object

        ao = AppObjects()

        build_display_state_object()

        ao.time_line.moveToBeginning()

        ao.ui.commandDefinitions.itemById("cmdID_PlayerCommand").execute()