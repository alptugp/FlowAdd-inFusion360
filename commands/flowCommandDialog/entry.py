from re import T
import adsk.core
import os
from ...lib import fusion360utils as futil
from ... import config
import traceback
import os

app = adsk.core.Application.get()
ui = app.userInterface

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_flowCmdDialog'
CMD_NAME = 'Sync'
CMD_Description = 'Sync the values with Flow'

# Specifies that the command will be promoted to the panel.
IS_PROMOTED = True

# Defines the location where the command button will be created.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

# Executed when add-in is run.
def start():
    # Creates the command definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Defines an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Adds a button into the UI so the user can run the command. ********
    # Gets the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Gets the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Creates the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specifies if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Deletes the button command control
    if command_control:
        command_control.deleteMe()

    # Deletes the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    cmd = args.command
    cmd.setDialogInitialSize(400, 400)

    # set_up = inputs.addBoolValueInput('set_up', 'Set Up', True, '', False)
    # pull = inputs.addBoolValueInput('pull', 'Pull', True, '', False)
    # push = inputs.addBoolValueInput('push', 'Push', True, '', False)                                                                                      

    # Creates radio button group input for setting up, pulling and pushing the changed values.
    radioButtonGroup = inputs.addRadioButtonGroupCommandInput('syncOptions', 'Sync Options')
    radioButtonItems = radioButtonGroup.listItems
    set_up = radioButtonItems.add("Set Up", False)
    pull = radioButtonItems.add("Pull", False)
    push = radioButtonItems.add("Push", False)
    
    # Connects the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)

# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # Gets a reference to the command's inputs.
    inputs = args.command.commandInputs
    # text_box: adsk.core.TextBoxCommandInput = inputs.itemById('text_box')
    # value_input: adsk.core.ValueCommandInput = inputs.itemById('value_input')

    if inputs.itemById('syncOptions').listItems[0].isSelected == True:
        ui.messageBox('Set Up')
    elif inputs.itemById('syncOptions').listItems[1].isSelected == True:
        run(adsk.core, "pull")
    elif inputs.itemById('syncOptions').listItems[2].isSelected == True:
        run(adsk.core, "push")

# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs


# This event handler is called when the user changes anything in the command dialog which
# allows modifying the values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows verifying that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verifies the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        inputs.areInputsValid = True
    else:
        inputs.areInputsValid = False
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []


















from dbm.ndbm import library
from http import client
import os
import sys
from tokenize import Double
from unicodedata import category

# Add vendor directory to module search path
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')

sys.path.append(vendor_dir)

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import requests
import json
import adsk.core, adsk.fusion, adsk.cam, traceback
import re

def run(context, operation):
    ui = None
    try:
        app: adsk.core.Application = adsk.core.Application.get()
        ui: adsk.core.UserInterface = app.userInterface

        # What to open
        target_project_name = app.data.activeProject.name

        # exits when there is no design opened in Fusion and the user pulls 
        if str(app.activeProduct.rootComponent.name) == "(Unsaved)":
            sys.exit("Please open a design in Fusion")

        target_design_name = removeVersionSuffix(app.activeProduct.rootComponent.name)
        
        # Open this design in fusion to get access to much deeper parts of the API
        open_docs_by_name(app, ui, target_project_name, target_design_name)
        
        # Set fusion objects from file (rather than just data objects)
        design: adsk.fusion.Design = app.activeProduct
        if not design:
            ui.messageBox("No active Fusion 360 design", "No Design")

        if operation == "pull":
            # fetches values from Flow and updates the parameters in Fusion
            fetchDatafromFlow(ui, design)
            ui.messageBox("Parameters pulled from Flow successfully")
        elif operation == "push":
            # pushes values to Flow
            pushValuesToFlow(ui, design)
            ui.messageBox("Parameters pushed to Flow successfully")
              
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



def open_docs_by_name(app: adsk.core.Application, ui: adsk.core.UserInterface, target_project_name: str, target_design_name: str):
    # Get all available data
    all_data: adsk.core.Data = app.data
    all_projects: list = all_data.dataProjects.asArray()
    
    # Get project
    for project in all_projects:
        if project.name == target_project_name:
            target_project: adsk.core.DataProject = project

    if not target_project:
        ui.messageBox(f"Project Not Found: {target_project_name}")
    
    files_in_project: list = target_project.rootFolder.dataFiles.asArray()
    
    # Get file
    for file in files_in_project:
        if file.name == target_design_name:
            target_file: adsk.core.DataFile = file
            app.documents.open(target_file)
        
    if not target_file:
        ui.messageBox(f"Design Not Found: {target_design_name}")


def fetchDatafromFlow(ui, design: adsk.fusion.Design):
    # Opening JSON file and authenticating the account
    with open('/Users/alptug/Desktop/cred/Autodesk-x-flow-intergration/credentials.json') as json_file:
        Data = json.load(json_file)
        username = Data["username"]
        password = Data["password"]

    # authenticating 
    url = "https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_iODQDOUFS"

    payload = {
        "ClientId": "4bmi0kl02b8312nt2qnacdkubn",
        "AuthFlow": "USER_PASSWORD_AUTH",
        "AuthParameters": {
            "USERNAME": username,
            "PASSWORD": password
        }
    }

    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # uses token to authenticate the account
    Dict = json.loads(response.text)
    token = Dict["AuthenticationResult"]["IdToken"]

    # transport with a defined url endpoint
    transport = AIOHTTPTransport(
        url = "https://api.flowengineering.com/v1/graphql",
        headers = {
            "Authorization": f'Bearer {token}'
        },
    )

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    projectId = getProjectId(client)

    categoryId = getCategoryId(client, projectId)

    datasQueryResult = getDatasQueryResult(client, categoryId)

    paramInModel = design.userParameters

    dataIdToExpressionDict = {}
    for x in datasQueryResult["data"]:
        # 
        if x["value"] == {} and paramInModel.itemByName(convertToFusionName(x["name"])) is not None:
            dataIdToExpressionDict[x["data_id"]] = "0 mm"
        else:
            # extract the expression from the query and adjust the expression if there is no space between the value and the unit
            data = adjustExpression(x["value"].strip())
            # put the expression into dataIdToExpression dictionary
            dataIdToExpressionDict[x["data_id"]] = data


    dataFusionNameToIdDict = {}
    for i in range(paramInModel.count):
       dataFusionNameToIdDict[paramInModel.item(i).name] = findMatchingDataId(paramInModel.item(i).name, datasQueryResult)
    
    difference = subtractLists(dataIdToExpressionDict.keys(), dataFusionNameToIdDict.values())

    # if difference is not empty, there are parameters in Flow which have no corresponding parameters in Fusion, and thus they must be created in Fusion
    for x in difference: 
        if x is not None:
            if dataIdToExpressionDict[x] != {}:
                # third arguement of the following function is the comment for the new parameter, and an empty string is passed for it in this case
                paramInModel.add(convertToFusionName(getParameterName(x, datasQueryResult["data"])),
                                 adsk.core.ValueInput.createByString(dataIdToExpressionDict[x]), 
                                 getParameterUnit(dataIdToExpressionDict[x]), 
                                 "")
            # the parameter has no assigned value in Flow and thus assign it to 0 mm in Fusion
            else:
                ui.messageBox("The parameter named " + getParameterName(x, datasQueryResult["data"]) + " was not assigned to a value in Flow and thus it is now assigned to 0 mm in Fusion")
                # dataIdToValueDict[x] = "0 mm"
                # dataNameToIdDict[convertToFusionName(getParameterName(x, datasQueryResult["data"]))] = x
                paramInModel.add(convertToFusionName(getParameterName(x, datasQueryResult["data"])),
                                 adsk.core.ValueInput.createByString("0 mm"), 
                                 "mm", 
                                 "")
        
    # transfer flow values to fusion names and put it into Valuesdict
    dataFusionNameToExpressionDict = {}

    for (name, dataId) in dataFusionNameToIdDict.items():
        dataFusionNameToExpressionDict[name] = findMatchingValue(dataId, dataIdToExpressionDict)
            
    for parameterName, parameterValue in dataFusionNameToExpressionDict.items():
        # ui.messageBox(str(parameterName) + ": " + str(parameterValue))
        # if parameterValue == {}: 
          #  paramInModel.itemByName(parameterName).expression = adsk.core.ValueInput.createByString("0 mm")
        if parameterValue is not None:
            if getParameterUnit(paramInModel.itemByName(parameterName).expression) == getParameterUnit(parameterValue):
                paramInModel.itemByName(parameterName).expression = parameterValue
            # if the unit of the parameter in Flow is different than that in Fusion, notify the user about unmatching units
            else:
                ui.messageBox("Unit of the parameter named " + convertToFlowName(parameterName) + " in Flow is not matching with that in Fusion, please change its unit in Flow so that they match")
        # user is informed when a parameter does not exist in Flow but exists in Fusion due to its deletion within Flow etc.
        else:
            ui.messageBox(str(convertToFlowName(parameterName)) + " does not exist in Flow")

    



def pushValuesToFlow(ui, design: adsk.fusion.Design):
    # Opening JSON file and authenticating the account
    with open('/Users/alptug/Desktop/cred/Autodesk-x-flow-intergration/credentials.json') as json_file:
        Data = json.load(json_file)
        username = Data["username"]
        password = Data["password"]

    # authenticating 
    url = "https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_iODQDOUFS"

    payload = {
        "ClientId": "4bmi0kl02b8312nt2qnacdkubn",
        "AuthFlow": "USER_PASSWORD_AUTH",
        "AuthParameters": {
            "USERNAME": username,
            "PASSWORD": password
        }
    }

    headers = {
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    # uses token to authenticate the account
    Dict = json.loads(response.text)
    token = Dict["AuthenticationResult"]["IdToken"]

    # transport with a defined url endpoint
    transport = AIOHTTPTransport(
        url = "https://api.flowengineering.com/v1/graphql",
        headers = {
            "Authorization": f'Bearer {token}'
        },
    )

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    projectId = getProjectId(client)

    categoryId = getCategoryId(client, projectId)

    datasQueryResult = getDatasQueryResult(client, categoryId)

    datasUpdateQuery = gql(
        """
    mutation UpdateData(
	    $dataId: uuid!
	    $value: Value
    ) {
	updateData(
		input: {
			dataId: $dataId			
			value: $value
		}
	) {
		data {
			name
			description
			folder{
				folder_id
				name
			}
			maturity {
				name
				colour
			}
			    value
		    }
	    }
    }
    """
    )

    # Keys of dataFlowNameToExpressionDict1 are that corresponding to Flow and keys of dataFlowNameToExpessionDict2 are that corresponding to Fusion 
    dataFlowNameToExpressionDict1 = {}
    for x in datasQueryResult["data"]: 
        # extract the value from the query
        dataExpression = x["value"]
        # put the value into dataIdList dictionary
        dataFlowNameToExpressionDict1[x["name"]] = dataExpression

    paramInModel = design.userParameters
    dataFlowNameToExpressionDict2 = {}
    for i in range(paramInModel.count):
        dataFlowNameToExpressionDict2[convertToFlowName(paramInModel.item(i).name)] = paramInModel.item(i).expression


    # difference1 contains names of the parameters in Fusion which does not exists in Flow
    difference1 = subtractLists(dataFlowNameToExpressionDict2.keys(), dataFlowNameToExpressionDict1.keys())

    # difference2 contains names of the parameters in Fusion which exists in Flow (the union of difference 1 and difference2 is equal to dataFlowNameToExpressionDict2.keys())
    difference2 = subtractLists(dataFlowNameToExpressionDict2.keys(), difference1)

    difference2ToExpressionDict = {}
    for name, expression in dataFlowNameToExpressionDict2.items():
        if name in difference2:
            difference2ToExpressionDict[name] = expression

    for name, expression in difference2ToExpressionDict.items():
        dataId = getParameterId(name, datasQueryResult["data"])
        client.execute(datasUpdateQuery, {"dataId": dataId,
	                                      "value": expression 
                                         })  


    dataCreateQuery = gql(
        """
    mutation CreateData($category: uuid!, $name: String!) {
	    createData(
		    input: { category: $category, name: $name }
	    ) {
		    data {
			    data_id
			    folder_id
			    category_id
			    name
		    }
	    }
    }
    """
    )

    # folderId = getFolderId(client, categoryId)
    
    for name in difference1: 
        dataCreateQueryResult = client.execute(dataCreateQuery, variable_values={"category": categoryId,
	                                                     "name": name
                                                        })
        # pushes the value of the new created parameter to Flow
        client.execute(datasUpdateQuery, variable_values={"dataId": dataCreateQueryResult["createData"]["data"]["data_id"],
	                                                      "value": paramInModel.itemByName(convertToFusionName(name)).expression
                                                         })

    # THE FOLLOWING PART HANDLES PUSHING PHYSICAL PROPERTIES SUCH AS MASS AND VOLUME

    # Get the root component of the active design.
    product = app.activeProduct
    rootComp = adsk.fusion.Design.cast(product).rootComponent


    # The following two for loops traverses through the active design and totals the mass and volume of every body within the design.

    # Iterate over any bodies in the root component.
    totalVolume = 0
    totalMass = 0
    for i in range(0, rootComp.bRepBodies.count):
        body = rootComp.bRepBodies.item(i)
        # Get the mass and volume of the current body and add it to the total.
        totalVolume += body.physicalProperties.volume
        totalMass += body.physicalProperties.mass

    # Iterate through all of the occurrences in the assembly.
    for i in range(0, rootComp.allOccurrences.count):
        occ = rootComp.allOccurrences.item(i)
            
        # Get the associated component.
        comp = occ.component
            
        # Iterate over all of the bodies within the component.
        for j in range(0, comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
                
            # Get the mass and volume of the current body and add it to the total.
            totalVolume += body.physicalProperties.volume
            totalMass += body.physicalProperties.mass

    # Create the expression for the volume using the default distance units
    volumeResult = design.unitsManager.formatInternalValue(totalVolume, design.unitsManager.defaultLengthUnits + '^3', True)
    # Create the expression for the mass using the 'kg' unit
    massResult = str(totalVolume) + " kg"

    
def convertToFlowName(fusionName):
    flowName = fusionName[0].upper()
    if fusionName[0].islower() and fusionName[1:].isupper():
        flowName += fusionName[1:]
    else:
        for i in range(1, len(fusionName)):
            if fusionName[i].isupper():
                flowName += " " + fusionName[i]
            else:
                flowName += fusionName[i]
    ## for i in range(1, len(fusionName)):
       ## if fusionName[i].islower() and fusionName[i - 1] == '_':
         ##   flowName += fusionName[i].upper()
        ## elif fusionName[i].islower():
        ##    flowName += fusionName[i]
        ##elif fusionName[i] == '_':
          ##  flowName += " "
        ##elif fusionName[i].isupper():
          ##  flowName += " " + fusionName[i]
    return flowName

# def getParameterValue(parameter):
  #  return (parameter.split())[0]

def getParameterUnit(parameter):
    return (parameter.split())[1]

def subtractLists(list1, list2):
    return list(set(list1) - set(list2))

def findMatchingDataId(fusionName, datasQueryResult):
    for x in datasQueryResult["data"]:
        if x["name"] == convertToFlowName(fusionName):
            return x["data_id"]
    
    # if the for loop does not return anything, there is no matching parameter name in Fusion and thus a corresponding one shoudl be created
    # paramInModel.add(fusi, , , "")

def getParameterName(dataId, dataDict):
    for x in dataDict:
        if x["data_id"] == dataId:
            return x["name"]

def getParameterId(dataName, dataDict):
    for x in dataDict:
        if x["name"] == dataName:
            return x["data_id"]
    
#def getParameterExpression(dataId, datasQueryResult):
 #   for x in datasQueryResult["data"]:
  #      if x["data_id"] == dataId:
   #         return x["value"]

def convertToFusionName(flowName):
    fusionName = flowName[0].lower() + flowName[1:].replace(" ", "")
    return fusionName

def findMatchingValue(dataId1, dataIdToValueDict):
    for dataId2, value in dataIdToValueDict.items():
        if dataId1 == dataId2:
            return value

def getProjectId(client):
    projectQuery = gql(
        """
    query Projects {
	    project {
		    project_id
		    name
		    description
		    creator {
			    user_id
			    given_name
			    family_name
		    }
		    archived
	    }
    }   
    """
    )

    projectQueryResult = client.execute(projectQuery)

    return projectQueryResult["project"][0]["project_id"]



def getCategoryId(client, projectId):
    categoryQuery = gql(
        """
    query DataCategories($projectId: uuid!) {
	    data_category(where: { project_id: { _eq: $projectId } }) {
		    category_id
		    name
		    human_id_prefix
		    project {
			    project_id
			    name
		    }
		    archived
	    }
    }
    """
    )

    categoryQueryResult = client.execute(categoryQuery, variable_values={"projectId": projectId})

    return categoryQueryResult["data_category"][0]["category_id"]


def getDatasQueryResult(client, categoryId):
    datasQuery = gql(
        """
    query Data($categoryId: uuid!) {
	    data(where: { category_id: { _eq: $categoryId } }) {
		    data_id
		    name
		    human_id
		    value
		    category {
			    category_id
			    name
			    human_id_prefix
		    }
		    archived
	    }   
    }
    """
    )

    datasQueryResult = client.execute(datasQuery, variable_values={"categoryId": categoryId})
    return datasQueryResult

def removeVersionSuffix(fileName):
    splittedFileName = fileName.split()
    rm = splittedFileName[:-1]
    listToStr = ' '.join([str(elem) for elem in rm])
    return listToStr

def adjustExpression(expression):
    for i in range(len(expression) - 1):
        if expression[i].isnumeric() and expression[i + 1].isalpha(): # there is no space between the value and units in this case
            expression = expression[:i + 1] + " " + expression[i + 1:]
    return expression   



#def getFolderId(client, categoryId):
#    dataFolderQuery = gql(
#        """
#    query DataFolders($categoryId: uuid!) {
#	    data_folder(where: { category_id: { _eq: $categoryId } }) {
#		    folder_id
#		    name
#		    category {
#			    category_id
#			    name
#			    human_id_prefix
#		    }
#	    }
#    }
#    """
#    )
#
#    dataFolderQueryResult = client.execute(dataFolderQuery, variable_values={"categoryId": categoryId})
#    return dataFolderQueryResult