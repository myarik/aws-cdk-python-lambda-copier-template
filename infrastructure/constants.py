"""
Constants
"""

SERVICE_NAME_TAG = "service"
OWNER_TAG = "owner"

SERVICE_NAME = "ticket-routing"
LOG_LEVEL = "DEBUG"

# Build folders
BUILD_FOLDER = ".build/lambdas/"
LAYER_BUILD_FOLDER = ".build/layers/"

# Lambda settings
HANDLER_LAMBDA_TIMEOUT = 10
HANDLER_LAMBDA_MEMORY_SIZE = 128

# Authorizer settings
AUTHORIZER_CACHE_TTL = 5
