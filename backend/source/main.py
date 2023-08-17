import os
import importlib

INSTANCE_NAME = os.environ.get('SIWINS_INSTANCE')

# Define the module name based on the cluster
module_path = f"source.{INSTANCE_NAME}"
main_config_path = f"{module_path}.main_config"
geoconfig_path = f"{module_path}.geoconfig"

# Import the module dynamically
try:
    main_config = importlib.import_module(main_config_path)
    geoconfig = importlib.import_module(geoconfig_path)
except ImportError:
    print(f"Module {module_path} not found")
