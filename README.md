# Tycho Station

A simple registry for storing versioned packages and archives.

## Installation

Python 3.6+ required

`pip install tycho-station[s3]`

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

# Pull specific version
tychoreg pull pkgname --version 1.0
# Outputs to tycho_packages/{filename} by default

# Pull multiple packages at latest
tychoreg pull-list pkgname1 pkgname2 pkgname3

# More help
tychoreg {command} --help
```
## Configuration

The default configuration file is `.tychoreg.json`. You can use the `--config` option to change this path.

**Example Configuration**

```json
{
  "tycho": {
    "backend": "s3",
    "outdir": "tycho_packages"
  },
  "s3": {
    "bucket": "my-registry",
    "region_name": "us-east-1",
    "aws_access_key_id": "KEYHERE",
    "aws_secret_access_key": "SECRETHERE"
  }
}
```

Note: s3 attributes can be anything that is accepted by `boto3.client('s3', **kwargs)` except for `bucket` which is passed in later.

**Example Configuration Using Environment Variables**

For this example, a Read only key is set for pulling packages by everyone and users with escalated privileges can use a Write key.

```json
{
  "s3": {
    "bucket": "my-registry",
    "region_name": "us-east-1",
    "aws_access_key_id": {
        "env": "REG_WRITE_KEY",
        "default": "KEYHERE"
    },
    "aws_secret_access_key": {
        "env": "REG_WRITE_SECRET",
        "default": "SECRETHERE"
    }
  }
}
```

**Loading a DotEnv file**
```json
    ...
    "tycho": {
        "dotenv": "/home/paul/cspace/tycho-station/.env"
    },
    ...
```


## Motivations

During the course of development you often need to store versioned packages that don't nicely fit into any packaging ecosystem. And even when they do fit into an ecosystem such as NPM, PyPi, Conan, etc sometimes you do not want to maintain the infrastructure behind those packaging systems. I wanted a simple way to store files on a private remote storage and pull down versions as needed. Thus Tycho Station was conceived.

Tycho Station lets you store archives such as tarballs and zip files but also really anything on a remote storage system in a versioned fashion and then pull them down as needed.

## Architecture

Tycho Station is designed to work with multiple storage systems but right now the first and default system is Amazon S3 storage. Packages are organized like shown below.

```
bucket
│
└───package_name_1
│   │   tycho.json
│   │   tycho_1.0.pkg
│   │   tycho_1.1.pkg
│   │   tycho_2.0.pkg
│
└───package_name_2
    │   tycho.json
    │   tycho_1.0.pkg
    │   tycho_1.1.pkg
    │   tycho_2.0.pkg
```

**tycho.json**

This file is what tracks the package meta data.

```json
{
  "localname": "narf.tar.gz",
  "latest": "1.0"
}
```

**tycho.json Attributes**
| Name           | Description  | Command(s)  |
| :------------- | :----------- | :---------- |
| localname      | Filename used when downloading the package. | Set by `init` command |
| latest         | Version that is downloaded when `latest` is requested. | Updated when `promote` command is used or `--promote-latest` flag is used with the `push` command. |
