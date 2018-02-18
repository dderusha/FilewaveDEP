"""
Get a computer setup for FileWave automation.

Present dialog to set division/building/role,
Name computer based on above choices,
download and install fw client,
Set division/building/role fields in custom.ini.
"""
import json
import platform
import subprocess
import sys
import Tkinter as tk
import urllib
from os import path

import objc
import requests
from Foundation import NSBundle

# import fw_apy

GITLAB_API = 'https://server.company.com/api/v3/'
PROJECT_PATH = 'path_to_project'
BRANCH_PATH = 'testbranch'
ROLE_MAP_PATH = 'role_map.json'
PRIVATE_TOKEN = 'private_token=SuP3rS3cr3t'
FILEWAVECLIENT = 'InstallApplications/v2/FileWaveClient.pkg'


def build_gitlab_url(file_path):
    """Return a gitlab url string for given file_path."""
    return '{}{}{}?filepath={}&{}'.format(GITLAB_API, PROJECT_PATH,
                                          BRANCH_PATH, file_path,
                                          PRIVATE_TOKEN)


ROLE_MAP_ADDRESS = build_gitlab_url(ROLE_MAP_PATH)
FILEWAVECLIENTDOWNLOAD = build_gitlab_url(FILEWAVECLIENT)


def get_mac_serial():
    """Return machine serial number for Macs."""
    iokit_bundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')
    functions = [("IOServiceGetMatchingService", b"II@"),
                 ("IOServiceMatching", b"@*"),
                 ("IORegistryEntryCreateCFProperty", b"@I@@I")]
    objc.loadBundleFunctions(iokit_bundle, globals(), functions)
    match = IOServiceMatching("IOPlatformExpertDevice")
    service = IOServiceGetMatchingService(0, match)
    return IORegistryEntryCreateCFProperty(service, "IOPlatformSerialNumber",
                                           None, 0)


def get_role_map():
    """Get JSON file from GitLab and to a dict."""
    role_map_url = urllib.urlopen(ROLE_MAP_ADDRESS)
    role_map_json = role_map_url.read()
    if 'error' in role_map_json:
        raise Exception('{} at: {}'.format(role_map_json['error'],
                                           ROLE_MAP_ADDRESS))
    return json.loads(role_map_json)


class UserDetailsDialog(tk.Frame):
    """Display detail popup menus and return selection."""

    def __init__(self, parent, role_map):
        """Present dialog and return user choice (division, building, role)."""
        tk.Frame.__init__(self, parent)
        self.role_map = role_map
        self.role = {'var': tk.StringVar(),
                     'header': tk.StringVar(),
                     'cmd': lambda x: self.ok_button.config(state='normal'),
                     'row': 4}
        self.role['var'].set('Choose Role')
        self.role['label'] = tk.Label(self, textvariable=self.role['header'],
                                      width=42, bg='red', fg='white')

        self.building = {'var': tk.StringVar(),
                         'header': tk.StringVar(),
                         'cmd': lambda x: set_menu(x, self.role,
                                                   self.building['options']),
                         'row': 2}
        self.building['var'].set('Choose Building')
        self.building['label'] = tk.Label(self,
                                          textvariable=self.building['header'],
                                          width=42, bg='red', fg='white')

        self.division = {'var': tk.StringVar(),
                         'header': 'Division',
                         'options': self.role_map,
                         'cmd': lambda x: set_menu(x, self.building,
                                                   self.division['options']),
                         'row': 0}
        self.division['var'].set('Choose Division')
        self.division['label'] = tk.Label(self, text=self.division['header'],
                                          width=42, bg='red', fg='white')

        def set_menu(selection, next_menu, options):
            """Set the next menu's label and options."""
            # print selection
            # print [item for item in options[selection]]
            next_options = options[selection]
            if "prefix" in next_options:
                next_options = (next_options.get('buildings', None) or
                                next_options['roles'])
            next_menu['options'] = next_options
            # print next_menu['options']
            next_menu['header'].set(selection)
            menu = build_menu(next_menu)
            next_menu['label'].grid(row=next_menu['row'])
            menu.grid(row=next_menu['row'] + 1)

        def build_menu(section):
            """Return an OptionMneu for section."""
            menu_config = tuple((self, section['var']) +
                                tuple([item for item in section['options']]))
            return tk.OptionMenu(*menu_config,
                                 command=section['cmd'])

        def ok_action(parent):
            """Destroy Window."""
            parent.destroy()

        self.ok_button = tk.Button(self, text='OK',
                                   state='disabled',
                                   command=lambda: ok_action(parent))
        self.ok_button.grid(row=20)

        division_menu = build_menu(self.division)
        self.division['label'].grid(row=self.division['row'])
        division_menu.grid(row=self.division['row'] + 1)

    def show(self):
        """Show window and wait for response."""
        # self.wm_deiconify()
        # self.entry.focus_force()
        self.wait_window()
        division = self.division['var'].get()
        building = self.building['var'].get()
        role = self.role['var'].get()

        return (division, building, role)


def choose_prefix():
    """Present window to get user details and return name prefix_parts."""
    root = tk.Tk()
    root.wm_geometry("400x200")
    root.title('Select User Details')

    role_map = get_role_map()
    window = UserDetailsDialog(root, role_map)
    window.grid()

    selection = window.show()
    # root.mainloop()

    division = role_map[selection[0]]
    building = division['buildings'][selection[1]]
    role = building['roles'][selection[2]]

    return (division['prefix'], building['prefix'], role)


def build_name(prefix_parts=None):
    """Get details and return new computer name."""
    if not prefix_parts:
        prefix_parts = choose_prefix()
    serial = get_mac_serial()
    name_parts = (prefix_parts + (serial,))
    return "{}-{}-{}-{}".format(*name_parts)


def name_mac(new_name):
    """Use scutil to rename a mac to new_name."""
    name_types = ['HostName', 'LocalHostName', 'ComputerName']
    for name_type in name_types:
        subprocess.call(['scutil', '--set', name_type, new_name])


def write_custom_field(field, value):
    """Set field to value in custom.ini."""
    target_os = platform.system()
    if target_os == 'Windows':
        fwcld_path = path.normpath('C:/Program Files (x86)/FileWave/fwcld')
    else:
        fwcld_path = '/usr/local/sbin/FileWave.app/Contents/MacOS/fwcld'

    command = [fwcld_path, '-custom_write',
               '-key', field,
               '-value', value]

    cmd_exececution = subprocess.Popen(command, shell=False,
                                       bufsize=1,
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    (output, dummy_err) = cmd_exececution.communicate()

    return output


def main():
    """Script workflow."""
    prefix_parts = choose_prefix()
    name = build_name(prefix_parts)
    division, building, role = prefix_parts
    print name
    write_custom_field('custom_string_04', division)
    write_custom_field('department', role)
    write_custom_field('building', building)
    name_mac(name)
    filewave_client = download_file(FILEWAVECLIENTDOWNLOAD,
                                    "/tmp/FileWaveClient.pkg")
    install_result = install_pkg(filewave_client)
    return install_result


def download_file(file_url, local_file_path):
    """Download file at file_url and save to local_file_path."""
    try:
        response = requests.get(url=file_url)
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        # print('Response HTTP Response Body: {content}'.format(
        #     content=response.content))
    except requests.exceptions.RequestException:
        print 'HTTP Request failed'
    with open(local_file_path, 'wb') as local_file:
        for chunk in response.iter_content(chunk_size=128):
            local_file.write(chunk)
    return local_file_path


def install_pkg(package):
    """Install package with Installer and return result."""
    cmd = ['sudo', '/usr/sbin/installer', '-pkg', package, '-tgt', '/']
    return subprocess.check_output(cmd, shell=False)


if __name__ == "__main__":
    INSTALL_RESULT = main()
    # filewave_client = download_file(FILEWAVECLIENTDOWNLOAD,
    #                                 "/tmp/FileWaveClient.pkg")
    # INSTALL_RESULT = install_pkg('/Users/dohare/Desktop/test_package.pkg')
    sys.exit(INSTALL_RESULT)
    # COMPUTER_NAME = main()
    # sys.exit(COMPUTER_NAME)
