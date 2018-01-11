# opennebula-flaskapp.py
# License: Undecided
#
# Portions of the code are obtained from StackOverflow, which the content is licensed under
# the Creative Commons CC BY-SA 3.0 with Attribution Required license.
# More info of Creative Commons license are available here:
# https://creativecommons.org/licenses/by-sa/3.0/
#
# Author: Chong Jin Yi, UniMy (chong.jy@student.unimy.edu.my)
# Please include "HPCCC OpenNebula Flask Web" in subject if you want to contact the author
#
# This program is a proof-of-concept code for a web frontend that allows
# a simplified way to create, stop, start and fetch the first IP address
#
# Notes:
# -The code here are a reference, it may not have all available features and may break anytime
# -Depending on which library you use for XML, you might need to use a different method to extract
#  IP address info from the instance info
# -Exceptions are handled at most on preventing crashes due to malformed XHR requests,
#  but **not** on the XML-RPC level
#
# Known issues:
# -Loads of hardcoding (OpenNebula username and passwords,
#  IP address and port, data extraction from XML)
# -Data type checking is almost nonexistant, save for the XML-RPC client communications
#
# It is possible that this code have more hidden issues that I may have overlooked
#
# DISCLAIMER:
# This code may be the worst code you have seen by far, but keep in mind that the coder:
# -is a sysadmin, not a programmer
# -programming is not his thing
# -new to Python, XML and XML-RPC
# -always look for shortcuts, even if the shortcut is obviously have obvious
#  general/security flaws or downright dangerous if malformed data is received :P
#
# If you think the coder has made the worst sin in Python coding, feel free to shoot a flame
# mail to the author, he will happily accept any suggestions.
#
# Good luck, and happy hacking!

from xmlrpc.client import ServerProxy
from flask import Flask, render_template, request
import untangle

# Instantiate the default Flask object
APP = Flask(__name__)

# OpenNebula session string for use when requesting data using XML-RPC
OPENNEBULA_SESSION = "oneadmin:opennebula"

# Dictionary to perform checks for the VM state
VM_STATE_MAPPING = {
    0: "Initializing",
    1: "Pending",
    2: "On Hold",
    3: "Active/Running",
    4: "Stopped",
    5: "Suspended",
    6: "Done", #Not sure on the use on this status
    # 7 is removed since it is not in use
    8: "Powered Off",
    9: "Undeployed",
    10: "Cloning",
    11: "Cloning Failed",
}

# Accepts an IP address that will connect to the XML-RPC server
# If conn is None (as in no value at all), 127.0.0.1 is assumed.
def create_xmlrpc_connection(conn=None):
    if conn is None:
        return ServerProxy("http://127.0.0.1:2633")
    return ServerProxy("http://"+conn+":2633")

# OPTIONAL, BUT RECOMMENDED:
# This function is used to disable web browsers from caching content since a
# completed request response doesn't need to be cached at all.
# Should work on most browsers.
@APP.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Cache-Control"] = "public, max-age=0"
    return response

# Renders the index page if / is requested
@APP.route('/')
def hello_world():
    return render_template("index.html")

# Decorator and view function used to accept objectid parameter and then
# attempts to start the VM and return the result
@APP.route('/start', methods=['POST'])
def startvm():
    # Define the operation used to start the VM
    operation = "resume"
    if request.method == "POST":
        try:
            # Collects the ID from the request and attempts to cast it to integer
            objectid = int(request.form['objectid'])
            # Create the connection
            xmlrpc_conn = create_xmlrpc_connection("192.168.4.196")
            # Send the request to OpenNebula XML-RPC server and collect the result
            result = xmlrpc_conn.one.vm.action(OPENNEBULA_SESSION, operation, objectid)
        except:
            # if casting to integer fails, return failed message and
            # return the objectid received in string format
            return "objectid is invalid. Value of objectid is: "+str(objectid)
    # If the execution finished without any exceptions, return the list casted
    # into string format to the sender
    return str(result)

# Stops the VM given the VM object ID
# If the object ID doesn't have a value, fail silently and return error message
# Else, send the result back to the caller in Python list form
@APP.route('/stop', methods=['POST'])
def stopvm():
    # Define the keyword to perform VM shutdown
    operation = "stop"
    if request.method == "POST":
        try:
            # Collects the ID from the request and casts into integer
            objectid = int(request.form['objectid'])
            # Create the connection
            xmlrpc_conn = create_xmlrpc_connection("192.168.4.196")
            # Send the request to OpenNebula XML-RPC server and store the returned result
            result = xmlrpc_conn.one.vm.action(OPENNEBULA_SESSION, operation, objectid)
        except:
            # If casting to integer fails, return failed message and return the objectid
            # received in string format
            return "objectid is invalid. Value of objectid is: "+str(objectid)
    # If the execution finished without any exceptions, return the list casted
    # into string format to the sender
    return str(result)

# Provides the IP addresses attached to the interface given the objectid
# If the object ID doesn't have a value, fail silently and return error message
# Else, return a list of the VM ID, name, state and first interface IP address
# Notes:
# a) This code assumes that the interface only have one interface.
#    Changes are required to allow multiple interfaces
@APP.route('/status', methods=['POST'])
def status():
    if request.method == 'POST':
        try:
            # Collects the ID from the request and casts into integer
            objectid = int(request.form['objectid'])
            # Create the connection
            xmlrpc_conn = create_xmlrpc_connection("192.168.4.196")
            # Initialize an empty list to store the result
            resultlist = []
            # Send the request to OpenNebula XML-RPC server and store the returned result
            result = xmlrpc_conn.one.vm.info(OPENNEBULA_SESSION, objectid)
            # Extract the data section of the list and then parse the XML output
            # Recommended: Run through XML validation using your favourite XML library
            obj = untangle.parse(result[1])
            # Capture the VM state value
            state_value = int(obj.VM.STATE.cdata)
            # Append the VM ID into the list
            resultlist.append(obj.VM.ID.cdata)
            # Append the VM name to the list
            resultlist.append(obj.VM.NAME.cdata)
            # Fetch the name of the state based on the value given from the dictionary
            # and append to the list
            resultlist.append(VM_STATE_MAPPING.get(state_value, "Invalid status"))
            # Append the VM first interface IP address into the list
            # Note: does not consider about multiple interfaces yet
            resultlist.append(obj.VM.TEMPLATE.CONTEXT.ETH0_IP.cdata)
        except:
            # If casting to integer fails, return failed message and return the objectid
            # received in string format
            return "objectid is invalid. Value of objectid is: "+str(objectid)
    # If the execution finished without any exceptions, return the list casted
    # into string format to the sender
    return str(resultlist)

# Returns all VM info available
# Requires either a XML library that can handle arbitrary length XML data or
# do required to prevengt the "path too long" issue on Windows
# Will return a list of VMs with the ID, name, state and first interface IP address
# List format will be the same as fetching single VM status on /status route,
# except this contains a list of the VM status list.
# This code works around that with the Untangle XML library because it cannot
# parse the XML if there's more than 7 VMs on OpenNebula and make use
# of the exception system to stop the loop
@APP.route('/statusall', methods=['POST'])
def statusall():
    if request.method == 'POST':
        # Create the connection
        xmlrpc_conn = create_xmlrpc_connection("192.168.4.196")
        # Initialize an empty list to store the result
        resultlist = []
        #Define a start position
        start_position = 0
        # Run the loop until an exception has reached, in which the loop will break
        while True:
            # Send the request to OpenNebula to fetch 5 VM infos and store the returned result
            result = xmlrpc_conn.one.vmpool.info(
                OPENNEBULA_SESSION, -2, start_position, start_position+4, -2)
            # Extract the data section of the list and then parse the XML output
            # Recommended: Run through XML validation using your favourite XML library
            obj = untangle.parse(result[1])
            try:
                # A for loop to iterate through the list
                for vm_listing in obj.VM_POOL.VM:
                    # Capture the VM state value
                    state_value = int(vm_listing.STATE.cdata)
                    # Appends a list of VM ID, name, word representation of the state and
                    # the first interface IP address
                    resultlist.append(
                        [vm_listing.ID.cdata,
                         vm_listing.NAME.cdata,
                         VM_STATE_MAPPING.get(state_value, "Invalid status"),
                         vm_listing.TEMPLATE.CONTEXT.ETH0_IP.cdata])
            except:
                # Breaks out when it reaches the end of the data
                break
            # Increment the start position value by 5 to proceed to fetch
            # more values from OpenNebula
            start_position = start_position+5
    # If the execution finished without any exceptions, return the list casted
    # into string format to the sender
    return str(resultlist)

# Creates new VM based on existing templates
# Note:
# -Name of VM is autogenerated by the system using "templatename-id"
# -VM generated are using the defaults. Can be modified by changing the 5th parameter
#  Refer to OpenNebula XML-RPC API documentation for more info.
@APP.route('/create', methods=['POST'])
def createvm():
    if request.method == "POST":
        try:
            # Collects the ID from the request and casts into integer
            objectid = int(request.form['objectid'])
            # Create the connection
            xmlrpc_conn = create_xmlrpc_connection("192.168.4.196")
            # Send the request to OpenNebula and store the returned result
            result = xmlrpc_conn.one.template.instantiate(
                OPENNEBULA_SESSION, objectid, "", False, "", False)
        except:
            # If casting to integer fails, return failed message and return
            # the objectid received in string format
            return "objectid is invalid. Value of objectid is: "+str(objectid)
    # If the execution finished without any exceptions, return the list casted
    # into string format to the sender
    return str(result)
