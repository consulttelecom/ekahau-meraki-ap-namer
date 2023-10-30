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


***How to use the tool:***


Copy survey project file in the tool file folder, then just start it from command line with two (or three) arguments:

* First argument is the Meraki API key
* Second argument is the filename of Ekahau project file
* Third argument is the organisation name (OPTIONAL, can be useful to filter out data from other organisations if your Meraki account has many of them)

	```
	Example of tool output
	(venv) PS C:\Users\rpodoyni\Ekahau_tools> python.exe .\Meraki_ap_names.py 6922*************************223344def Floors.esx My_organisation         
	Getting organizations...
	Done!
	Getting AP serial numbers...
	Done!
	Getting AP BSSIDs...
	Done!
	Changed AP name in project file  Measured AP-39:d5  to  EMEA-SP-MDR-10PQR-WAP09
	Changed AP name in project file  Measured AP-39:e6  to  EMEA-SP-MDR-10PQR-WAP09
	Changed AP name in project file  Measured AP-39:f7  to  EMEA-SP-MDR-10PQR-WAP06
	Changed AP name in project file  Measured AP-39:a4  to  EMEA-SP-MDR-10PQR-AP705
	Changed AP name in project file  Measured AP-39:b8  to  EMEA-SP-MDR-10PQR-WAP10
	Changed AP name in project file  Measured AP-f0:eb  to  EMEA-SP-MDR-10PQR-WAP07
	New project file is ready to use, filename is C:\Users\rpodoyni\Ekahau_tools\Floors.esx_modified.esx
	(venv) PS C:\Users\rpodoyni\Ekahau_tools>
	```


## Tested with:

* Ekahau PRO 10
* Ekahau AI PRO 11

## Dependencies:
The following list of standard Python libraries are used in this tool:
* shutil
* zipfile
* json
* os
* logging
* sys

All of these are standard libraries and do not require any installation efforts.

### This tool is inspired by the following works of smart Wi-Fi guys:
* https://github.com/francoisverges/semfio-ekahau
* http://nerdian.ca/files/2020/06/EkahauFileStructure.pdf

### How to get in touch for support\questions\ideas etc.
Collaboration via github tools is the preferred way, so open the issue, make pull request, fork, star etc.
Please add the following data to your issues:
* log file written during the issue (Ekahau.log from root folder)
* describe your environment (PC, OS version, Python version, libraries version)