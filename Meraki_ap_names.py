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


def get_organization_ids(api_key):
    print('Getting organizations...')
    orgs = get_data('https://api.meraki.com/api/v1/organizations', api_key)
    orgs_dict = {}
    for item in orgs:
        orgs_dict[item['name']] = item['id']
    print('Done!')
    logging.debug('Organizations data is received via API')
    return orgs_dict


def get_organization_aps(api_key, orgs_dict, organization_name = ''):
    aps_dict = {}
    print('Getting AP serial numbers...')
    if organization_name != '':
        if organization_name in orgs_dict:
            orgs_dict = {key:value for key,value in orgs_dict.items() if key == organization_name}
        else:
            logging.debug('Provided organization name does not exists')
            raise SystemExit('Provided organization name does not exists')
    for org_id in orgs_dict.values():
        aps_dict[org_id] = {}
        url = 'https://api.meraki.com/api/v1/organizations/' + org_id + '/devices/statuses'
        query = {'productTypes[]': 'wireless'}
        aps = get_data(url, api_key, query)
        if len(aps) > 0:
            for item in aps:
                if 'errors' not in item:
                    aps_dict[org_id][item['name']] = item['serial']
    print('Done!')
    logging.debug('AP serial data is received via API')
    return aps_dict


def get_aps_bssids(api_key, aps_dict):
    bssids_dict = {}
    print('Getting AP BSSIDs...')
    for ap_info in aps_dict.values():
        for ap,serial in ap_info.items():
            url = 'https://api.meraki.com/api/v1/devices/' + serial + '/wireless/status'
            bssids = get_data(url, api_key)
            bssid = bssids['basicServiceSets'][0]['bssid']
            bssids_dict[ap] = bssid
    print('Done!')
    logging.debug('AP name - MAC address data is received via API')
    return bssids_dict


def add_ap_names(project_filename, bssid_dict):
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

        for item in bssid_dict.items():
            ap_name = item[0]
            bssid = item[1][:-1] #Intentionally removed last symbol from MAC address
            for measurement in accessPointMeasurements['accessPointMeasurements']:
                if bssid in measurement['mac']: #We found BSSID -> MAC
                    logging.debug('We found BSSID -> MAC ' + bssid + ' ' + measurement['mac'] + ' ' + measurement['id'])
                    for measuredRadio in measuredRadios['measuredRadios']:
                        if measurement['id'] in measuredRadio['accessPointMeasurementIds']: #We catch MAC -> Measurement ID and found Access_point_ID
                            logging.debug('We found MAC -> Measurement ID and found Access_point_ID' + bssid + ' ' + measurement['mac'] + ' ' + measurement['id'] + ' ' + measuredRadio['accessPointId'])
                            for ap in accessPoints['accessPoints']:
                                if ap['id'] == measuredRadio['accessPointId']:
                                    print('Changed AP name in project file ', ap['name'],' to ',ap_name)
                                    ap['name'] = ap_name

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
    log_filepath = home / 'Ekahau.log'
    logging.basicConfig(filename = str(log_filepath), encoding='utf-8', filemode='w', level=logging.DEBUG)
    if len(sys.argv) > 1:
        logging.debug('Correct number of arguments supplied')
        meraki_api_key = sys.argv[1]
        project_filepath = home / sys.argv[2]
        if len(sys.argv) > 3:
            org_name = sys.argv[3]
        else:
            org_name = ''
        org_ids = get_organization_ids(meraki_api_key)
        aps = get_organization_aps(meraki_api_key, org_ids, org_name)
        bssid_dict = get_aps_bssids(meraki_api_key, aps)
        if len(bssid_dict) > 0:
            add_ap_names(project_filepath,bssid_dict)
        else:
            print('No BSSID data is received via API, please check logs')
            logging.debug('No BSSID data is received via API, please check logs')
    else:
        print('Incorrect number of arguments supplied, please check README for instructions')
        logging.debug('!!! INCorrect number of arguments supplied: ' + str(len(sys.argv)))


if __name__ == "__main__":
    main()