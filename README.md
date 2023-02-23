# PetKit Home Assistant Integration
![GitHub manifest version (path)](https://img.shields.io/github/manifest-json/v/RobertD502/home-assistant-petkit?filename=custom_components%2Fpetkit%2Fmanifest.json)

<a href="https://www.buymeacoffee.com/RobertD502" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="100" width="424"></a>

### A lot of work has been put into creating the backend and this integration. If you enjoy this integration, consider donating by clicking on the logo above.

***All proceeds go towards helping a local animal rescue.**

___

Custom Home Assistant component for controlling and monitoring PetKit devices and pets.

`Currently Supported Devices:`
- [Fresh Element Infinity](https://www.amazon.com/PETKIT-Automatic-Stainless-Programmable-Dispenser/dp/B09JFK8BCQ)
- [Fresh Element Solo](https://www.amazon.com/PETKIT-Automatic-Dispenser-Compatible-Freeze-Dried/dp/B09158J9PF/)
- [Fresh Element Mini Pro](https://www.amazon.com/PETKIT-Automatic-Stainless-Indicator-Dispenser-2-8L/dp/B08GS1CPHH/)
- [Eversweet 3 Pro Water Fountain](https://www.amazon.com/PETKIT-Wireless-Fountain-Stainless-Dispenser/dp/B09QRH6L3M/)
- [Pura X Litter Box](https://www.amazon.com/PETKIT-Self-Cleaning-Scooping-Automatic-Multiple/dp/B08T9CCP1M)



## **Prior To Installation**

- **This integration requires using your PetKit account `email` and `password`.**

- **If using another PetKit integration that uses the petkit domain, you will need to delete it prior to installing this integration.**

- **The current polling interval is set to 2 minutes. If you would like to set a different polling interval, change the `DEFAULT_SCAN_INTERVAL` in the constants.py file (in seconds).**

## Important - Please Read:
### Note About PetKit Account: 

PetKit accounts can only be logged in on one device at a time. Using this integration will result in getting signed out of the mobile app. You can avoid this by creating a secondary account and sharing devices from the main account **(except water fountains)**. However, some device functionality is lost when using a secondary account as well as not being able to share pets between accounts. **Therefore, you will get the most out of this integration by using your original account.**
### If you have a water fountain:

`Note #1:` Getting the most recent data from your water fountain, as well as controlling the water fountain, requires that the BLE relay is set up within the PetKit app. Otherwise, you will be limited to data that isn't up-to-date and no ability to control the water fountain as it requires another compatible PetKit device acting as a BLE relay.

`Note #2:` If you have the BLE relay set up, please be sure to follow these direction prior to using the integration:
- Sign out of the PetKit app and turn off bluetooth on your phone, tablet, etc.
- With bluetooth turned off, force close the PetKit app (be sure to do this on any device that was using your account with the PetKit app).
- Unplug all PetKit devices. Once all are off, you may plug them in again.
- With all devices powered back on, you can turn bluetooth back on (on your mobile device or tablet).
- Proceed with the installation and setup instructions for this integration.
> Although these steps may seem tedious, they are a necessary evil. The PetKit app will ping the bluetooth endpoints and initiate the relay even with your account signed out. The only way of giving the integration control/the ability to initiate the relay is to sever any bluetooth connection that the app has started.


### Using the PetKit app:
If you want to use the PetKit app momentarily to change some settings, be sure to disable the PetKit integration before logging into the app. If you don't, you will be asked to reauthenticate. Once you are done making changes within the app, re-enable the integration.
> If you needed the BLE relay while using the app (bluetooth turned on on your device), please be sure to follow the steps in `Note #2` above in order to sever the BLE relay connection started by the PetKit app.

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

Each PetKit device and pet is represented as a device in Home Assistant. Within each device
are several entities described below.


## Feeders
___

<details>
  <summary> <b>Fresh Element Infinity</b> (<i>click to expand</i>)</summary>
  <!---->

Each Feeder has the following entities:

| Entity                      | Entity Type     | Additional Comments                                                                                                                                                                                                                                                                                                                    |
|-----------------------------|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Call pet`                  | `Button`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                               |
| `Cancel manual feed`        | `Button`        | - Only available if your feeder is online (connected to PetKit's servers). <br/>- Will cancel a manual feeding that is currently in progress.                                                                                                                                                                                          |
| `Indicator light`           | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                               |
| `Manual Feed`               | `Number`        | - Only available if your feeder is online (connected to PetKit's servers). <br/>- Select the amount of food, in grams, you'd like to dispense immediately. <br/>- Note: valid amount ranges from 5-200 grams in increments of 1 gram.                                                                                                  |
| `Desiccant days remaining`  | `Sensor`        | Number of days left before the desiccant needs to be replaced.                                                                                                                                                                                                                                                                         |
| `Food level`                | `Binary Sensor` | Allows for determining if there is a food shortage.                                                                                                                                                                                                                                                                                    |
| `Child lock`                | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                               |
| `Do not disturb`            | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                                                               |
| `Reset desiccant`           | `Button`        | - Allows you to reset the desiccant back to 30 days after replacing it. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                |
| `Sound`                     | `Select`        | - Allows you to select which sound is played when calling your pet. <br/>- Default sound is selected if no self-recorded sounds are available or selected. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                             |
| `Surplus`                   | `Number`        | - Allows for selecting weight in bowl that is considered to be surplus. <br/>- If a surplus amount is selected and surplus control is enabled, planned feedings will stop when the weight of food detected in the bowl is equal to the surplus amount. <br/>- Only available if your feeder is online (connected to PetKit's servers). |
| `Surplus control`           | `Switch`        | - Enable or disable surplus control. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                                   |
| `System notification sound` | `Switch`        | - Enable or disable system notification sound. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                         |
| `Voice with dispense`       | `Switch`        | - Enable or disable sound (selected in Sound entity) to play with every feeding. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                       |
| `Volume`                    | `Number`        | - Allows for controlling feeder sound volume.  <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                                                                                                                                                                         |
| `Amount eaten`              | `Sensor`        | Amount of food your pet has eaten from the bowl today.                                                                                                                                                                                                                                                                                 |
| `Battery`                   | `Binary Sensor` | Indicates if your battery is charging or not charging.                                                                                                                                                                                                                                                                                 |
| `Battery status`            | `Sensor`        | - Will only become available when feeder is running on batteries. <br/>- Indicates the battery level (Normal or Low).                                                                                                                                                                                                                  |
| `Dispensed`                 | `Sensor`        | Amount of food, in grams, dispensed today.                                                                                                                                                                                                                                                                                             |
| `Error`                     | `Sensor`        | Identifies any errors reported by the feeder.                                                                                                                                                                                                                                                                                          |
| `Food in bowl`              | `Sensor`        | Amount of food, in grams, that is currently in the bowl.                                                                                                                                                                                                                                                                               |
| `Planned`                   | `Sensor`        | Amount of food, in grams, that the feeder plans to dispense today.                                                                                                                                                                                                                                                                     |
| `Planned dispensed`         | `Sensor`        | Of the planned amount that is to be dispensed today, amount of food (grams) that has been dispensed.                                                                                                                                                                                                                                   |
| `RSSI`                      | `Sensor`        | WiFi connection strength.                                                                                                                                                                                                                                                                                                              |
| `Status`                    | `Sensor`        | `Normal` = Feeder is connected to PetKit's servers <br/>`Offline` = Feeder is not connected to PetKit servers <br/>`On Batteries` = Feeder is currently being powered by the batteries.                                                                                                                                                |
| `Times dispensed`           | `Sensor`        | Number of times food has been dispensed today.                                                                                                                                                                                                                                                                                         |
| `Times eaten`               | `Sensor`        | Number of times pet ate today.                                                                                                                                                                                                                                                                                                         |
</details>

<details>
  <summary> <b>Fresh Element Solo</b> (<i>click to expand</i>)</summary>
  <!---->

Each Feeder has the following entities:

| Entity                      | Entity Type     | Additional Comments                                                                                                                                                                                   |
|-----------------------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Cancel manual feed`        | `Button`        | - Only available if your feeder is online (connected to PetKit's servers). <br/>- Will cancel a manual feeding that is currently in progress.                                                         |
| `Indicator light`           | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Manual feed`               | `Select`        | - Allows setting the amount of food to dispense immediately. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                          |
| `Desiccant days remaining`  | `Sensor`        | Number of days left before the desiccant needs to be replaced.                                                                                                                                        |
| `Food level`                | `Binary Sensor` | Allows for determining if there is a food shortage.                                                                                                                                                   |
| `Child lock`                | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Dispense tone`             | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Food shortage alarm`       | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Reset desiccant`           | `Button`        | - Allows you to reset the desiccant back to 30 days after replacing it. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                               |
| `Battery installed`         | `Binary Sensor` | If batteries are removed or installed, power cycling the feeder is required for the status to update.                                                                                                 |
| `Battery status`            | `Sensor`        | - Will only become available when feeder is running on batteries. <br/>- Indicates the battery level (Normal or Low).                                                                                 |
| `Dispensed`                 | `Sensor`        | Amount of food, in grams, dispensed today.                                                                                                                                                            |
| `Manually dispensed`        | `Sensor`        | Amount of food, in grams, manually dispensed today.                                                                                                                                                   |
| `Planned`                   | `Sensor`        | Amount of food, in grams, that the feeder plans to dispense today.                                                                                                                                    |
| `Planned dispensed`         | `Sensor`        | Of the planned amount that is to be dispensed today, amount of food (grams) that has been dispensed.                                                                                                  |
| `RSSI`                      | `Sensor`        | WiFi connection strength.                                                                                                                                                                             |
| `Status`                    | `Sensor`        | `Normal` = Feeder is connected to PetKit's servers <br/>`Offline` = Feeder is not connected to PetKit servers <br/>`On Batteries` = If installed, feeder is currently being powered by the batteries. |
| `Times dispensed`           | `Sensor`        | Number of times food has been dispensed today.                                                                                                                                                        |
</details>

<details>
  <summary> <b>Fresh Element Mini Pro</b> (<i>click to expand</i>)</summary>
  <!---->

Each Feeder has the following entities:

| Entity                      | Entity Type     | Additional Comments                                                                                                                                                                                   |
|-----------------------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Indicator light`           | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Manual feed`               | `Select`        | - Allows setting the amount of food to dispense immediately. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                          |
| `Desiccant days remaining`  | `Sensor`        | Number of days left before the desiccant needs to be replaced.                                                                                                                                        |
| `Food level`                | `Binary Sensor` | Allows for determining if there is a food shortage.                                                                                                                                                   |
| `Child lock`                | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Reset desiccant`           | `Button`        | - Allows you to reset the desiccant back to 30 days after replacing it. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                               |
| `Battery status`            | `Sensor`        | - Will only become available when feeder is running on batteries. <br/>- Indicates the battery level (Normal or Low).                                                                                 |
| `RSSI`                      | `Sensor`        | WiFi connection strength.                                                                                                                                                                             |
| `Status`                    | `Sensor`        | `Normal` = Feeder is connected to PetKit's servers <br/>`Offline` = Feeder is not connected to PetKit servers <br/>`On Batteries` = If installed, feeder is currently being powered by the batteries. |

> Friendly Note: Mini feeders have a bug when batteries are installed that has never been addressed by PetKit. This can result in your device locking up until the batteries are removed and feeder is power cycled. I am not sure what triggers this bug, but as a safety measure I don't install batteries into mini feeders.
</details>

## Water Fountains
___

<details>
  <summary> <b>Eversweet 3 Pro</b> (<i>click to expand</i>)</summary>
  <!---->

Each water fountain has the following entities:

| Entity                 | Entity Type     | Additional Comments                                                                                                                                                                                                                                                                                                                                                    |
|------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Do not disturb`       | `Switch`        | -`Only available if BLE relay is set up and main BLE relay device is online.` <br/>- Allows for enabling or disabling do not disturb - Use PetKit app to set do not disturb schedule if you plan on using this entity.                                                                                                                                                 |
| `Light`                | `Switch`        | `Only available if BLE relay is set up and main BLE relay device is online.`                                                                                                                                                                                                                                                                                           |
| `Power`                | `Switch`        | -`Only available if BLE relay is set up and main BLE relay device is online.` <br/>- Turning power off is equivalent to "Pause" in the PetKit app. <br/>- Turning power on resumes the water fountain in the mode (Normal/Smart) it was in prior to being powered off.                                                                                                 |
| `Filter`               | `Sensor`        | Indicates % filter life left.                                                                                                                                                                                                                                                                                                                                          |
| `Water level`          | `Binary Sensor` | Indicates if water needs to be added to the water fountain.                                                                                                                                                                                                                                                                                                            |
| `Light brightness`     | `Select`        | -`Only available if BLE relay is set up and main BLE relay device is online.` <br/>- Only available when light is turned on                                                                                                                                                                                                                                            |
| `Mode`                 | `Select`        | -`Only available if BLE relay is set up and main BLE relay device is online.` <br/>- Allows setting mode to Normal or Smart. <br/>- For "Smart mode", use the PetKit app to set the water on and off minutes.                                                                                                                                                          |
| `Reset filter`         | `Button`        | `Only available if BLE relay is set up and main BLE relay device is online.`                                                                                                                                                                                                                                                                                           |
| `Energy usage`         | `Sensor`        |                                                                                                                                                                                                                                                                                                                                                                        |
| `Last data update`     | `Sensor`        | - Date/Time that the water fountain last reported updated data to PetKit servers. <br/>- This can be used to track and identify if the BLE relay is working correctly as this will change whenever the main BLE relay device polls the water fountain. <br/>- If you have the BLE relay set up, this sensor is only concerning if it shows data was updated hours ago. |
| `Purified water today` | `Sensor`        | Number of times water has been purified.                                                                                                                                                                                                                                                                                                                               |


**Note About Water Fountain Control**


>  If you have the BLE relay set up in the PetKit app and the main BLE relay device is online, sometimes the bluetooth connection will fail when attempting to send a command (e.g., changing mode, light brightness, etc) . If this happens, it will be noted in the Home Assistant logs. Retrying the command usually results in a subsequent successful connection. 
</details>

## Litter Boxes
___

<details>
  <summary> <b>Pura X</b> (<i>click to expand</i>)</summary>
  <!---->

Each litter box has the following entities:

| Entity                 | Entity Type     | Additional Comments                                                                                                                                                                                                                      |
|------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Odor removal` | `Button` | - Activates immediate odor removal <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                                                                        |
| `Pause Cleaning` | `Button` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Power` | `Button` | - Turn litter box on/off <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                  |
| `Start/Resume cleaning` | `Button` | - Start a manual cleaning or resume a cleaning if litter box is currently paused. <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                         |
| `Average Use` | `Sensor` | Average use duration of the litter box today.                                                                                                                                                                                            |
| `Deodorizer` | `Binary Sensor` | Allows for determining if deodorizer needs to be refilled.                                                                                                                                                                               |
| `Last used by` | `Sensor` | Indicates which cat used the litter box last.                                                                                                                                                                                            |
| `Litter` | `Binary Sensor` | Allows for determining if the litter needs to be refilled.                                                                                                                                                                               |
| `Times used` | `Sensor` | Number of times litter box was used today.                                                                                                                                                                                               |
| `Total use` | `Sensor` | Total number of seconds litter box was used today.                                                                                                                                                                                       |
| `Waste bin` | `Binary Sensor` | Allows for determining if the waste bin is full.                                                                                                                                                                                         |
| `Auto cleaning` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Kitten Mode is turned on.                                                                                                              |
| `Auto odor removal` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Avoid repeat cleaning` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Kitten Mode is turned on.                                                           | 
| `Child lock`| `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Cleaning delay` | `Number` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Kitten Mode is turned on.                                                           |
| `Cleaning interval` | `Select` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Avoid repeat cleaning is disabled. <br/>- Not available if Kitten Mode is turned on. |
| `Display` | `Switch` | - Turn display on litter box on or off. <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                                                                   |
| `Do not disturb` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Kitten mode` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Light weight cleaning disabled` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Avoid repeat cleaning is disabled. <br/>- Not available if Kitten Mode is turned on. |
| `Litter type` | `Select` | Type of litter that is being used in the litter box.                                                                                                                                                                                     |
| `Periodic cleaning` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Kitten Mode is turned on.                                                                                                              |
| `Periodic odor removal` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Deodorizer level` | `Sensor` | Percent of deodorizer remaining.                                                                                                                                                                                                         |
| `Error` | `Sensor` | Any errors being reported by the litter box.                                                                                                                                                                                             |
| `Last event` | `Sensor` | - Last event that occured in the litter box. <br/>- sub_events attribute is used to list any events that are associated with the main event. <br/>- This sensor is used to mimic the timeline that is seen in the PetKit app.            |
| `Litter level` | `Sensor` | Percent of litter that is left in the litter box.                                                                                                                                                                                        |
| `Litter weight` | `Sensor` | - Weight of litter currently in litter box. <br/>- By default this is in Kg. The unit can be changed in the settings of this entity.                                                                                                     |
| `Manually paused` | `Binary Sensor` | Indicates if the litter box has been manually paused or not. Please see note below table for additional information.                                                                                                                     |
| `RSSI` | `Sensor` | WiFi connection strength.                                                                                                                                                                                                                |

> When manually pausing the litter box, the manually paused sensor entity will show a state of On. If cleaning isn't resumed, the litter box will (by default) resume cleaning after 10 minutes - the manually paused entity will return to a state of Off. If you manually pause a cleaning and restart Home Assistant while the litter box is paused, this sensor will have an incorrect state of Off. This is a limitation on PetKit's end as the state of the litter box is not reported by their servers. This behavior is evident when a cleaning is paused from the PetKit app, the app is force closed, and opened again. The goal of this entity is to be able to manually keep track of the state of the litter box since PetKit doesn't do that.
</details>

## Pets
___

<details>
  <summary> <b>Dog</b> (<i>click to expand</i>)</summary>
  <!---->

| Entity                 | Entity Type     | Additional Comments                                                                                                                                                                                                                      |
|------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Set weight` | `Number` | Set the weight of the dog. |

</details>

<details>
  <summary> <b>Cat</b> (<i>click to expand</i>)</summary>
  <!---->

| Entity                 | Entity Type                                                                                                                                                                                                                                                                                                                             | Additional Comments                                                                                                                                                                                                                                                                                                                      |
|------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Set weight` | `Number`                                                                                                                                                                                                                                                                                                                                | Set the weight of the cat.                                                                                                                                                                                                                                                                                                               |
| `Last use duration` | `Sensor`                                                                                                                                                                                                                                                                                                                                | - Amount of time spent in the litter box during last use today. <br/>- Only available if PetKit account has litter box(es). <br/>- If multiple litter boxes, this will display data obtained from the most recent litter box used.                                                                                                       |
| `Latest weight` | `Sensor` | - Most recent weight measurement obtained during last litter box use today. <br/>- Only available if PetKit account has litter box(es). <br/>- If multiple litter boxes, this will display data obtained from the most recent litter box used. <br/>- By default the unit used is Kg. Unit can be changed in the settings of the entity. |
</details>
