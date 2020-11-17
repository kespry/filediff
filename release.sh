#!/bin/bash -e

update_version() {
python <<EOF
# Update setup.py
lines = []
with open("setup.py") as fp:
  for line in fp:
    if line.startswith("MINOR_VERSION"):
      mv = int(line.split()[2])
      mv += 1
      line = "MINOR_VERSION = {}\n".format(mv)
    lines.append(line)

with open("setup.py", "w") as fp:
  fp.writelines(lines)

print("Updated minor version to {}".format(mv))
EOF
}

pip install --upgrade pip==19.2
pip install wheel twine keyring artifacts-keyring

rm -rf ./build ./dist

update_version

python setup.py sdist bdist_wheel

# If the lib builds commit the updated version
git commit setup.py -m "Bumpped version"

twine upload -r kespryml dist/*
