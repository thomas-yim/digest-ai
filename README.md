# digest-ai

For M1 macs call 
CONDA_SUBDIR=osx-64 conda env create -f environment.yml

Otherwise call
conda env create -f environment.yml

Then to enter the environment call

`conda activate digest`

You need an openai key that will go in config_keys.py under the field OPENAI_KEY=""

You will need a google speech service account and export GOOGLE_APPLICATION_CREDENTIALS="key.json"

Consult other repo for the website.
Run the flask app to setup the api at a port and forward a public address to the localhost.
