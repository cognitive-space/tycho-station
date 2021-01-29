# Tycho Station

A simple registry for storing versioned packages and archives.

## Installation

Python 3.6+ required

`pip install tycho-station`

## Usage

```bash
# initialize package on remote storage
# pkgname = Name of package
# filename =  Filename you would like package downloaded to when it's pulled
tychoreg init pkgname filename

# Push new version to remote storage
tychoreg push pkgname 1.0 path_to/local/file --promote-latest

# Pull latest package
tychoreg pull pkgname
# Outputs to tycho_packages/{filename} by default
```

