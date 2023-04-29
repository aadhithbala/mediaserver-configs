import subprocess
import requests
import json
import os

# Discord webhook URL
webhook_url = "INSERT_WEBHOOK_URL"

# Execute apt update and upgrade
print("Updating package list...")
subprocess.run(['apt', 'update', '-y'])
print("Upgrading packages...")
subprocess.run(['apt', 'upgrade', '-y'])


# Get list of upgraded packages
print("Getting list of upgraded packages...")
upgraded_packages = subprocess.run(['apt', 'list', '--upgradable'], stdout=subprocess.PIPE).stdout.decode().strip()

# Print list of upgraded packages
print("Upgraded packages:", upgraded_packages)

# Remove orphaned packages
print("Removing orphaned packages...")
try:
    orphan_packages = subprocess.run(['deborphan'], stdout=subprocess.PIPE).stdout.decode().splitlines()
    if orphan_packages:
        subprocess.run(['apt-get', 'remove', '--purge'] + orphan_packages)
        print("Orphaned packages removed:", orphan_packages)
    else:
        print("No orphaned packages found.")
except FileNotFoundError:
    print("Could not remove orphaned packages: deborphan not found.")

# Remove unused packages
print("Removing unused packages...")
subprocess.run(['apt-get', 'autoremove', '-y'])

# Clean apt cache
print("Cleaning apt cache...")
subprocess.run(['apt-get', 'clean'])

# Vacuum systemd journals
print("Vacuuming systemd journals...")
try:
    output = subprocess.run(['journalctl', '--vacuum-time=3d'], stdout=subprocess.PIPE).stdout.decode().strip()
    if output:
        print("Journals vacuumed:", output)
    else:
        print("No journals vacuumed.")
except FileNotFoundError:
    print("Could not vacuum journals: journalctl not found.")

# Check for system errors
print("Checking for system errors...")
system_errors = subprocess.run(['journalctl', '-p', '3', '-xb'], stdout=subprocess.PIPE).stdout.decode().strip()
if system_errors:
    print("System errors found:", system_errors)
else:
    print("No system errors found.")

# Send message to Discord webhook
if webhook_url:
    # Prepare the message payload
    message = {
        "username": "Server Housekeeper",
        "embeds": [
            {
                "title": "Server Housekeeping Report",
                "description": "A report on the latest server housekeeping tasks.",
                "color": 15418782,
                "fields": [
                    {
                        "name": "Upgraded Packages",
                        "value": upgraded_packages if upgraded_packages else "No packages upgraded.",
                        "inline": False
                    },
                    {
                        "name": "Orphaned Packages",
                        "value": str(orphan_packages) if orphan_packages else "No orphaned packages found.",
                        "inline": False
                    },
                    {
                        "name": "Unused Packages",
                        "value": "Unused packages removed.",
                        "inline": False
                    },
                    {
                        "name": "Apt Cache",
                        "value": "Apt cache cleaned.",
                        "inline": False
                    },
                    {
                        "name": "Systemd Journals",
                        "value": output if output else "No journals vacuumed.",
                        "inline": False
                    },
                    {
                        "name": "System Errors",
                        "value": system_errors if system_errors else "No system errors found.",
                        "inline": False
                    }
                ]
            }
        ]
    }

    # Send the message to the webhook
    headers = {"Content-Type": "application/json"}
    response = requests.post(webhook_url, data=json.dumps(message), headers=headers)

    # Check the response status code
    if response.status_code == 204:
        print("Housekeeping report sent to Discord webhook.")
    else:
        print("Failed to send housekeeping report to Discord webhook.")
else:
    print("Discord webhook URL not provided. Skipping report.") 
