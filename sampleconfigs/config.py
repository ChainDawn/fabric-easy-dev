import yaml

KEY_ORGANIZATIONS = "Organizations"
KEY_SYSTEM_CHANNEL = "SystemChannel"
KEY_USER_CHANNEL = "UserChannels"

with open("../deploy/config.yaml", 'r') as configFile:
    config = yaml.safe_load(configFile)

if KEY_ORGANIZATIONS in config:
    print("Config Organizations Msp..")

if KEY_SYSTEM_CHANNEL in config:
    print("Config System Channel..")

if KEY_USER_CHANNEL is None:
    print("Config User Channels..")
