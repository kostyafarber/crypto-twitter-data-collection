import boto3

ssm = boto3.client('ssm', region_name='ap-southeast-2', aws_access_key_id='AKIAQQUWHDWV3JE5P6FY', aws_secret_access_key='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')
response = ssm.get_parameters(Names=['binance-public-key', 'binance-api-secret'], WithDecryption=True)

