#!/bin/bash

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --version VERSION         Set the version."
    echo "  --build_name BUILD_NAME   Set the build name."
    echo "  --build_number NUMBER     Set the build number."
    echo "  --version_file FILE       Set the version file."
    echo "  --push                    Push the Docker image."
    exit 1
}

for cmd in jq docker python; do
    if ! command -v $cmd &> /dev/null; then
        echo "Error: $cmd is required but not installed." >&2
        exit 1
    fi
done

version="0.1.1"
build_name="Salvador Limones"
version_file="version.json"

while [[ $# -gt 0 ]]; do
    case $1 in
        --version) version="$2"; shift 2 ;;
        --build_name) build_name="$2"; shift 2 ;;
        --build_number) build_number="$2"; shift 2 ;;
        --version_file) version_file="$2"; shift 2 ;;
        --push) push=true; shift ;;
        *) echo "Unknown option: $1" >&2; usage ;;
    esac
done

if [[ -z "$build_number" ]]; then
    build_number=$(jq -r '.mancave[0].buildNumber' "$version_file")
    if ! [[ $build_number =~ ^[0-9]+$ ]]; then
        echo "Error: Failed to parse build number from $version_file" >&2
        exit 1
    fi
    ((build_number++))
fi

if ! python -c "from tools.common import version_generator; version_generator('$version', '$build_name', '$build_number', '$version_file')"; then
    echo "Error: Failed to update version file." >&2
    exit 1
fi

if ! docker compose build; then
    echo "Error: Docker build failed." >&2
    exit 1
fi

if [[ "$push" == true ]]; then
    if ! docker push rootifera/mancaveman:psql; then
        echo "Error: Docker push failed." >&2
        exit 1
    fi
fi
