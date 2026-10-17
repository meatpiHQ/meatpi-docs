# LEDs

<p class="lead">Three LEDs say what the device is doing: power, connection and bus activity. There are no patterns to decode; each one is on, off or blinking with the traffic.</p>

| LED | On the case | Meaning |
| --- | --- | --- |
| **Power** | the power symbol | On while WiCAN runs. Off while it sleeps, and when it has no power. It also lights when the device is put into download mode for [recovery over USB](../firmware/usb-flash.md). |
| **Connection** | the WiFi symbol | On while someone is connected to WiCAN: an app on the TCP port, a phone over Bluetooth, the Monitor tab, or the MQTT broker. It says nothing about the WiFi link itself: a WiCAN joined to your network with nobody talking to it shows it off. |
| **Data** | the envelope | Blinks with the frames received from the CAN bus. Steady off means nothing is arriving: the ignition is off, the bit rate is wrong, or the bus is not connected. |

| Everything off | |
| --- | --- |
| Asleep, or no power | WiCAN wakes when the battery voltage rises above the sleep voltage, see [Sleep and battery alert](../power/sleep-and-wake.md). Plugged into a car with the ignition off, that is normal after the sleep delay. |

On WiCAN OBD the three LEDs are on the face of the case under their symbols. On WiCAN USB the connection and data LEDs show next to the terminal labels.
