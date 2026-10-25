---
title: Home Assistant
---

# Home Assistant

<p class="lead">The dongle speaks the same Home Assistant contract as the WiCAN family: it announces itself by mDNS, the MeatPi integration registers its webhook, and the dongle pushes its position and status on a timer. In a car with a WiCAN PRO you do not need this page; the WiCAN already forwards the dongle's position as its `gps_*` parameters. This link is for a dongle used on its own.</p>

<dl class="facts" markdown>
<dt>Discovery</dt><dd>mDNS service `_meatpi._tcp` with `device_type` `espnetlink`, name `espnetlink_<device id>.local`</dd>
<dt>Registration</dt><dd>The integration posts its webhook URL to the dongle; nothing to type</dd>
<dt>What it sends</dt><dd>The device identity and status, and the position while it has a fix</dd>
<dt>Interval</dt><dd>60 s by default, 1 to 3600 s; only changes unless you ask for everything</dd>
</dl>

## Set it up

<div class="steps" markdown>

1.  **Put the dongle on a network Home Assistant can reach.** Join your home WiFi in station mode ([WiFi](../connectivity/wifi.md)) with the network marked trusted, or run a VPN that Home Assistant sits on ([VPN](../connectivity/vpn.md)). The mobile network alone is not enough for the registration: the integration must reach the dongle once.

2.  **Add the device in Home Assistant.** With the MeatPi (WiCAN) integration installed, Home Assistant discovers `espnetlink_<id>` by mDNS and offers it under ==Settings== › ==Devices & services==. Adding it registers the integration's webhook URL on the dongle.

3.  **Check the dongle's Home Assistant card.** ==Settings== › ==Home Assistant== shows ==WebHook Stats==: the OK and Fail counts, the status and the registered URL. The first push arrives within one interval.

</div>

The integration owns the URL and the interval while it is registered (it re-registers after a restart of either side). A URL typed by hand into ==Url== is kept only with ==Manual Override== on.

## Settings

==Settings== › ==Home Assistant==, applied with ==Submit Changes==, except that a registration from the integration applies at once:

<dl class="facts" markdown>
<dt>Enabled</dt><dd>The push runs. Off by default; the integration's registration turns it on.</dd>
<dt>Url, Url2</dt><dd>The webhook URLs: the first is tried first, the second is the fallback (a public URL such as a Nabu Casa address for when the dongle is away from home). The integration fills them.</dd>
<dt>Interval S</dt><dd>1 to 3600 s, 60 by default.</dd>
<dt>Data Mode</dt><dd>`changed` (the default): each push carries only what changed since the previous one, plus the identity. `full`: everything every time.</dd>
<dt>Gzip</dt><dd>Compress the push. Off by default; on over the mobile network it saves most of the data.</dd>
<dt>Manual Override</dt><dd>Keep the URL you typed even when the integration pushes another.</dd>
<dt>Cert Set</dt><dd>A certificate set from ==System== › ==Certificates== for a Home Assistant with its own certificate authority. Empty uses the built-in bundle.</dd>
</dl>

## What arrives

Every interval the dongle posts one JSON document to the URL:

```json
{
  "schema": 1,
  "status": {
    "device_id": "14c19f457fed", "fw_version": "1.23.1", "hw_version": "ESPNetLink",
    "device_type": "espnetlink", "mdns": "http://espnetlink_14c19f457fed.local",
    "bits": { "time_synced": true, "eth_connected": true, "vpn_enabled": false },
    "vpn_status": "connected", "vpn_ip": "10.6.0.2"
  },
  "gps": {
    "latitude": -37.81828, "longitude": 144.96711, "accuracy": 3,
    "altitude": 31.4, "speed": 0.0, "heading": 146.6
  }
}
```

The identity (`device_id`, `fw_version`, `hw_version`) is in every push even in `changed` mode. The `gps` section is sent whole whenever the receiver has a fix, and left out otherwise, so the device tracker never gets half a position. `vpn_status` and `vpn_ip` appear while a VPN tunnel is up; the integration remembers the address as the way to reach the dongle away from home. The dongle retries on the next interval when Home Assistant answers 503, and stops after three identity rejections (403) until the next registration.

## Troubleshooting

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| Home Assistant does not discover the dongle | not on the same network, or mDNS blocked | the station WiFi on the same subnet as Home Assistant; ==Enabled== under ==Network Discovery== |
| Discovered, but the registration fails | the network is marked untrusted on the dongle | tick ==Sta Trusted== for that network |
| ==WebHook Stats== shows failures | the URL is unreachable from the dongle's network, or a certificate problem | a URL the dongle can resolve and reach; for a private CA, a ==Cert Set== |
| Status `rejected` | Home Assistant refused the device identity three times | remove and add the device again in Home Assistant |
| No position in Home Assistant | no fix | wait for the GPS tile to say Fix |
