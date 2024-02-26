#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Colour

print_color() {
    COLOR="$1"
    TEXT="$2"
    echo -e "${COLOR}${TEXT}${NC}"
}

print_separator() {
    print_color "$BLUE" "===================================================="
}

generate_random_number() {
    echo $((100000 + RANDOM % 900000))
}

perform_wipe() {
    print_color "$YELLOW" "This action will delete all the data."
    print_separator

    rand_num=$(generate_random_number)
    print_color "$GREEN" "Generated number: $rand_num"

    print_color "$YELLOW" "Enter the above 6-digit number to confirm: "
    read user_input

    if [ "$user_input" = "$rand_num" ]; then
        print_color "$RED" "Last Warning: CTRL+C to quit"
        sleep 5

        docker compose down --rmi all --volumes
    else
        print_color "$RED" "Incorrect number. Aborting wipe."
    fi
}

print_separator

if [ "$1" = "--wipe" ]; then
    perform_wipe
else
    print_color "$YELLOW" "Stopping Docker containers..."
    docker compose down || print_color "$RED" "Failed to stop Docker containers!"
fi

print_separator
print_color "$GREEN" "Operation completed successfully."
