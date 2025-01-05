<h1 align="center">
  <a href="https://petkit.com"><img src="https://raw.githubusercontent.com/RobertD502/home-assistant-petkit/main/logo.png" width="480"></a>
  <br>
  <i>PetKit Home Assistant Integration</i>
  <br>
  <h3 align="center">
    <i> Custom Home Assistant component for controlling and monitoring PetKit devices and pets. </i>
    <br>
  </h3>
</h1>

<p align="center">
  <a href="https://github.com/RobertD502/home-assistant-petkit/releases"><img src="https://img.shields.io/github/v/release/RobertD502/home-assistant-petkit?display_name=tag&include_prereleases&sort=semver" alt="Current version"></a>
  <img alt="GitHub" src="https://img.shields.io/github/license/RobertD502/home-assistant-petkit">
  <img alt="GitHub manifest.json dynamic (path)" src="https://img.shields.io/github/manifest-json/requirements/RobertD502/home-assistant-petkit%2Fmain%2Fcustom_components%2Fpetkit?label=requirements">
  <img alt="Total lines count" src="https://tokei.rs/b1/github/RobertD502/home-assistant-petkit">
</p>

<p align="center">
  <a href="https://www.buymeacoffee.com/RobertD502" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="90" width="381.6"></a>
  <a href="https://liberapay.com/RobertD502/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg" height="90" width="270"></a>
</p>

### A lot of work has been put into creating the backend and this integration. If you enjoy this integration, consider donating by clicking on one of the supported methods above.

***All proceeds go towards helping a local animal rescue.**

___
## Discord Server
<a href="https://discord.gg/FXrmHaapf3"><img alt="Discord" src="http://invidget.switchblade.xyz/FXrmHaapf3"></a>

Join the Home Assistant PetKit discord server to follow development news or to share ideas with other users.

## Currently Supported Devices

`Feeders`
- [Fresh Element Infinity](https://www.amazon.com/PETKIT-Automatic-Stainless-Programmable-Dispenser/dp/B09JFK8BCQ)
- [Fresh Element Solo](https://www.amazon.com/PETKIT-Automatic-Dispenser-Compatible-Freeze-Dried/dp/B09158J9PF/)
- [Fresh Element Mini Pro](https://www.amazon.com/PETKIT-Automatic-Stainless-Indicator-Dispenser-2-8L/dp/B08GS1CPHH/)
- [Fresh Element Gemini](https://www.amazon.com/PETKIT-Automatic-Combination-Dispenser-Stainless/dp/B0BF56RTQH)
- [Fresh Element](https://petkit.us/products/petkit-element-wi-fi-enabled-smart-pet-food-container-feeder)
> [!CAUTION]
> YumShare feeders are **NOT** currently supported, but will be in the future. Once they are supported this message will be removed.

`Litter Boxes`
- [Pura X Litter Box](https://www.amazon.com/PETKIT-Self-Cleaning-Scooping-Automatic-Multiple/dp/B08T9CCP1M)
- [Pura MAX / MAX 2 Litter Box with/without Pura Air deodorizer](https://www.amazon.com/PETKIT-Self-Cleaning-Capacity-Multiple-Automatic/dp/B09KC7Q4YF)

`Purifiers`
- [Air Magicube](https://www.instachew.com/product-page/petkit-air-magicube-smart-odor-eliminator)

`Water Fountains`
- [Eversweet Solo 2 Water Fountain](https://www.amazon.com/PETKIT-EVERSWEET-Wireless-Visualization-Dispenser-2L/dp/B0B3RWF653)
- [Eversweet 3 Pro Water Fountain](https://www.amazon.com/PETKIT-Wireless-Fountain-Stainless-Dispenser/dp/B09QRH6L3M/)
- [Eversweet 3 Pro (UVC Version) Water Fountain](https://petkit.com/products/eversweet-3-pro-wireless-pump-uvc)
- [Eversweet 5 Mini Water Fountain](https://www.petkit.nl/products/eversweet-5-mini-binnen-2-weken-geleverd)



## **Prior To Installation**

- **This integration requires using your PetKit account `email` (`number` for PetKit China accounts) and `password`.** Third-party account sign-in methods (Facebook, Apple, Twitter) are **not supported**.

> [!CAUTION]
> **If using another PetKit integration that uses the petkit domain, you will need to delete it prior to installing this integration. You'll also need to remove any mention of it from your configuration.yaml file.**

> [!CAUTION]
> **If you are running Home Assistant as a Docker container, the `TZ` environment variable must be set.**


## Important - Please Read:
### PetKit Account & Family Sharing Feature:

> [!IMPORTANT]
> - PetKit accounts can only be logged in on one device at a time. Using a single account for both this integration and the mobile app will result in getting signed out of one of them. You can avoid this by creating a secondary account and sharing the devices/pets to it using the family sharing feature. You may use the primary account or the secondary account with this integration. However, as development was done using a primary account, if you use your secondary account with this integration, I cannot guarantee that all features work.   <br><br>


### If you have a water fountain:

> [!NOTE]
> Getting the most recent data from your water fountain, as well as controlling the water fountain, requires that the BLE relay is set up **within the PetKit app**. Otherwise, you will not be able to control the water fountain as it requires another compatible PetKit device acting as a BLE relay and data will only be as recent as the last time your phone connected to the water fountain.

> [!CAUTION]
> If you have a Pura MAX litter box acting as a BLE relay for your water fountain, you may want to disable the `Use PetKit BLE relay (if available)` option. A bug exists in the Pura Max firmware that causes the litter box to eventually become unresponsive and needing a reboot if both the integration and PetKit mobile app are in use.  

# Installation

## With HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=RobertD502&repository=home-assistant-petkit&category=integration)

> [!Tip]
> If you are unable to use the button above, manually search for PetKit in HACS.


## Manual
Copy the `petkit` directory, from `custom_components` in this repository,
and place it inside your Home Assistant Core installation's `custom_components` directory. Restart Home Assistant prior to moving on to the `Setup` section.

> [!WARNING]
> If installing manually, in order to be alerted about new releases, you will need to subscribe to releases from this repository.

# Setup

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=petkit)

> [!Tip]
> If you are unable to use the button above, follow the steps below:
> 1. Navigate to the Home Assistant Integrations page (Settings --> Devices & Services)
> 2. Click the `+ ADD INTEGRATION` button in the lower right-hand corner
> 3. Search for `PetKit`

> [!Caution]
> * Be sure to select the country associated with your account (Hong Kong users should select Hong Kong, not China).
> * During setup, set the timezone option to `Set Automatically`. If the tzlocal library isn't able to fetch your timezone, please manually select your timezone.

**The current polling interval is set to 2 minutes (120 seconds). If you would like to set a different polling interval, change the polling interval option (via the UI). Keep in mind, setting the polling interval too short may result in your account getting rate limited/blocked.**

# Devices

Each PetKit device and pet is represented as a device in Home Assistant. Within each device
are several entities described below.


## Feeders
___

<details>
  <summary> <b>Fresh Element Infinity</b> (<i>click to expand</i>)</summary>
  <!---->
<br/>
Each Feeder has the following entities:
<br/>

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
<br/>
Each Feeder has the following entities:
<br/>

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
| `Error`                     | `Sensor`        | Identifies any errors reported by the feeder.                                                                                                                                                                                                                                                                                          |
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
<br/>
Each Feeder has the following entities:
<br/>

| Entity                      | Entity Type     | Additional Comments                                                                                                                                                                                   |
|-----------------------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Indicator light`           | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Manual feed`               | `Select`        | - Allows setting the amount of food to dispense immediately. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                          |
| `Desiccant days remaining`  | `Sensor`        | Number of days left before the desiccant needs to be replaced.                                                                                                                                        |
| `Food level`                | `Binary Sensor` | Allows for determining if there is a food shortage.                                                                                                                                                   |
| `Child lock`                | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Reset desiccant`           | `Button`        | - Allows you to reset the desiccant back to 30 days after replacing it. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                               |
| `Battery status`            | `Sensor`        | - Will only become available when feeder is running on batteries. <br/>- Indicates the battery level (Normal or Low).                                                                                 |
| `Error`                     | `Sensor`        | Identifies any errors reported by the feeder.                                                                                                                                                                                                                                                                                          |
| `RSSI`                      | `Sensor`        | WiFi connection strength.                                                                                                                                                                             |
| `Status`                    | `Sensor`        | `Normal` = Feeder is connected to PetKit's servers <br/>`Offline` = Feeder is not connected to PetKit servers <br/>`On Batteries` = If installed, feeder is currently being powered by the batteries. |

> Friendly Note: Mini feeders have a bug when batteries are installed that has never been addressed by PetKit. This can result in your device locking up until the batteries are removed and feeder is power cycled. I am not sure what triggers this bug, but as a safety measure I don't install batteries into mini feeders.
</details>

<details>
  <summary> <b>Fresh Element Gemini</b> (<i>click to expand</i>)</summary>
  <!---->
<br/>
Each Feeder has the following entities:
<br/>

| Entity                      | Entity Type     | Additional Comments                                                                                                                                                                                   |
|-----------------------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Cancel manual feed`        | `Button`        | - Only available if your feeder is online (connected to PetKit's servers). <br/>- Will cancel a manual feeding that is currently in progress.                                                         |
| `Indicator light`           | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Manual feed`               | `Text`        | - Allows setting the amount of portions to dispense immediately from hopper 1 and 2. <br/>- Only available if your feeder is online (connected to PetKit's servers). <br/>- Valid text is in the form `number,number`. For example, setting a value of 1,2 will dispense one portion from hopper 1 and 2 portions from hopper 2. Allowed portion sizes for each hooper range from and include 0 to 10.                                                          |
| `Desiccant days remaining`  | `Sensor`        | Number of days left before the desiccant needs to be replaced.                                                                                                                                        |
| `Food level hopper 1`                | `Binary Sensor` | Allows for determining if there is a food shortage in hopper 1.                                                                                                                                                   |
| `Food level hopper 2`                | `Binary Sensor` | Allows for determining if there is a food shortage in hopper 2.                                                                                                                                                   |
| `Child lock`                | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Dispense tone`             | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Food replenished`             | `Button`        | Tells the PetKit servers that you have replenished hopper 1 and 2 with food. If you don't do this after replenishing food, the food level for hoppers 1 and 2 won't update until a manual feeding is sent or until the next scheduled feeding.                                                                                                                              |
| `Food shortage alarm`       | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Minimum eating duration`       | `Number`        | Minimum amount of time, in seconds, pet has to eat food before it is recorded.                                                                                                                              |
| `Reset desiccant`           | `Button`        | - Allows you to reset the desiccant back to 30 days after replacing it. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                               |
| `Average eating time`           | `Sensor`        | Average amount of time pet(s) have spent eating food.                                               |
| `Battery installed`         | `Binary Sensor` | If batteries are removed or installed, power cycling the feeder is required for the status to update.                                                                                                 |
| `Battery status`            | `Sensor`        | - Will only become available when feeder is running on batteries. <br/>- Indicates the battery level (Normal or Low).                                                                                 |
| `Dispensed hopper 1`                 | `Sensor`        | Amount of portions dispensed from hopper 1 today.                                                                                                                                                            |
| `Dispensed hopper 2`                 | `Sensor`        | Amount of portions dispensed from hopper 2 today.                                                                                                                                                            |
| `Error`                     | `Sensor`        | Identifies any errors reported by the feeder.                                                                                                                                                                                                                                                                                          |
| `Manually dispensed hopper 1`        | `Sensor`        | Amount of portions manually dispensed from hopper 1 today.                                                                                                                                                   |
| `Manually dispensed hopper 2`        | `Sensor`        | Amount of portions manually dispensed from hopper 2 today.                                                                                                                                                   |
| `Planned dispensed hopper 1`         | `Sensor`        | Of the planned amount that is to be dispensed today, amount of portions that have been dispensed from hopper 1.                                                                                                  |
| `Planned dispensed hopper 2`         | `Sensor`        | Of the planned amount that is to be dispensed today, amount of portions that have been dispensed from hopper 2.                                                                                                  |
| `Planned hopper 1`                   | `Sensor`        | Amount of portions that the feeder plans to dispense from hopper 1 today.                                                                                                                                    |
| `Planned hopper 2`                   | `Sensor`        | Amount of portions that the feeder plans to dispense from hopper 2 today.                                                                                                                                    |
| `RSSI`                      | `Sensor`        | WiFi connection strength.                                                                                                                                                                             |
| `Status`                    | `Sensor`        | `Normal` = Feeder is connected to PetKit's servers <br/>`Offline` = Feeder is not connected to PetKit servers <br/>`On Batteries` = If installed, feeder is currently being powered by the batteries. |
| `Times dispensed`           | `Sensor`        | Number of times food has been dispensed today.                                                                                                                                                        |
| `Times eaten`           | `Sensor`        | Number of times pet(s) ate today.                                                                                                                                                        |

</details>


<details>
  <summary> <b>Fresh Element</b> (<i>click to expand</i>)</summary>
  <!---->
<br/>
Each Feeder has the following entities:
<br/>

| Entity                     | Entity Type     | Additional Comments                                                                                                                                                                                   |
|----------------------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Cancel manual feed`       | `Button`        | - Only available if your feeder is online (connected to PetKit's servers). <br/>- Will cancel a manual feeding that is currently in progress.                                                         |
| `Indicator light`          | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Manual feed`              | `Number`        | - Allows setting the amount of food (grams) to dispense immediately. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                                  |
| `Desiccant days remaining` | `Sensor`        | Number of days left before the desiccant needs to be replaced.                                                                                                                                        |
| `Food level`               | `Binary Sensor` | Allows for determining if there is a food shortage.                                                                                                                                                   |
| `Child lock`               | `Switch`        | Only available if your feeder is online (connected to PetKit's servers).                                                                                                                              |
| `Reset desiccant`          | `Button`        | - Allows you to reset the desiccant back to 30 days after replacing it. <br/>- Only available if your feeder is online (connected to PetKit's servers).                                               |
| `Start calibration`        | `Button`        | See note at the bottom of the table for description provided by PetKit.                                                                                                                               |
| `Stop calibration`         | `Button`        |                                                                                                                                                                                                       |
| `Battery status`           | `Sensor`        | - Will only become available when feeder is running on batteries. <br/>- Indicates the battery level (Normal or Low).                                                                                 |
| `Error`                    | `Sensor`        | Identifies any errors reported by the feeder.                                                                                                                                                         |
| `Food Left`                | `Sensor`        | Identifies the amount of food, as a percentage, left in the feeder.                                                                                                                                   |
| `RSSI`                     | `Sensor`        | WiFi connection strength.                                                                                                                                                                             |
| `Status`                   | `Sensor`        | `Normal` = Feeder is connected to PetKit's servers <br/>`Offline` = Feeder is not connected to PetKit servers <br/>`On Batteries` = If installed, feeder is currently being powered by the batteries. |

> Feeder Calibration: Calibration is required after every installation and removal of batteries from the feeder. Prior to calibration, be sure to clean out all of the food from the feeder as the calibration process will empty any food that is left in the feeder.

</details>


## Water Fountains
___

<details>
  <summary> <b>Eversweet 3 Pro/5 Mini/Solo 2</b> (<i>click to expand</i>)</summary>
  <!---->
<br/>
Each water fountain has the following entities:
<br/>

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
<br/>
Each litter box has the following entities:
<br/>

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
| `Last event` | `Sensor` | - Last event that occured in the litter box. <br/>- sub_events attribute is used to list any events that are associated with the main event. <br/>- This sensor is used to mimic the timeline that is seen in the PetKit app. <br/>- Please see "Last event states" section below         |
| `Litter level` | `Sensor` | Percent of litter that is left in the litter box.                                                                                                                                                                                        |
| `Litter weight` | `Sensor` | - Weight of litter currently in litter box. <br/>- By default this is in Kg. The unit can be changed in the settings of this entity.                                                                                                     |
| `Manually paused` | `Binary Sensor` | Indicates if the litter box has been manually paused or not. Please see note below table for additional information.                                                                                                                     |
| `RSSI` | `Sensor` | WiFi connection strength.                                                                                                                                                                                                                |

> When manually pausing the litter box, the manually paused sensor entity will show a state of On. If cleaning isn't resumed, the litter box will (by default) resume cleaning after 10 minutes - the manually paused entity will return to a state of Off. If you manually pause a cleaning and restart Home Assistant while the litter box is paused, this sensor will have an incorrect state of Off. This is a limitation on PetKit's end as the state of the litter box is not reported by their servers. This behavior is evident when a cleaning is paused from the PetKit app, the app is force closed, and opened again. The goal of this entity is to be able to manually keep track of the state of the litter box since PetKit doesn't do that.
  <details>
    <summary> <b>Last event states</b> (<i>click to expand</i>)</summary>
    <!---->
  <br/>
  The following are all possible event/sub event states and their full descriptions:
  <br/>
  
| Event/Sub event state                 | Full Description                                                                                        |
|-------------------------------------|------------------------------------------------------------------------------------------------------|
| no_events_yet                       | No events yet                                                                                        |
| event_type_unknown                  | Event type unknown                                                                                   |
| cleaning_completed                  | Cleaning completed                                                                                   |
| dumping_over                        | Dumping Over                                                                                         |
| reset_over                          | Reset over                                                                                           |
| spray_over                          | Spray over                                                                                           |
| pet_out                             | Pet out                                                                                              |
| auto_cleaning_completed             | Auto cleaning completed                                                                              |
| periodic_cleaning_completed         | Periodic cleaning completed                                                                          |
| manual_cleaning_completed           | Manual cleaning completed                                                                            |
| auto_cleaning_terminated            | Automatic cleaning terminated                                                                        |
| periodic_cleaning_terminated        | Periodic cleaning terminated                                                                         |
| manual_cleaning_terminated          | Manual cleaning terminated                                                                           |
| auto_cleaning_failed_full           | Automatic cleaning failed, waste collection bin is full, please empty promptly                       |
| auto_cleaning_failed_hall_l         | Automatic cleaning failure, the cylinder is not properly locked in place, please check               |
| auto_cleaning_failed_hall_t         | Automatic cleaning failure, the litter box's upper cupper cover is not placed properly, please check |
| scheduled_cleaning_failed_full      | Scheduled cleaning failed, waste collection bin is full, please empty promptly                       |
| scheduled_cleaning_failed_hall_l    | Scheduled cleaning failure, the cylinder is not properly locked in place, please check               |
| scheduled_cleaning_failed_hall_t    | Scheduled cleaning failure, the litter box's upper cupper cover is not placed properly, please check |
| manual_cleaning_failed_full         | Manual cleaning failed, waste collection bin is full, please empty promptly                          |
| manual_cleaning_failed_hall_l       | Manual cleaning failure, the cylinder is not properly locked in place, please check                  |
| manual_cleaning_failed_hall_t       | Manual cleaning failure, the litter box's upper cupper cover is not placed properly, please check    |
| auto_cleaning_canceled              | Automatic cleaning canceled, device in operation                                                     |
| periodic_cleaning_canceled          | Periodic cleaning canceled, device in operation                                                      |
| manual_cleaning_canceled            | Manual cleaning canceled, device in operation                                                        |
| auto_cleaning_canceled_kitten       | Kitten mode is enabled, auto cleaning is canceled                                                    |
| periodic_cleaning_canceled_kitten   | Kitten mode is enabled, periodically cleaning is canceled                                            |
| litter_empty_completed              | Cat litter empty completed                                                                           |
| litter_empty_terminated             | Cat litter empty terminated                                                                          |
| litter_empty_failed_full            | Cat litter empty failed, waste collection bin is full, please empty promptly                         |
| litter_empty_failed_hall_l          | Cat litter empty failure, the cylinder is not properly locked in place, please check                 |
| litter_empty_failed_hall_t          | Cat litter empty failure, the litter box's cupper cover is not placed properly, please check         |
| reset_completed                     | Device reset completed                                                                               |
| reset_terminated                    | Device reset terminated                                                                              |
| reset_failed_full                   | Device reset failed, waste collection bin is full, please empty promptly                             |
| reset_failed_hall_l                 | Device reset failure, the cylinder is not properly locked in place, please check                     |
| reset_failed_hall_t                 | Device reset failure, the litter box's cupper cover is not placed properly, please check             |
| deodorant_finished                  | Deodorant finished                                                                                   |
| periodic_odor_completed             | Periodic odor removal completed                                                                      |
| manual_odor_completed               | Manual odor removal completed                                                                        |
| deodorant_finished_liquid_lack      | Deodorant finished, not enough purifying liquid, please refill in time                               |
| periodic_odor_completed_liquid_lack | Periodic odor removal completed, not enough purifying liquid, please refill in time                  |
| manual_odor_completed_liquid_lack   | Manual odor removal completed, not enough purifying liquid, please refill in time                    |
| auto_odor_failed                    | Automatic odor removal failed, odor eliminator error                                                 |
| periodic_odor_failed                | Periodic odor removal failure, odor eliminator malfunction                                           |
| manual_odor_failed                  | Manual odor removal failure, odor eliminator malfunction                                             |
| no_sub_events                       | No associated sub events                                                                             |


  </details>
</details>

<details>
  <summary> <b>Pura MAX</b> (<i>click to expand</i>)</summary>
  <!---->
<br/>
Each litter box has the following entities:
<br/>

| Entity                 | Entity Type     | Additional Comments                                                                                                                                                                                                                      |
|------------------------|-----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Dump litter` | `Button` | <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                                                                        |
| `Exit maintenance mode` | `Button` | <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                                                                        |
| `Odor removal` | `Button` | - Activates immediate odor removal <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                                                                        |
| `Pause cleaning` | `Button` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Pause exiting maintenance mode` | `Button` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Pause litter dumping` | `Button` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Power` | `Button` | - Turn litter box on/off <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                  |
| `Reset N50 odor eliminator` | `Button` |                                                                                                                                   |
| `Reset Pura Air liquid` | `Button` | Only available if litter box has a Pura Air associated with it                                                                                                                                |
| `Resume exiting maintenance mode` | `Button` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Resume litter dumping` | `Button` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Start maintenance mode` | `Button` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Start/Resume cleaning` | `Button` | - Start a manual cleaning or resume a cleaning if litter box is currently paused. <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                         |
| `Turn light ON` | `Button` | Only available if litter box has a Pura Air associated with it.                                                                         |
| `Average Use` | `Sensor` | Average use duration of the litter box today.                                                                                                                                                                                            |
| `Last used by` | `Sensor` | Indicates which cat used the litter box last.                                                                                                                                                                                            |
| `Litter` | `Binary Sensor` | Allows for determining if the litter needs to be refilled.                                                                                                                                                                               |
| `Pura Air liquid` | `Binary Sensor` | - Allows for determining if the Pura Air liquid needs to be refilled. <br/>- Only available if litter box has a Pura Air associated with it                                                                                        |
| `Times used` | `Sensor` | Number of times litter box was used today.                                                                                                                                                                                               |
| `Total use` | `Sensor` | Total number of seconds litter box was used today.                                                                                                                                                                                       |
| `Waste bin` | `Binary Sensor` | Allows for determining if the waste bin is full.                                                                                                                                                                                         |
| `Auto cleaning` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Kitten Mode is turned on.                                                                                                              |
| `Auto odor removal` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Avoid repeat cleaning` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Kitten Mode is turned on.                                                           |
| `Child lock`| `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Cleaning delay` | `Number` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Kitten Mode is turned on.                                                           |
| `Cleaning interval` | `Select` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Avoid repeat cleaning is disabled. <br/>- Not available if Kitten Mode is turned on. |
| `Continuous rotation` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). |
| `Deep cleaning` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Avoid repeat cleaning is disabled. <br/>- Not available if Kitten Mode is turned on. |
| `Deep deodorization` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers) and has a Pura Air associated with it. <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Avoid repeat cleaning is disabled. <br/>- Not available if Kitten Mode is turned on. |
| `Display` | `Switch` | - Turn display on litter box on or off. <br/>- Only available if litter box is online (Connected to PetKit's servers).                                                                                                                   |
| `Do not disturb` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Enhanced adsorption` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Kitten mode` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Light weight cleaning disabled` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Auto Cleaning is disabled. <br/>- Not available if Avoid repeat cleaning is disabled. <br/>- Not available if Kitten Mode is turned on. |
| `Litter type` | `Select` | Type of litter that is being used in the litter box.                                                                                                                                                                                     |
| `Periodic cleaning` | `Switch` | - Only available if litter box is online (Connected to PetKit's servers). <br/>- Not available if Kitten Mode is turned on.                                                                                                              |
| `Periodic odor removal` | `Switch` | Only available if litter box is online (Connected to PetKit's servers).                                                                                                                                                                  |
| `Error` | `Sensor` | Any errors being reported by the litter box.                                                                                                                                                                                             |
| `Last event` | `Sensor` | - Last event that occured in the litter box. <br/>- sub_events attribute is used to list any events that are associated with the main event. <br/>- This sensor is used to mimic the timeline that is seen in the PetKit app. <br/>- Please see "Last event states" section below         |
| `Litter level` | `Sensor` | Percent of litter that is left in the litter box.                                                                                                                                                                                        |
| `Litter weight` | `Sensor` | - Weight of litter currently in litter box. <br/>- By default this is in Kg. The unit can be changed in the settings of this entity.                                                                                                     |
| `N50 odor eliminator` | `Sensor` | - Amount of days left before N50 filter needs to be replaced.                                                                                                     |
| `Pura Air battery` | `Sensor` | - Only available if litter box has a Pura Air associated with it                                                                                                     |
| `Pura Air liquid` | `Sensor` | - Only available if litter box has a Pura Air associated with it. <br/>- Amount of liquid left in the Pura Air                                                                                                     |
| `RSSI` | `Sensor` | WiFi connection strength.                                                                                                                                                                                                                |
| `State` | `Sensor` | - Current work state of the litter box. <br/>- Please see "State entity states" section below.                                                                                                                                                                                                 |

  
  <details>
    <summary> <b>Last event states</b> (<i>click to expand</i>)</summary>
    <!---->
  <br/>
  The following are all possible event/sub event states and their full descriptions:
  <br/>

| Event/Sub event state                | Full Description                                                                                     |
|------------------------------------- |------------------------------------------------------------------------------------------------------|
| no_events_yet                        | No events yet                                                                                        |
| event_type_unknown                   | Event type unknown                                                                                   |
| cleaning_completed                   | Cleaning completed                                                                                   |
| dumping_over                         | Dumping Over                                                                                         |
| reset_over                           | Reset over                                                                                           |
| spray_over                           | Spray over                                                                                           |
| light_over                           | Light over                                                                                           |
| pet_out                              | Pet out                                                                                              |
| auto_cleaning_completed              | Auto cleaning completed                                                                              |
| periodic_cleaning_completed          | Periodic cleaning completed                                                                          |
| manual_cleaning_completed            | Manual cleaning completed                                                                            |
| auto_cleaning_terminated             | Automatic cleaning terminated                                                                        |
| periodic_cleaning_terminated         | Periodic cleaning terminated                                                                         |
| manual_cleaning_terminated           | Manual cleaning terminated                                                                           |
| auto_cleaning_failed_full            | Automatic cleaning failed, waste collection bin is full, please empty promptly                       |
| auto_cleaning_failed_hall_t          | Automatic cleaning failure, the litter box's upper cupper cover is not placed properly, please check |
| auto_cleaning_failed_falldown        | Automatic cleaning failure, the litter box has been knocked down, please check.                      |
| auto_cleaning_failed_other           | Automatic cleaning failure, device malfunction, please check.                                        |
| scheduled_cleaning_failed_full       | Scheduled cleaning failed, waste collection bin is full, please empty promptly                       |
| scheduled_cleaning_failed_hall_t     | Scheduled cleaning failure, the litter box's upper cupper cover is not placed properly, please check |
| scheduled_cleaning_failed_falldown   | Scheduled cleaning failure, the litter box has been knocked down, please check.                      |
| scheduled_cleaning_failed_other      | Scheduled cleaning failure, device malfunction, please check.                                        |
| manual_cleaning_failed_full          | Manual cleaning failed, waste collection bin is full, please empty promptly                          |
| manual_cleaning_failed_hall_t        | Manual cleaning failure, the litter box's upper cupper cover is not placed properly, please check    |
| manual_cleaning_failed_falldown      | Manual cleaning failure, the litter box has been knocked down, please check.                         |
| manual_cleaning_failed_other         | Manual cleaning failure, device malfunction, please check.                                           |
| auto_cleaning_canceled               | Automatic cleaning canceled, device in operation                                                     |
| periodic_cleaning_canceled           | Periodic cleaning canceled, device in operation                                                      |
| manual_cleaning_canceled             | Manual cleaning canceled, device in operation                                                        |
| auto_cleaning_failed_maintenance     | Automatic cleaning failed, the device is in maintenance mode                                         |
| periodic_cleaning_failed_maintenance | Periodically cleaning failed, the device is in maintenance mode                                      |
| auto_cleaning_canceled_kitten        | Kitten mode is enabled, auto cleaning is canceled                                                    |
| periodic_cleaning_canceled_kitten    | Kitten mode is enabled, periodically cleaning is canceled                                            |
| litter_empty_completed               | Cat litter empty completed                                                                           |
| litter_empty_terminated              | Cat litter empty terminated                                                                          |
| litter_empty_failed_full             | Cat litter empty failed, waste collection bin is full, please empty promptly                         |
| litter_empty_failed_hall_t           | Cat litter empty failure, the litter box's cupper cover is not placed properly, please check         |
| litter_empty_failed_falldown         | Cat litter empty failure, the litter box has been knocked down, please check                         |
| litter_empty_failed_other            | Cat litter empty failure, device malfunction, please check.                                          |
| reset_completed                      | Device reset completed                                                                               |
| reset_terminated                     | Device reset terminated                                                                              |
| reset_failed_full                    | Device reset failed, waste collection bin is full, please empty promptly                             |
| reset_failed_hall_t                  | Device reset failure, the litter box's cupper cover is not placed properly, please check             |
| reset_failed_falldown                | Device reset failure, the litter box has been knocked down, please check.                            |
| reset_failed_other                   | Device reset failure, device malfunction, please check.                                              |
| maintenance_mode                     | Maintenance mode                                                                                     |
| deodorant_finished                   | Deodorant finished                                                                                   |
| periodic_odor_completed              | Periodic odor removal completed                                                                      |
| manual_odor_completed                | Manual odor removal completed                                                                        |
| auto_odor_terminated                 | Automatic odor removal has been terminated.                                                          |
| periodic_odor_terminated             | Periodic odor removal terminated.                                                                    |
| manual_odor_terminated               | Manual odor removal terminated.                                                                      |
| auto_odor_failed                     | Automatic odor removal failed, odor eliminator error                                                 |
| periodic_odor_failed                 | Periodic odor removal failure, odor eliminator malfunction                                           |
| manual_odor_failed                   | Manual odor removal failure, odor eliminator malfunction                                             |
| auto_odor_canceled                   | Automatic odor removal has been canceled, the device is running.                                     |
| periodic_odor_canceled               | Periodic odor removal canceled. Litter Box is working.                                               |
| manual_odor_canceled                 | Manual odor removal canceled. Litter Box is working.                                                 |
| auto_odor_failed_device              | Automatic odor removal failed, no smart spray is connected.                                          |
| periodic_odor_failed_device          | Periodic odor removal failed. Odor Removal Device disconnected.                                      |
| manual_odor_failed_device            | Manual odor removal failed. Odor Removal Device disconnected.                                        |
| auto_odor_failed_batt                | Automatic odor removal failed, please confirm that the battery of smart spray is sufficient.         |
| periodic_odor_failed_batt            | Periodic odor removal failed. Please make sure the Odor Removal Device has sufficient battery.       |
| manual_odor_failed_batt              | Manual odor removal failed. Please make sure the Odor Removal Device has sufficient battery.         |
| auto_odor_failed_low_batt            | Automatic odor removal failed, battery is low.                                                       |
| periodic_odor_failed_low_batt        | Periodic odor removal failed. Odor Removal Device battery low.                                       |
| manual_odor_failed_low_batt          | Manual odor removal failed. Odor Removal Device battery low.                                         |
| cat_stopped_odor                     | Your cat is using the litter box, deodorization has been canceled                                    |
| light_on                             | The light is ON                                                                                      |
| light_already_on                     | The light is on. There is no need to turn on again.                                                  |
| light_malfunc                        | Failing to turn on the light. Device malfunction, please check.                                      |
| light_no_device                      | Failing to turn on the light. Please bind the odor removal device first.                             |
| light_batt_cap                       | Failing to turn on the light. Please check the battery capacity of the odor removal device.          |
| light_low_batt                       | Failing to turn on the light. Low battery capacity of odor removal device.                           |
| no_sub_events                        | No associated sub events                                                                             |

  </details>

  <details>
    <summary> <b>State entity states</b> (<i>click to expand</i>)</summary>
    <!---->
  <br/>
  The following are all possible State entity states and their full descriptions:
  <br/>

| State                                | Full Description                                                                                                                                     |
|------------------------------------- |------------------------------------------------------------------------------------------------------------------------------------------------------|    
| cleaning_litter_box                  | Cleaning litter box                                                                                                                                  |
| cleaning_litter_box_paused           | Litter box cleaning paused                                                                                                                           |
| cleaning_paused_pet_entered          | Litter box cleaning paused: Pet entered while in operation, anti-pinch sensors activated, device stopped working. Please check the device ASAP.      |
| cleaning_paused_system_error         | Litter box cleaning paused: System error, operation paused                                                                                           |
| cleaning_paused_pet_approach         | Litter box cleaning paused: Your cat is approaching, operation paused                                                                                |
| cleaning_paused_pet_using            | Litter box cleaning paused: Your cat is using the device, operation paused                                                                           |
| resetting_device                     | Resetting device                                                                                                                                     |
| litter_box_paused                    | Litter box paused                                                                                                                                    |
| paused_pet_entered                   | Litter box paused: Pet entered while in operation, anti-pinch sensors activated, device stopped working. Please check the device ASAP.               |
| paused_system_error                  | Litter box paused: System error, operation paused                                                                                                    |
| paused_pet_approach                  | Litter box paused: Your cat is approaching, operation paused                                                                                         |
| paused_pet_using                     | Litter box paused: Your cat is using the device, operation paused                                                                                    |
| dumping_litter                       | Dumping cat litter                                                                                                                                   |
| dumping_litter_paused                | Dumping cat litter paused                                                                                                                            |
| dumping_paused_pet_entered           | Dumping cat litter paused: Pet entered while in operation, anti-pinch sensors activated, device stopped working. Please check the device ASAP.       |
| dumping_paused_system_error          | Dumping cat litter paused: System error, operation paused                                                                                            |
| dumping_paused_pet_approach          | Dumping cat litter paused: Your cat is approaching, operation paused                                                                                 |
| dumping_paused_pet_using             | Dumping cat litter paused: Your cat is using the device, operation paused                                                                            |
| resetting                            | Resetting                                                                                                                                            |
| leveling                             | Leveling cat litter, please wait.                                                                                                                    |
| calibrating                          | Calibrating litter box, please wait.                                                                                                                 |
| maintenance_mode                     | In maintenance mode                                                                                                                                  |
| maintenance_paused_pet_entered       | Maintenance mode paused: Pet entered while in operation, anti-pinch sensors activated, device stopped working. Please check the device ASAP.         |
| maintenance_paused_cover             | Maintenance mode paused: The top cover is not installed, operation paused                                                                            |
| maintenance_paused_system_error      | Maintenance mode paused: System error, operation paused                                                                                              |
| maintenance_paused_pet_approach      | Maintenance mode paused: Your cat is approaching, operation paused                                                                                   |
| maintenance_paused_pet_using         | Maintenance mode paused: Your cat is using the device, operation paused                                                                              |
| maintenance_paused                   | Maintenance mode paused                                                                                                                              |
| exit_maintenance                     | Exiting maintenance mode                                                                                                                             |
| maintenance_exit_paused_pet_entered  | Maintenance mode exiting paused: Pet entered while in operation, anti-pinch sensors activated, device stopped working. Please check the device ASAP. |
| maintenance_exit_paused_cover        | Maintenance mode exiting paused: The top cover is not installed, operation paused                                                                    |
| maintenance_exit_paused_system_error | Maintenance mode exiting paused: System error, operation paused                                                                                      |
| maintenance_exit_paused_pet_approach | Maintenance mode exiting paused: Your cat is approaching, operation paused                                                                           |
| maintenance_exit_paused_pet_using    | Maintenance mode exiting paused: Your cat is using the device, operation paused                                                                      |
| maintenance_exit_paused              | Maintenance mode exiting paused                                                                                                                      |
| idle                                 | Idle                                                                                                                                                 |

  </details>    
</details>

## Purifiers
___

<details>
  <summary> <b>Air Magicube</b> (<i>click to expand</i>)</summary>
  <!---->
<br/>
Each purifier has the following entities:
<br/>

| Entity            | Entity Type | Additional Comments                                                                                                                                                                                                   |
|-------------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `Indicator light` | `Switch`    | Only available if your purifier is online (connected to PetKit's servers)                                                                                                                                             |
| `Prompt tone`     | `Switch`    | Only available if your purifier is online (connected to PetKit's servers).                                                                                                                                            |
| `Purifier`        | `Fan`       | - Only available if purifier is online (Connected to PetKit's servers). <br/>- Can turn the purifier `On` and `Off` and view/change the current mode to one of the following: `auto`, `silent`, `standard`, `strong`. |
| `Air purified`    | `Sensor`    |                                                                                                                                                                                                                       |
| `Humidity`        | `Sensor`    |                                                                                                                                                                                                                       |
| `Temperature`     | `Sensor`    |                                                                                                                                                                                                                       |
| `Error`           | `Sensor`    | Displays any error messages. `Note:` Even though it isn't really an error, An error message is displayed by PetKit if the purifier is in standby mode.                                                                |
| `Liquid`          | `Sensor`    | Percent of purifying liquid that remains in the purifier.                                                                                                                                                             |
| `RSSI`            | `Sensor`    | WiFi connection strength.                                                                                                                                                                                             |

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
| `Last use duration` | `Sensor`                                                                                                                                                                                                                                                                                                                                | - Amount of time spent in the litter box during last use. <br/>- Only available if PetKit account has litter box(es). <br/>- If multiple litter boxes, this will display data obtained from the most recent litter box used. <br/>- Will read 0 after first time setup if pet hasn't used litter box that day.                                                                                                      |
| `Latest weight` | `Sensor` | - Most recent weight measurement obtained during last litter box use. <br/>- Only available if PetKit account has litter box(es). <br/>- If multiple litter boxes, this will display data obtained from the most recent litter box used. <br/>- By default the unit used is Kg. Unit can be changed in the settings of the entity. <br/>- Will read 0 after first time setup if pet hasn't used litter box that day. |
</details>

# Help With Translations

A simple way of contributing to this integration is by helping translate the entity names and states to other languages.
<br/>
<br/>**If you speak another language, and would like to help:**
1. Inside of `custom_components/petkit/translations`, you will find two files: `en.json` and `hr.json`.
2. Create a new file and title it based on the [639-1 language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) you are creating a translation for in the format `<language_code>.json`.
3. Copy the contents from the `en.json` file to your newly created file.
4. If you are unsure what needs to be translated from english to the target language, compare the `en.json` file to the `hr.json` to see what was translated.
5. Create a PR with your new language file placed in the `translations` directory.
