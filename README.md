# hass-mipow-comet
Home-Assistant mipow comet component

# Install python-mipow
	pip install git+https://papagei9@github.com/papagei9/python-mipow.git

# Setup

Copy mipow_comet.py to `home-assistant-config-dir/custom_components/light/`

# Configure HASS

Add the following code to `home-assistant-config-dir/configuration.yml`


```
light:
  - platform: mipow_comet
    devices:
      70:44:4B:14:AC:E6:
        name: LED stripe
```
