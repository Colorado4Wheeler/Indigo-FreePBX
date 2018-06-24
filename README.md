![](https://github.com/Colorado4Wheeler/WikiDocs/blob/master/FreePBX/freepbx-logo-250.png)

# FreePBX

This plugin for the [Indigo Domotics](http://www.indigodomo.com/) home automation platform that interacts with your [FreePBX](http://www.freepbx.org/) telephone system to allow you to control your PBX and extensions via Indigo.

## Requirements

You must install the RestAPI module from the FreePBX modules admin and enable the module for this plugin to work.

## Basic Instructions

Once the RestAPI module is installed, open it to get the Token and Token Key, then create a PBX Server device in Indigo with this information and the IP address of your PBX.  Once complete you can create PBX Extension devices in Indigo for each extension you wish to control and use Indigo Actions to manipulate the extensions

## BETA Product

This is currently in beta, there is a lot planned for this if there is interest, currently this supports:

* Do Not Disturb (Enabling/disabling for any extension, showing status)
* Call Forwarding (Enabling/disabling for any extension, showing status)
* Call Waiting (Showing status)
* Call Flow - aka Day/Night ((Enabling/disabling any flow, showing status)
