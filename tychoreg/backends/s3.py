import boto3
import botocore

from tychoreg.backends.core import BackendBase, Package


class Backend(BackendBase):
    def __init__(self, **config):
        self.bucket = config['bucket']
        del config['bucket']
        self.client = boto3.client('s3', **config)

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
                data = self.json_data(metapath)
                pkg = Package(name, data)

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
