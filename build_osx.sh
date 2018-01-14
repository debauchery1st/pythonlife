#!/usr/bin/env bash
echo "building OSX package."
chmod +x ./install_buildozer.sh
./install_buildozer.sh
buildozer osx release
mv ./bin ./dist
open ./dist/pylife.dmg

echo "cleaning build directories"
rm -rf ./.buildozer
cd buildozer
sudo -H pip uninstall .
cd ..
rm -rf ./buildozer

echo "done"

