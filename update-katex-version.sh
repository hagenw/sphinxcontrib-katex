#!/bin/bash

NEW_VERSION=$(curl -s 'https://registry.npmjs.org/katex' | jq '.["dist-tags"]["latest"]')
CURRENT_VERSION=$(awk '/katex_version =/{print $3}' sphinxcontrib/katex.py)

# Remove "" and '' around version
NEW_VERSION=${NEW_VERSION//\"/}
CURRENT_VERSION=${CURRENT_VERSION//\'/}

echo "Current KaTeX version: ${CURRENT_VERSION}"
echo "New KaTeX version: ${NEW_VERSION}"

# Download JS file
curl -s https://cdn.jsdelivr.net/npm/katex@${NEW_VERSION}/dist/katex.min.js --output sphinxcontrib/katex.min.js

# Update Python file
sed -i "/katex_version = '${CURRENT_VERSION}'/c\\katex_version = '${NEW_VERSION}'" sphinxcontrib/katex.py

# Update README
sed -i "s/${CURRENT_VERSION}/${NEW_VERSION}/" README.rst
