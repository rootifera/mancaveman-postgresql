#!/bin/bash

# environment options: 'live', 'dev', 'dev-nobuild', 'live-nobuild'
version="0.1.0"
environment="dev"
buildname="Nick Virago"

# Function to display usage information
usage() {
    echo "Usage: $0 [-v version] [-e environment]"
    echo "  -v version: Specify the version (default: $version)"
    echo "  -e environment: Specify the environment (live, dev, dev-nobuild, live-nobuild)"
}

# Function to handle version generation and Docker operations
handle_build() {
    local env_version=$1
    local docker_tag=$2
    local should_build=$3

    echo "Building $env_version..."
    python -c "from tools.common import version_generator; version_generator('$env_version', '$buildname', 'version.json')"

    if [ "$should_build" == "yes" ]; then
        docker build -t rootifera/mancaveman:$docker_tag .
        docker login
        docker push rootifera/mancaveman:$docker_tag
    fi
}

# Parsing command-line options
while getopts ":v:e:h" opt; do
  case $opt in
    v) version="$OPTARG" ;;
    e) environment="$OPTARG" ;;
    h) usage; exit 0 ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2; usage; exit 1 ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2; usage; exit 1 ;;
  esac
done

# Handling different environments
case $environment in
    "live") handle_build "$version" "latest" "yes" ;;
    "dev") handle_build "$version-dev" "dev" "yes" ;;
    "dev-nobuild") handle_build "$version-dev" "dev" "no" ;;
    "live-nobuild") handle_build "$version" "latest" "no" ;;
    *)
        echo "Unknown environment: $environment" >&2; usage; exit 1 ;;
esac
