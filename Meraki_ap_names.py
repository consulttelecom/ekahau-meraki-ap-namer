import argparse
from tabnanny import verbose

import requests, time
import shutil
import zipfile
import json
import logging
import pathlib
import sys

__author__ = "Roman Podoynitsyn"


def get_data(url, api_key, query=[]):
    headers = {'Content-type': 'application/json',
               'X-Cisco-Meraki-API-Key': api_key}
    try:
        r = requests.get(url, headers=headers, params=query)
        if r.status_code == 429:
            time.sleep(int(r.headers["Retry-After"]))
            get_data(url, api_key, query)
        elif r.status_code == 404:
            print('Warning: API access is disabled for URL ', url)
            logging.debug('Warning: API access is disabled for URL ' + url)
            return r.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return r.json()


def get_organization_ids(api_key, verbose=False):
    """
    :param verbose: Show status on terminal
    :param api_key: API Token from Meraki
    :return: dictionary with organization and id like {'org_name':'12345678'}
    """
    orgs = get_data('https://api.meraki.com/api/v1/organizations', api_key)
    orgs_dict = {}
    for item in orgs:
        orgs_dict[item['name']] = item['id']
        if verbose:
            print(f'ORG: {item['name']}, ID: {item['id']} \n')
    logging.debug(f'Organizations received via API: \n'
                  f'{orgs_dict}')
    if verbose:
        print('Organizations - Done!')
    return orgs_dict


def get_organization_aps(api_key, orgs_dict, organization_name = '', ap_item = 'serial', verbose=False):
    """

    :param api_key: Meraki Token
    :param orgs_dict: Dictionary with organization name and id
    :param organization_name: Meraki Organization
    :param ap_item: if set to model, will get AP models instead Serials
    :param verbose: Print key and value on output
    :return: if serial, will return a dictionary with AP name and Serial, if model, AP name and model
    """
    aps_dict = {}
    if organization_name != '':
        if organization_name in orgs_dict.keys():
            orgs_dict = {key:value for key,value in orgs_dict.items() if key == organization_name}
            if verbose:
                print(f'Org selected: {orgs_dict}')
        else:
            logging.debug('Provided organization name does not exists')
            raise SystemExit('Provided organization name does not exists')
    for org_id in orgs_dict.values():
        aps_dict[org_id] = {}
        url = 'https://api.meraki.com/api/v1/organizations/' + org_id + '/devices/statuses'
        query = {'productTypes[]': 'wireless'}
        aps = get_data(url, api_key, query)
        if len(aps) > 0:
            if ap_item == 'serial':
                for item in aps:
                    if 'errors' not in item:
                        aps_dict[org_id][item['name']] = item['serial']
                        if verbose:
                            print(f'Linked {item['name']} to Serial: {item['serial']}')

                logging.debug(f'AP serial received via API: \n {aps_dict}')
                if verbose:
                    print('Serial Numbers - Done!')
                return aps_dict
            if ap_item == 'model':
                for item in aps:
                    if 'errors' not in item:
                        aps_dict[org_id][item['name']] = item['model']
                        if verbose:
                            print(f'Linked {item['name']} to Model: {item['model']}')

                logging.debug(f'AP Models received via API: \n {aps_dict}')
                if verbose:
                    print('AP Models - Done!')
                return aps_dict


def get_aps_bssids(api_key, aps_dict, verbose=False):
    """

    :param api_key: Meraki Token
    :param aps_dict: dictionary with AP name and Serial
    :param verbose: will print AP name and BSSID on output
    :return: will return a dictionary with AP name and first enabled BSSID
    """
    bssids_dict = {}
    for ap_info in aps_dict.values():
        for ap,serial in ap_info.items():
            url = 'https://api.meraki.com/api/v1/devices/' + serial + '/wireless/status'
            bssids = get_data(url, api_key)
            #Get first enabled BSSID
            for radio in bssids['basicServiceSets']:
                if radio['enabled']:
                    bssids_dict[ap] = radio['bssid']
                    if verbose:
                        print(f'Linked {ap} to BSSID {radio['bssid']}')
                    break
                else:
                    continue
    if verbose:
        print('BSSIDs - Done!')
    logging.debug(f'AP Name - BSSID address received via API \n'
                  f'{bssids_dict}')
    return bssids_dict



def add_ap_names(project_filename, bssid_dict, models, change_model=False, verbose=False):
    """

    :param project_filename: Ekahau file name with extension esx
    :param bssid_dict: dictionary get on get_aps_bssids()
    :param models: dictionary get on get_organizations_aps(ap_item='models')
    :param change_model: Set to true to change models of Ekahau AP with param models
    :param verbose: print changed AP name and Model
    :return: will decompress Ekahau file, change json files and create a new file with json modified
    """
    p = pathlib.Path('Ekahau/')
    p.mkdir(parents=True, exist_ok=True)
    working_directory = pathlib.Path.cwd()
    temp_folder_filepath = working_directory / 'Ekahau'
    # Load & Unzip the Ekahau Project File
    with zipfile.ZipFile(project_filename, 'r') as myzip:
        myzip.extractall(temp_folder_filepath)

        # Load the accessPoints.json file into the accessPoints dictionary
        with myzip.open('accessPoints.json') as json_file:
            accessPoints = json.load(json_file)

        # Load the measuredRadios.json file into the simulatedRadios dictionary
        with myzip.open('measuredRadios.json') as json_file:
            measuredRadios = json.load(json_file)

        # Load the accessPointMeasurements.json file into the simulatedRadios dictionary
        with myzip.open('accessPointMeasurements.json') as json_file:
            accessPointMeasurements = json.load(json_file)

        for meraki_name in bssid_dict:
            bssid = bssid_dict[meraki_name]
            for measurement in accessPointMeasurements['accessPointMeasurements']:
                if bssid[8:] in measurement['mac']:
                    # We found BSSID -> MAC
                    logging.debug(f'We found BSSID -> MAC {bssid} {measurement['mac']} {measurement['id']}')
                    for measuredRadio in measuredRadios['measuredRadios']:
                        if measurement['id'] in measuredRadio['accessPointMeasurementIds']:
                            # We catch MAC -> Measurement ID and found Access_point_ID
                            logging.debug(f'We found MAC -> Measurement ID and found Access_point_ID {bssid} '
                                          f'{measurement['mac']} {measurement['id']} {measuredRadio['accessPointId']}')
                            for ekahau_ap in accessPoints['accessPoints']:
                                if ekahau_ap['id'] == measuredRadio['accessPointId']:
                                    ekahau_ap['name'] = meraki_name
                                    if verbose:
                                        print(f'Changed AP name in project file {ekahau_ap['name']} to {meraki_name}')

        if change_model:
            for ap_info in models.values():
                for meraki_name, meraki_model in ap_info.items():
                    for ekahau_ap in accessPoints['accessPoints']:
                        if ekahau_ap['mine']:
                            if ekahau_ap['name'] == meraki_name:
                                ekahau_ap['model'] = meraki_model
                                logging.debug(f'Changed {ekahau_ap['name']} model to {meraki_model}')
                                if verbose:
                                    print(f'Changed {ekahau_ap['name']} model to {meraki_model}')


    # Write the changes into the accessPoints.json File
    filepath = temp_folder_filepath / 'accessPoints.json'
    with filepath.open(mode= "w", encoding="utf-8") as file:
        json.dump(accessPoints, file, indent=4)
    logging.debug('New accessPoints.json file is written')

    # Create a new version of the Ekahau Project
    new_filename = pathlib.Path(str(project_filename) +'_modified')
    shutil.make_archive(new_filename, 'zip', temp_folder_filepath)
    my_file = pathlib.Path(str(new_filename)+'.zip')
    my_file.rename(my_file.with_suffix('.esx'))
    #shutil.move(new_filename + '.zip', new_filename + '.esx')
    logging.debug('New project file is ready to use, filename is ' + str(my_file.with_suffix('.esx')))
    print('New project file is ready to use, filename is ' + str(my_file.with_suffix('.esx')))

    # Cleaning Up
    shutil.rmtree(temp_folder_filepath)
    logging.debug('Working folder is cleaned')


def main():
    home = pathlib.Path.cwd()

    #Log directory
    log_filepath = home / 'Ekahau.log'
    logging.basicConfig(filename=str(log_filepath), encoding='utf-8', filemode='w', level=logging.DEBUG)

    #Line Arguments
    line_option = argparse.ArgumentParser(description='Sync Ekahau AP details with Meraki informations')
    line_option.add_argument('-t', '--token', metavar='API_TOKEN',
                             help='Meraki user token API', required=True, type=str)
    line_option.add_argument('-e', '--ekahau',metavar='File.esx', type=str, required=True,
                             help='Insert full name with extension of ekahau file, '
                                  'it need to be in the same folder as this script'
                                  f'\n {home}')
    line_option.add_argument('-o', '--org', metavar='Meraki Organization Name', type=str, default='',
                             help='Insert the name of Meraki Organization to get data just from one Organization')
    line_option.add_argument('-m', '--model', action='store_true',
                             help='Use this flag to change AP Models too')
    line_option.add_argument('-v', '--verbose', help='Show process steps', action='store_true')

    # Variable means line arguments
    variable = line_option.parse_args()

    project_filepath = home / variable.ekahau

    #Get Meraki data's
    org_ids = get_organization_ids(variable.token, verbose=variable.verbose)
    aps = get_organization_aps(variable.token, org_ids, variable.org, verbose=variable.verbose)
    bssid_dict = get_aps_bssids(variable.token, aps, verbose=variable.verbose)

    if len(bssid_dict) > 0:
        if variable.model:
            models_dict = get_organization_aps(variable.token, org_ids, variable.org, ap_item='model', verbose=variable.verbose)
            add_ap_names(project_filepath, bssid_dict, models_dict, True, verbose=variable.verbose)
        else:
            add_ap_names(project_filepath, bssid_dict, False, verbose=variable.verbose)
    else:
        print('No BSSID data is received via API, please check logs')
        logging.debug('No BSSID data is received via API, please check logs')


if __name__ == "__main__":
    main()