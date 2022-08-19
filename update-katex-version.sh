#!/bin/bash

NEW_VERSION=$(curl -s 'https://registry.npmjs.org/katex' | jq '.["dist-tags"]["latest"]')
CURRENT_VERSION=$(awk '/katex_version =/{print $3}' sphinxcontrib/katex.py)

# Remove "" and '' around version
NEW_VERSION=${NEW_VERSION//\"/}
CURRENT_VERSION=${CURRENT_VERSION//\'/}

echo "Current KaTeX version: ${CURRENT_VERSION}"
echo "New KaTeX version: ${NEW_VERSION}"

if [ ${NEW_VERSION} -lt ${CURRENT_VERSION} ]; then
    echo "Something went wrong as current version is newer"
    exit 1
fi

if [ ${NEW_VERSION} -eq ${CURRENT_VERSION} ]; then
    echo "Versions are the same."
    exit 0
fi

KATEX_URL="https://cdn.jsdelivr.net/npm/katex@${NEW_VERSION}/dist"

# Download JS files
echo "Updating katex.min.js"
curl -s ${KATEX_URL}/katex.min.js --output sphinxcontrib/katex.min.js
echo "Updating auto-render.min.js"
curl -s ${KATEX_URL}/auto-render.min.js --output sphinxcontrib/auto-render.min.js

# Update Python file
sed -i "/katex_version = '${CURRENT_VERSION}'/c\\katex_version = '${NEW_VERSION}'" sphinxcontrib/katex.py

# Update README
sed -i "s/${CURRENT_VERSION}/${NEW_VERSION}/" README.rst
