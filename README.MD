Are you a wireless engineer who's ever tried to decipher RF site survey data from an Ekahau survey project, only to discover that your access points are suffering from a severe case of namelessness? 📡🤷‍♂️

Don't worry; you're not alone! This "name-nesia" epidemic has baffled even the most seasoned Meraki wireless network experts. But fear not, there's hope on the horizon!

But here's the good news: If you're posessing the Meraki API key, you're just a couple of clever commands away from naming enlightenment. Say goodbye to featureless "Measured AP-39:a4" and hello to crystal-clear "CEO-Office-VIP-AP"! 🎉

Join us on this whimsical adventure through the wonderful world of wireless wizardry, where AP "name-nesia" is a thing of the past. Get ready to unravel the mysteries of Meraki with a sprinkle of tech-savvy magic! 

On a serious note, special feature for broadcasting AP names in 802.11 beacon frames should be enabled by Meraki support team during survey. If it was not done properly, you can get the data about AP names via your Meraki API.


## AP name adder for Ekahau project files for Meraki Customers

Python script to add the names of access points into the Ekahau survey project file.
Meraki API is used as the source of data about AP names.


Example of project data before using this tool:
![title](./Screenshot_no_AP_names.png "Initial Ekahau project no AP names")


After using this tool (the project file is enriched with data from Meraki cloud and all AP names are fulfilled)   :
![title](./Screenshot_with_AP_names.png "Ekahau project enriched with AP names")

## Installation

Installation is not required as soon as you have Python installed to your PC, just clone the repository and go to folder:

Clone the repo
```bash
git clone https://github.com/consulttelecom/ekahau-meraki-ap-namer.git
```
Go to tool folder
```bash
cd ekahau-meraki-ap-namer
```
And install python dependencies
```bash
pip install -r requirements.txt
```

## Usage 

Copy the Ekahau survey project file (*.esx) in the tool file folder, then just start the tool as Python script from command line with arguments:

	```
	usage: Meraki_ap_names.py [-h] -t API_TOKEN -e File.esx [-o Meraki Organization Name] [-m] [-v]

	Sync Ekahau AP details with Meraki informations

	options:
	  -h, --help            show this help message and exit
	  -t API_TOKEN, --token API_TOKEN
	                        Meraki user token API
	  -e File.esx, --ekahau File.esx
	                        Insert full name with extension of ekahau file, it need to be in the same folder as this script C:\Users\pedro.dalcolli\PycharmProjects\ekahau-meraki-ap-import
	  -o Meraki Organization Name, --org Meraki Organization Name
	                        Insert the name of Meraki Organization to get data just from one Organization
	  -m, --model           Use this flag to change AP Models too
	  -v, --verbose         Show process steps

	```
Just APT_TOKEN and Ekahau File name is mandatory, Organization, model and verbose are optional
Some examples how to use:
on this example variables are: 
	token is: 1234token4321
	ekahau file is: WPS
	Organization is: Net Skilll
```bash
python.exe .\Meraki_ap_names.py -t 1234token4321 -e WPS.esx -v -o 'Net Skilll'
```
is possible to run with optinioal values too:
```bash
python.exe .\Meraki_ap_names.py -e WPS.esx -t 1234token4321
```

## Tested with:

* Ekahau AI PRO 11.6.1

### How to get in touch for support\questions\ideas etc.
Collaboration via github tools is the preferred way, so open the issue, make pull request, fork, star etc.
Please add the following data to your issues:
* log file written during the issue (Ekahau.log from root folder)
* describe your environment (PC, OS version, Python version, libraries version)