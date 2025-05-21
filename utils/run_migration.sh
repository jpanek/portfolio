#!/bin/bash

########################################################################################
#how-to-run:

#1) run migration:
#bash utils/run_migration.sh migrate "added time to price table"

#2) run upgrade
#bash utils/run_migration.sh upgrade 
########################################################################################

# Define the project root directory
PROJECT_DIR="/Users/jurajpanek/Documents/code/portfolio_app"

# Check if the first parameter is provided
if [ -z "$1" ]; then
    echo "Error: Missing action parameter (migrate or upgrade)"
    exit 1
fi

# If migrating, check if a migration message is provided
if [ "$1" == "migrate" ] && [ -z "$2" ]; then
    echo "Error: Missing migration message for migration"
    exit 1
fi

# If the first parameter is "migrate"
if [ "$1" == "migrate" ]; then
    echo -e "\nDropping views:"
    "$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/utils/drop_views.py"

    echo -e "\nRunning DB Migration: \"$2\" "
    FLASK_APP="$PROJECT_DIR/app.py" "$PROJECT_DIR/venv/bin/flask" db migrate -m "$2"

# If the first parameter is "upgrade"
elif [ "$1" == "upgrade" ]; then

    echo -e "\nDropping views just in case before upgreading the DB:"
    "$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/utils/drop_views.py" #should remove later

    echo -e "\nUpgrading DB:"
    FLASK_APP="$PROJECT_DIR/app.py" "$PROJECT_DIR/venv/bin/flask" db upgrade

    echo -e "\nRecreating views:"
    "$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/utils/create_views.py"

else
    echo "Error: Invalid first parameter. Use 'migrate' or 'upgrade'."
    exit 1
fi
