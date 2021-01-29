import io
import json
import os

import boto3
import botocore

from tychoreg.backends.core import BackendBase, Package


class Backend(BackendBase):
    def __init__(self, cli_kwargs, backend_kwargs):
        super().__init__(cli_kwargs, backend_kwargs)

        self.bucket = backend_kwargs['bucket']
        del backend_kwargs['bucket']
        self.client = boto3.client('s3', **backend_kwargs)

    def exists(self, key):
        try:
            content = self.client.head_object(Bucket=self.bucket, Key=key)

        except botocore.exceptions.ClientError as e:
            return False

        else:
            return True

    def read(self, key):
        s3_object = self.client.get_object(Bucket=self.bucket, Key=key)
        return s3_object['Body'].read()

    def list_packages(self):
        ret = []
        paginator = self.client.get_paginator('list_objects')
        result = paginator.paginate(Bucket=self.bucket, Delimiter='/')
        for prefix in result.search('CommonPrefixes'):
            name = prefix.get('Prefix')[:-1]
            pkg = Package(name)
            metapath = str(pkg.metapath)
            if self.exists(metapath):
                pkg.meta = self.json_data(metapath)

            ret.append(pkg)

        return ret

    def list_versions(self, pkg):
        ret = []
        result = self.client.list_objects(Bucket=self.bucket,
                                          Prefix='{}/tycho_'.format(pkg))
        for r in result.get('Contents'):
            key = r['Key']
            if key.endswith('.pkg'):
                key = key.replace('{}/tycho_'.format(pkg), '')
                key = key[:-4]
                ret.append(key)

        ret.sort()
        return ret

    def pull(self, pkgname, version, outfile=None, force=False):
        pkg = Package(pkgname)
        pkg.meta = self.json_data(str(pkg.metapath))
        if version == 'latest':
            version = pkg.meta['latest']

        if not version:
            self.message('Nothing to Pull: {}'.format(pkgname))
            return

        file_key = self.remote_pkg_path(pkgname, version)
        localpath = self.outdir / pkg.meta['localname']
        if outfile:
            localpath = outfile

        self.ensure_dir(localpath.parent)

        info = None
        if not force:
            info = self.client.head_object(Bucket=self.bucket, Key=file_key)
            force = self.needs_update(info['ETag'], info['ContentLength'],
                                      localpath)

        if force:
            if not info:
                info = self.client.head_object(Bucket=self.bucket,
                                               Key=file_key)

            self.message('Pulling: {} {} -> {}'.format(pkgname, version,
                                                       localpath))
            self.client.download_file(self.bucket, file_key, str(localpath))
            self.write_etag(info['ETag'], localpath)

        else:
            self.message('Skipping: {}'.format(pkgname))

    def push(self, pkgname, version, file, promote_latest=False):
        file_key = self.remote_pkg_path(pkgname, version)

        if self.exists(file_key):
            self.error('Already Exists: {}, Version {}'.format(
                pkgname, version))
            return 1

        else:
            self.client.upload_file(str(file), self.bucket, file_key)
            if promote_latest:
                self.promote(pkgname, version)

    def promote(self, pkgname, version):
        file_key = self.remote_pkg_path(pkgname, version)

        if self.exists(file_key):
            pkg = Package(pkgname)
            data = self.json_data(str(pkg.metapath))
            data['latest'] = version
            fh = io.BytesIO(json.dumps(data, indent=2).encode())
            self.client.upload_fileobj(fh, self.bucket, str(pkg.metapath))

        else:
            self.error('Does Not Exist: {}, Version {}'.format(
                pkgname, version))
            return 1

    def init(self, pkgname, filename):
        pkg = Package(pkgname)

        if self.exists(str(pkg.metapath)):
            self.error('Already Initialized: {}'.format(pkgname))

        else:
            data = {"localname": filename, "latest": None}
            fh = io.BytesIO(json.dumps(data, indent=2).encode())
            self.client.upload_fileobj(fh, self.bucket, str(pkg.metapath))
            self.message('Initialized: {}'.format(pkgname))
