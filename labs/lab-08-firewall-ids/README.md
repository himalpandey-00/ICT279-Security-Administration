# Lab 08 – Firewall and Intrusion Detection System (IDS)

## Overview

This lab focused on configuring and testing host-based firewall controls using Linux `iptables` and implementing network intrusion detection using Snort.

The Ubuntu VM was used as the firewall, server and IDS, while the Windows 10 VM acted as the client and generated traffic for testing. The lab progressed from basic packet filtering to stateful firewall rules and then to signature-based intrusion detection.

The final part tested Snort against known attack packet captures, including Teardrop and EternalBlue.

---

## Lab Environment

| System | Role | IP Address |
|---|---|---|
| Ubuntu 20.04 | Firewall, server and Snort IDS | `192.168.1.104` |
| Windows 10 | Client / traffic source | `192.168.1.101` |
| Network | Virtual lab network | `192.168.1.0/24` |
| Ubuntu interface | Network interface | `enp0s3` |

### Network Configuration

Ubuntu was configured with `192.168.1.104/24` on `enp0s3`.

![Ubuntu network configuration](screenshots/01-ubuntu-network-configuration.png)

Windows 10 used `192.168.1.101/24`, placing both VMs on the same subnet.

![Windows 10 network configuration](screenshots/02-windows10-network-configuration.png)

---

# Task 1 – Starting and Testing Services

The required packages were checked and installed:

- `iptables`
- Apache2
- `vsftpd`
- OpenSSH Server
- Snort

![Required packages installed](screenshots/03-required-packages-installed.png)

The Apache, FTP and SSH services were started:

```bash
sudo systemctl start apache2
sudo systemctl start vsftpd
sudo systemctl start ssh
```

All three services reported an active state.

![Ubuntu services running](screenshots/04-ubuntu-services-running.png)

Before applying firewall rules, connectivity from Windows 10 was tested to establish a baseline.

### HTTP

The Apache default page was successfully accessed from Windows at `http://192.168.1.104`.

![HTTP before firewall](screenshots/05-windows-http-before-firewall.png)

### SSH

Windows successfully established an SSH session with Ubuntu:

```powershell
ssh himal@192.168.1.104
```

![SSH before firewall](screenshots/06-windows-ssh-before-firewall.png)

### FTP

The Windows client successfully connected to the Ubuntu FTP server.

![FTP before firewall](screenshots/07-windows-ftp-before-firewall.png)

These tests confirmed that all three services were reachable before firewall filtering was introduced.

---

# Task 2 – Linux Firewall Configuration

## Initial iptables State

The initial firewall configuration was inspected using:

```bash
sudo iptables -nvL
```

The INPUT, FORWARD and OUTPUT chains all had a default policy of `ACCEPT`, with no filtering rules configured.

![Initial iptables state](screenshots/08-iptables-initial-state.png)

A default policy of `ACCEPT` means packets reaching the end of a chain without matching another rule are allowed.

## Configuring Incoming Traffic Rules

The following INPUT rules were added:

```bash
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A INPUT -s 192.168.1.101 -p tcp --dport 22 -j ACCEPT
```

These allowed loopback, HTTP, HTTPS, and SSH from the Windows 10 client.

![Initial INPUT rules](screenshots/09-iptables-initial-input-rules.png)

### Why was FTP still accessible?

FTP was still accessible even though TCP port 21 was not explicitly allowed because the INPUT chain still had a default policy of `ACCEPT`. Unmatched traffic therefore reached the end of the chain and was allowed.

This demonstrated the difference between **implicit allow** and **implicit deny**.

## Implementing Implicit Deny

A catch-all DROP rule was added:

```bash
sudo iptables -A INPUT -j DROP
```

![Implicit deny rule](screenshots/10-iptables-implicit-deny-rule.png)

After testing HTTP, SSH and FTP again, the counters showed traffic matching permitted rules and the final DROP rule.

![Firewall counters after testing](screenshots/11-iptables-rule-counters-after-testing.png)

A new FTP connection was tested from Windows:

```powershell
Test-NetConnection 192.168.1.104 -Port 21
```

The result was `TcpTestSucceeded : False`.

![FTP blocked by iptables](screenshots/12-ftp-blocked-by-iptables.png)

HTTP and SSH remained accessible because their ACCEPT rules appeared before the DROP rule.

### Final DROP Rule vs Default DROP Policy

Both a final catch-all DROP rule and a default DROP policy can implement implicit deny. A default policy such as:

```bash
sudo iptables -P INPUT DROP
```

is cleaner because traffic that does not match an explicit ACCEPT rule is automatically dropped. A final DROP rule provides similar behaviour, but rules appended after it will never be reached.

## Nmap Firewall Verification

Nmap was installed on Windows 10.

![Nmap installed](screenshots/13-nmap-installed-windows.png)

Ubuntu was scanned with:

```powershell
nmap -Pn 192.168.1.104
```

The scan showed SSH and HTTP as open, HTTPS as closed because no HTTPS service was listening, and the remaining scanned TCP ports as filtered.

![Nmap firewall verification](screenshots/14-nmap-firewall-verification.png)

The firewall counters increased significantly after the scan, particularly on the DROP rule.

![iptables counters after Nmap](screenshots/15-iptables-counters-after-nmap.png)

## Allowing FTP for a Specific Host

FTP access was then permitted specifically for the Windows host on TCP ports 20 and 21, while the INPUT chain used a default DROP policy.

![FTP rules with default DROP](screenshots/16-iptables-ftp-rules-default-drop.png)

FTP authentication and directory listing were successfully tested.

![FTP access after firewall rule](screenshots/17-ftp-access-after-firewall-rule.png)

## Blocking a Bad Host

The Windows machine was temporarily treated as a bad host:

```bash
sudo iptables -I INPUT 2 -s 192.168.1.101 -j DROP
```

![Bad host DROP rule](screenshots/18-iptables-bad-host-drop-rule.png)

Because iptables evaluates rules from top to bottom, this DROP rule was processed before the later HTTP, SSH and FTP ACCEPT rules.

Tests against SSH and HTTP both failed.

![Bad host blocked](screenshots/19-bad-host-ssh-http-blocked.png)

The temporary rule was then removed:

```bash
sudo iptables -D INPUT 2
```

![Bad host rule removed](screenshots/20-bad-host-rule-removed.png)

This demonstrated the importance of firewall rule ordering.

---

# Stateful Firewall Filtering

The multiport module was loaded:

```bash
sudo modprobe xt_multiport
```

Rules were created to allow established responses from server services:

```bash
sudo iptables -A OUTPUT -p tcp -m multiport --sports 20,21,22,80,443 \
-m state --state ESTABLISHED -j ACCEPT

sudo iptables -A OUTPUT -o lo -j ACCEPT

sudo iptables -A OUTPUT -p udp --dport 53 \
-m state --state NEW,ESTABLISHED -j ACCEPT

sudo iptables -A INPUT -p udp --sport 53 \
-m state --state ESTABLISHED -j ACCEPT
```

![Stateful firewall rules](screenshots/21-stateful-input-output-rules.png)

The OUTPUT policy was changed to DROP:

```bash
sudo iptables -P OUTPUT DROP
```

![OUTPUT default DROP](screenshots/22-output-default-drop.png)

DNS continued to work because it had explicit stateful rules. Ubuntu could not initiate a new outbound HTTP connection because no rule yet permitted a NEW TCP connection to port 80.

![DNS works while HTTP is blocked](screenshots/23-dns-works-http-blocked.png)

## Stateful Filtering Challenge

Outbound HTTP and HTTPS were enabled without modifying the previous incoming service rules:

```bash
sudo iptables -A OUTPUT -p tcp -m multiport --dports 80,443 \
-m state --state NEW,ESTABLISHED -j ACCEPT

sudo iptables -A INPUT -p tcp -m multiport --sports 80,443 \
-m state --state ESTABLISHED -j ACCEPT
```

Both HTTP and HTTPS connections completed successfully.

![Outbound HTTP and HTTPS success](screenshots/24-outbound-http-https-stateful-success.png)

Outbound FTP remained blocked because Ubuntu was not permitted to initiate a NEW FTP connection.

![Outbound FTP blocked](screenshots/25-outbound-ftp-blocked.png)

This demonstrated how stateful filtering distinguishes new connections from traffic belonging to established flows.

---

# Task 3 – Snort Intrusion Detection System

Before configuring Snort, iptables was reset:

```bash
sudo iptables -P INPUT ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -F
```

![iptables reset](screenshots/26-iptables-reset-before-snort.png)

## Snort Network Configuration

The Debian Snort configuration showed:

```text
DEBIAN_SNORT_HOME_NET="192.168.1.0/24"
DEBIAN_SNORT_INTERFACE="enp0s3"
```

![Snort network configuration](screenshots/27-snort-network-configuration.png)

The running Snort process also confirmed the correct interface and HOME_NET.

![Snort running process](screenshots/28-snort-running-process.png)

## Snort Configuration

The `icmp-info.rules` include was disabled to avoid interference with the custom ICMP rule, and full alert logging was enabled:

```text
output alert_full: snort.alert_full
```

The configuration was tested using:

```bash
sudo snort -T -c /etc/snort/snort.conf -i enp0s3
```

Snort successfully validated the configuration.

![Snort configuration validation](screenshots/29-snort-configuration-validation.png)

---

# Custom Snort Rules

## ICMP Detection

The following custom rule was added to `/etc/snort/rules/local.rules`:

```text
alert icmp any any -> 192.168.1.104 any (msg:"ICMP Packet found"; sid:10000001;)
```

The configuration successfully validated.

![Custom rule validation](screenshots/30-snort-custom-rule-validation.png)

Snort was restarted and confirmed active.

![Snort service active](screenshots/31-snort-service-active.png)

Windows generated ICMP traffic by pinging Ubuntu. Snort generated an alert using SID `10000001`.

![Custom ICMP alert](screenshots/32-snort-custom-icmp-alert.png)

## Bidirectional ICMP Rule

The direction operator was changed from `->` to `<>`.

The custom rule then detected both the ICMP Echo Request from Windows to Ubuntu and the Echo Reply from Ubuntu to Windows.

![Bidirectional ICMP detection](screenshots/33-snort-bidirectional-icmp-alert.png)

This matched expectations because `<>` makes the Snort rule bidirectional.

## FTP and HTTP Detection

Two additional rules were added:

```text
alert tcp any any -> any 21 (msg:"FTP Packet found"; sid:10000002;)
alert tcp any any -> any 80 (msg:"HTTP Packet found"; sid:10000003;)
```

The configuration successfully passed validation.

![FTP and HTTP rules validation](screenshots/34-snort-ftp-http-rules-validation.png)

HTTP traffic triggered SID `10000003`.

![HTTP Snort alert](screenshots/35-snort-http-alert.png)

FTP traffic triggered SID `10000002`.

![FTP Snort alert](screenshots/36-snort-ftp-alert.png)

The custom rules therefore successfully identified ICMP, FTP and HTTP traffic.

---

# Testing Snort Against Known Attacks

## Teardrop

The Teardrop packet capture was analysed offline:

```bash
sudo snort -qvde -A console \
-c /etc/snort/snort.conf \
-l /var/log/snort \
-r ~/Downloads/teardrop.cap \
-K ascii
```

Snort generated:

```text
DOS Teardrop attack
Classification: Attempted Denial of Service
Priority: 2
```

![Teardrop detection](screenshots/37-snort-teardrop-detection.png)

### Result

**Teardrop was successfully detected.**

The output also displayed IP fragmentation information associated with the captured traffic.

---

# EternalBlue / MS17-010 Testing

The EternalBlue capture was analysed:

```bash
sudo snort -qvde -A console \
-c /etc/snort/snort.conf \
-l /var/log/snort \
-r ~/Downloads/eternalblue-success-unpatched-win7.pcap \
-K ascii
```

Snort processed SMB traffic involving TCP port 445.

![EternalBlue PCAP processed](screenshots/38-eternalblue-not-detected-default-rules.png)

Searching the alert log produced no EternalBlue, MS17-010 or exploit-specific alert.

![No EternalBlue default alert](screenshots/39-eternalblue-no-default-alert.png)

### Initial Result

The original ruleset processed the capture but did **not specifically identify it as EternalBlue/MS17-010**.

## Additional EternalBlue Rules

The three EternalBlue signatures supplied in the lab were added to the local rules. They covered:

- Possible EternalBlue heap spray
- EternalBlue echo request
- EternalBlue echo response

The rules passed configuration validation, but rerunning the PCAP did not produce an EternalBlue-specific alert.

![EternalBlue custom rules no alert](screenshots/40-eternalblue-custom-rules-no-alert.png)

---

# Snort Community Rules

The Snort community rules were downloaded:

```bash
wget https://www.snort.org/downloads/community/community-rules.tar.gz
```

![Community rules downloaded](screenshots/41-snort-community-rules-downloaded.png)

Inspection of `community.rules` showed several signatures referencing MS17-010 and related SMB/CVE activity.

![MS17-010 community signatures](screenshots/42-community-rules-ms17-010-signatures.png)

## Snort Version Compatibility

When the community rules were loaded, Snort reported an incompatibility:

```text
unknown modifier "bitmask 0x8000"
```

![Community rule compatibility error](screenshots/43-community-rules-snort-version-error.png)

The Ubuntu VM was running Snort 2.9.7.0, and some newer community rules used options unsupported by that engine version. The offending rules were identified using the line numbers reported by Snort and commented out.

After resolving the incompatible rules, the configuration successfully validated.

![Community rules validation success](screenshots/44-community-rules-validation-success.png)

## Final EternalBlue Test

The EternalBlue PCAP was tested again with the community rules enabled.

The capture used the `192.168.198.0/24` network rather than the live lab network, so offline analysis was also tested with:

```text
HOME_NET=[192.168.198.0/24]
```

No EternalBlue/MS17-010-specific alert was generated.

![Final EternalBlue test](screenshots/45-eternalblue-no-detection-final-test.png)

### EternalBlue Result Summary

| Test | Result |
|---|---|
| Original Snort rules | No EternalBlue-specific alert |
| Lab-provided EternalBlue rules | No EternalBlue-specific alert |
| Community rules | No EternalBlue-specific alert |
| Community rules with PCAP HOME_NET | No EternalBlue-specific alert |

The capture was successfully processed and SMB traffic was visible, but none of the tested configurations generated an EternalBlue-specific alert in this environment.

---

# Key Findings

- `iptables` processes rules sequentially, so **rule order directly affects the result**.
- A default `DROP` policy implements **implicit deny**, allowing only explicitly authorised traffic.
- Packet counters and Nmap provide useful methods for verifying firewall behaviour.
- Stateful filtering distinguishes **NEW** connections from **ESTABLISHED** traffic.
- Stateful rules can permit replies to legitimate connections without allowing arbitrary outbound connections.
- Snort custom rules can detect selected protocols and traffic patterns using signatures.
- The `->` operator matches one direction, while `<>` can match both directions.
- Snort successfully detected the **Teardrop DoS attack** in the supplied PCAP.
- Processing malicious traffic does not automatically mean an IDS will identify the specific exploit.
- IDS effectiveness depends on suitable signatures, configuration and compatibility between the detection engine and ruleset.
- Updating IDS signatures can introduce compatibility problems when the IDS engine is older.

---

# Conclusion

This lab provided practical experience with two complementary network security controls: firewalls and intrusion detection systems.

Using `iptables` demonstrated how packet filtering, implicit deny, rule ordering and connection state can control network access. The Nmap tests and packet counters provided evidence that the firewall was enforcing the intended policy.

Snort demonstrated a different security function. Rather than simply permitting or denying traffic, it inspected network traffic against detection rules. Custom signatures successfully identified ICMP, FTP and HTTP traffic, while the Teardrop capture demonstrated detection of a known denial-of-service attack.

The EternalBlue investigation also showed an important practical limitation of signature-based intrusion detection. Snort could process the SMB traffic, but the tested signatures did not generate an EternalBlue-specific alert in this environment. Updating the community rules also exposed compatibility issues with the older Snort 2.9.7.0 engine.

Overall, the lab demonstrated why firewalling and intrusion detection are most effective when used together as part of a defence-in-depth architecture.
