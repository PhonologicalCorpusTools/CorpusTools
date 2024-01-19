#!/bin/sh
# This shell script creates a DMG distribution of the executable on a mac.
# Run it after creating an .app using pyinstaller.

# Create a folder 'dmg' under dist and use it to prepare the DMG.
mkdir -p dist/dmg
# Empty the dmg folder.
rm -r dist/dmg/*
# Copy the app bundle to the dmg folder.
cp -r "dist/Phonological CorpusTools.app" dist/dmg
# If the DMG already exists, delete it.
test -f "dist/CorpusTools.dmg" && rm "dist/CorpusTools.dmg"

create-dmg \
  --volname "Phonological CorpusTools" \
  --volicon "resources/favicon.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "Phonological CorpusTools.app" 175 120 \
  --hide-extension "Phonological CorpusTools.app" \
  --app-drop-link 425 120 \
  "dist/CorpusTools.dmg" \
  "dist/dmg/"
  