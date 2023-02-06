# PetKit Home Assistant Integration
![GitHub manifest version (path)](https://img.shields.io/github/manifest-json/v/RobertD502/home-assistant-flair?filename=custom_components%2Fpetkit%2Fmanifest.json)

<a href="https://www.buymeacoffee.com/RobertD502" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="100" width="424"></a>

### A lot of work has been put into creating the backend and this integration. If you enjoy this integration, consider donating by clicking on the logo above.

***All proceeds go towards helping a local animal rescue.**

___

Custom Home Assistant component for controlling and monitoring PetKit devices.

`Currently Supported Devices:`
- [Fresh Element Solo](https://www.amazon.com/PETKIT-Automatic-Dispenser-Compatible-Freeze-Dried/dp/B09158J9PF/)
- [Fresh Element Mini Pro](https://www.amazon.com/PETKIT-Automatic-Stainless-Indicator-Dispenser-2-8L/dp/B08GS1CPHH/)
- [Eversweet 3 Pro Water Fountain](https://www.amazon.com/PETKIT-Wireless-Fountain-Stainless-Dispenser/dp/B09QRH6L3M/)



## **Prior To Installation**

**This integration requires using your PetKit account `email` and `password`.**

**If using another PetKit integration that uses the petkit domain, you will need to delete it prior to installing this integration.**

**The current polling interval is set to 2 minutes. If you would like to set a different polling interval, change the `DEFAULT_SCAN_INTERVAL` in the constants.py file (in seconds).**

### If you don't have a water fountain on your PetKit account: 

Create a new PetKit account and share your devices from your original account to it. This will allow you to use your main account on the mobile app and the secondary account with this integration. Otherwise, your main account will get logged out of the mobile app when using this integration. This is a limitation of how PetKit handles authorization.

### If you do have a water fountain:

Unfortunately, there is no way of sharing a water fountain with a secondary account. As a result, you will need to use your main PetKit account to pull in water fountain data. When doing so, your main account will get signed out of any mobile app it is currently signed in on. This is a limitation of how PetKit handles authorization. If you only want to pull in data for non-water fountain devices, see "If you don't have a water fountain on your PetKit account" above.

`Note #1:` When using your main PetKit account: as long as you don't reopen the PetKit app, your notification token will remain valid allowing you to receive notifications from the PetKit app even though your account is technically signed out of the app.

`Note #2:` If you want to use the PetKit app momentarily to change some settings, be sure to disable the PetKit integration before logging into the app (If you don't, you will be asked to reauthenticate). Once you are done making changes within the app, re-enable the integration.

`Note #3:` Getting the most recent data from your water fountain, as well as controlling the water fountain, requires that the BLE relay is set up within the PetKit app. Otherwise, you will be limited to data that isn't up-to-date and no ability to control the water fountain as it requires another compatible PetKit device acting as a BLE relay. 

# Installation

## With HACS

1. Add this repository as a custom repository in HACS.
2. Download the integration.
3. Restart Home Assistant

## Manual
Copy the `petkit` directory, from `custom_components` in this repository,
and place it inside your Home Assistant Core installation's `custom_components` directory. Restart Home Assistant prior to moving on to the `Setup` section.

`Note`: If installing manually, in order to be alerted about new releases, you will need to subscribe to releases from this repository. 

## Setup

Click on the button below to add the integration:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=petkit)

Alternatively, follow the steps below:

1. Navigate to the Home Assistant Integrations page (Settings --> Devices & Services)
2. Click the `+ ADD INTEGRATION` button in the lower right-hand corner
3. Search for `PetKit`

# Devices

Each PetKit device is represented as a device in Home Assistant. Within each device
are several entities described below.


## Feeders

Each Feeder has the following entities:

| Entity                     | Entity Type     | Additional Comments                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|----------------------------|-----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Child lock`               | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                                                                                                                                                     |
| `Dispense tone`            | `Switch`        | -`Only available for Fresh Element Solo feeders.` <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                                                                                            |
| `Food shortage alarm`      | `Switch`        | -`Only available for Fresh Element Solo feeders.` <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                                                                                            |
| `Indicator light`          | `Switch`        | This entity is only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                                                                                                                                      |
| `Manual feed`              | `Select`        | - Allows setting the amount of food to dispense immediately - amount allowed is personalized to the type of feeder. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                          |
| `Food level`               | `Binary Sensor` | Allows for determining if there is a food shortage.                                                                                                                                                                                                                                                                                                                                                                                                          |
| `Cancel manual feed`       | `Button`        | -`Only available for Fresh Element Solo feeders.` <br/>- Allows you to cancel a manual feeding that is currently dispensing.                                                                                                                                                                                                                                                                                                                                 |
| `Reset desiccant`          | `Button`        | - Allows you to reset the desiccant back to 30 days after replacing it. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                                                                      |
| `Battery installed`        | `Binary Sensor` | -`Only available for Fresh Element Solo feeders. - Mini Feeders always report the same value regardless of if batteries are installed or not`. <br/>- If batteries are removed or installed, power cycling the feeder is required for the status to update.                                                                                                                                                                                                  |
| `Battery status`           | `Sensor`        | -`Will only become available when feeder is running on batteries.` <br/>- Indicates the battery level (Normal or Low). <br/>-`Friendly Note:` Mini feeders have a bug when batteries are installed that has never been addressed by PetKit. This can result in your device locking up until the batteries are removed and feeder is power cycled. I am not sure what triggers this bug, but as a safety measure I don't install batteries into mini feeders. |
| `Desiccant days remaining` | `Sensor`        | Number of days left before the desiccant needs to be replaced.                                                                                                                                                                                                                                                                                                                                                                                               |
| `Dispensed`                | `Sensor`        | -`Only available for Fresh Element Solo feeders.` <br/>- Amount of food, in grams, dispensed today.                                                                                                                                                                                                                                                                                                                                                          |
| `Manually dispensed`       | `Sensor`        | -`Only available for Fresh Element Solo feeders.` <br/>- Amount of food, in grams, manually dispensed today.                                                                                                                                                                                                                                                                                                                                                 |
| `Planned`                  | `Sensor`        | -`Only available for Fresh Element Solo feeders.` <br/>- Amount of food, in grams, that the feeder plans to dispense today.                                                                                                                                                                                                                                                                                                                                  |
| `Planned dispensed`        | `Sensor`        | -`Only available for Fresh Element Solo feeders.` <br/>- Of the planned amount that is to be dispensed today, amount of food (grams) that has been dispensed.                                                                                                                                                                                                                                                                                                |
| `RSSI`                     | `Sensor`        | WiFi connection strength.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `Status`                   | `Sensor`        | `Normal` = Feeder is connected to PetKit's servers <br/>`Offline` = Feeder is not connected to PetKit servers <br/>`On Batteries` = If installed, feeder is currently being powered by the batteries.                                                                                                                                                                                                                                                        |
| `Times dispensed`          | `Sensor`        | -`Only available for Fresh Element Solo feeders.` <br/>- Number of times food has been dispensed today.                                                                                                                                                                                                                                                                                                                                                      |


## Eversweet 3 Pro Water Fountain

Each water fountain has the following entities:

| Entity                     | Entity Type     | Additional Comments                                                                                                                                                                                                                                                                                                                                                    |
|----------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Do not disturb`           | `Switch`        | -`Only available if BLE relay is set up and main BLE relay device is online.` <br/>- Allows for enabling or disabling do not disturb - Use PetKit app to set do not disturb schedule if you plan on using this entity.                                                                                                                                                 |
| `Light`                    | `Switch`        | `Only available if BLE relay is set up and main BLE relay device is online.`                                                                                                                                                                                                                                                                                           |
| `Power`                    | `Switch`        | -`Only available if BLE relay is set up and main BLE relay device is online.` <br/>- Turning power off is equivalent to "Pause" in the PetKit app. <br/>- Turning power on resumes the water fountain in the mode (Normal/Smart) it was in prior to being powered off.                                                                                                 |
| `Filter`                   | `Sensor`        | Indicates % filter life left.                                                                                                                                                                                                                                                                                                                                          |
| `Water level`              | `Binary Sensor` | Indicates if water needs to be added to the water fountain.                                                                                                                                                                                                                                                                                                            |
| `Light brightness`         | `Select`        | `Only available if BLE relay is set up and main BLE relay device is online.`                                                                                                                                                                                                                                                                                           |
| `Mode`                     | `Select`        | -`Only available if BLE relay is set up and main BLE relay device is online.` <br/>- Allows setting mode to Normal or Smart. <br/>- For "Smart mode", use the PetKit app to set the water on and off minutes.                                                                                                                                                          |
| `Reset filter`             | `Button`        | `Only available if BLE relay is set up and main BLE relay device is online.`                                                                                                                                                                                                                                                                                           |
| `Energy usage`             | `Sensor`        |                                                                                                                                                                                                                                                                                                                                                                        |
| `Last data update`         | `Sensor`        | - Date/Time that the water fountain last reported updated data to PetKit servers. <br/>- This can be used to track and identify if the BLE relay is working correctly as this will change whenever the main BLE relay device polls the water fountain. <br/>- If you have the BLE relay set up, this sensor is only concerning if it shows data was updated hours ago. |


**Note About Water Fountain Control**


>  If you have the BLE relay set up in the PetKit app and the main BLE relay device is online, sometimes the bluetooth connection will fail when attempting to send a command (e.g., changing mode, light brightness, etc) . If this happens, it will be noted in the Home Assistant logs. Retrying the command usually results in a subsequent successful connection. 
