# FilewaveDEP

Our Goal is to make the process of building and re-purposing workstations faster and more enjoyable. I.T. takes too long to service user needs as quickly as they expect.

# Workflow

We use Filewave as our MDM solution to support our fleet of macs and PC's. We needed a solution that did not have platform limitations.  We don't install the Filewave client with Filewave.  We made a custom package based off the work of Erik Gomez's Installapplications - https://github.com/erikng/installapplications

The custom .pkg is uploaded to Filewave, one of the few MDM vendors that allow custom .pkg's.  Our InstallApplications is instructed to download the following:

# preflight packages

NONE

# setupassistant packages

fwcld_log_dummy.pkg puts a empty log file in /var/log/fwcld.log 
DEPNotify.pkg installs DEPNotify and opens the app using the -filewave flag

# reason for setupassistant packages

fwcld_log_dummy is a Placeholder log file until the Filewave client gets installed.  We are using DEPNotify to share computer build information with the user.  We open DEPNotify with the -filewave flag so DEPNotify reads the activity in the fwcld.log sharing build information progress.  IF we open DEPNotify and there is no fwcld.log file existing in /var/log, DEPNotify will quit and fails to show build content to the user.

# userland packages

EnergySaverProfile.pkg installs a profile configuring the mac not to sleep
comanylogo.pkg places company logo for use in DEPNotify's status window
wait_for_dock.py waits for the dock to start in the user session
filewavebootstrap.py names computer in user session

# reason for userland packages

Filewave will download all packages, settings and configurations for the workstation before it installs or configures anything.  Apple sets macs to sleep after 15min out of the box.  EnergySaverprofile will change sleep to an hour resolving the issue.  wait_for_dock.py waits for the dock to start in the user session.  When the dock is running, the filewave bootstrap script opens a window prompting the user for their Division, location and role.  The Filewave bootstrap renames the computer appending the serialnumber at the end.  After the computer is renamed, the Filewave bootstrap script downloads and installs the Filewave client.

# bootstrap.json - InstallApplications component 

bootstrap.json is used as a package manifest instructing InstallApplications what to download from our webserver.

# role_map.json

role_map.json Defines our company locations, departments and roles chosen from the FilewaveBootstrap.py script

# com.company.installapplications.plist

com.company.installapplications.plist - LaunchDaemon deployed in InstallApplications

# extras

make sure the permissions on your custom FileWaveClient.pkg are 644 apache apache
`-rw-r--r--.  1 apache apache    34454 Feb  6  2018 FileWaveClient.pkg`


more documentation to follow 

