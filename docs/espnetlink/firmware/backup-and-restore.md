---
title: Backup and restore
---

# Backup and restore

<p class="lead">The whole configuration of the dongle is one JSON file: download it from the System page, keep it, upload it to the same dongle after a factory reset or to another dongle to clone it. A restore is all or nothing.</p>

## Download

==System== › ==Maintenance== › ==Download Config== saves `espnetlink-settings.json`. The file holds every settings component with its version and values, **including the passwords and keys** (the APN password, the SIM PIN, the WiFi passwords, the VPN keys): a backup that lost them could not bring back a working configuration. Keep the file private.

```text
curl -o espnetlink-settings.json http://192.168.7.1/api/settings/backup
```

The values are the ones that apply at the next start, so a change saved a moment ago is in the file even before the restart.

## Upload

==System== › ==Maintenance== › ==Upload Config==, pick the file. Every component in the file is checked first (a backup from an older firmware is migrated on the way); if anything is wrong, nothing is written and the page names the component and the reason. Otherwise the settings are stored and the dongle restarts once to apply them. Components the firmware does not know are skipped and listed; a backup from a newer firmware than the one running is refused with "update the firmware first".

What a restore does not carry: the files under `/data` (the certificate sets, the factory record), the firmware itself, and the one-time marker that the WiFi password was generated. A restored WiFi password is the one in the file.

```text
curl -X POST -H "Content-Type: application/json" --data-binary @espnetlink-settings.json http://192.168.7.1/api/settings/backup
```

## Cloning a dongle

A backup restored on another dongle gives it the same APN, PIN, WiFi, VPN and Home Assistant settings. Its device id, its mDNS name and its access point name stay its own (they come from its hardware), but the access point password from the file replaces the second dongle's generated one.

## The quick settings as text

`config list -j` on the console prints the carrier settings, the WiFi mode, the USB class and the GPS switches as one JSON line, handy to keep in a note; `config set` puts one of them back. See [Console](../tools/console.md).
