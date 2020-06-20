#!/usr/bin/env python3

import boto3
import csv
import fire
import json
import uuid


class DataLoad(object):
    """
    Load the service data into DynamoDB
    """
    def __init__(self):
        self.loadmap = LoadMap()


    def Load(self, filename, table, mapfile='', overwrite=False, dryrun=True, local=False):
        dynamodb = boto3.resource('dynamodb')

        if local == False:
            dynamodb = boto3.resource('dynamodb')
        else:
            dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url='http://localhost:8000'
            )

        if dryrun == False:
            try:
                dynamodb_table = dynamodb.Table(table)
            except Exception as e:
                print('Error connecting to DynamoDB: {}, {}'.format(table, e))

        # Sort out the CSV -> JSON mapping.
        # If no mapfile provided assume filename_map.csv
        if len(mapfile) == 0:
            mapfile = '_map.'.join(filename.split('.'))

        mapping = self.loadmap.Load(mapfile)
        # If overwrite is true remove old data
        if overwrite == True:
            # TODO: Make this work
            # Clear out all existing data (or delete and re-create table)
            print('Replacing existing data!')

            # TODO Fix hardcoded primary key
            scan = None
            with dynamodb_table.batch_writer() as batch:
                while scan is None or 'LastEvaluatedKey' in scan:
                    if scan is not None and 'LastEvaluatedKey' in scan:
                        scan = dynamodb_table.scan(
                            ExclusiveStartKey = scan['LastEvaulatedKey'],
                        )
                    else:
                        scan = dynamodb_table.scan()
                print('Deleting {} items from table'.format(len(scan)+1))
                for item in scan['Items']:
                    batch.delete_item(Key={'uuid': item['uuid']})
        else:
            print('Adding to existing data.')

        # Open the file and read in.
        rows = 0
        try:
            csvfile = open(filename, 'r', encoding='utf-8-sig', newline='\n')
            csv_data = csv.DictReader(csvfile, delimiter=',')

            print('Using mapfile: {}'.format(mapfile))
            print('Using datafile: {}'.format(filename))

            for line in csv_data:
                json_data = {}
                for key in mapping:
                    # If source is empty we assume the same field name as destinateion
                    if mapping[key]['source'] == None:
                        source_field = key
                    else:
                        source_field = mapping[key]['source']

                    value = ''
                    if mapping[key]['action'] == None:
                        # Check source field exists, and isn't empty
                        if source_field in line:
                            if line[source_field] != None:
                                if len(line[source_field]) > 0:
                                    value = str(line[source_field])
                    else:
                        # Generate a UUID
                        if mapping[key]['action'] == 'generate_uuid':
                            value = str(uuid.uuid4())

                    # Probably need to do some data work for field types
                    if len(value) > 0:
                        if mapping[key]['type'] == 'list':
                            # TODO Create a list from the data.
                            json_data[key] = value.split('|')
                        else:
                            json_data[key] = value

                print('{} : {}'.format(csv_data.line_num, json_data))

                if dryrun == False:
                    response = dynamodb_table.put_item(
                        Item=json_data,
                    )

                    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                        print('Line Ok - {} : {}'.format(csv_data.line_num, json_data))
                        rows += 1
                    else:
                        print('Error - {} : {}'.format(csv_data.line_num, json_data))

            csvfile.close()

            print('Rows added: {}'.format(rows))

        except OSError as e:
            print('Error opening file: {}, {}'.format(filename, e))
            sys.exit(0)


class LoadMap(object):

    def Load(self, mapfile):
        """
        Create the CSV to JSON map

        If no mapfile provided assume filename_map.csv
        """

        # Open the file and read in.
        try:
            csvfile = open(mapfile, 'r', encoding='utf-8-sig', newline='\n')
            map_data = csv.DictReader(csvfile, delimiter=',')

            mapping = {}
            fields = {'source', 'type', 'action'}
            for line in map_data:
                mapping[line['destination']] = {}
                for field in fields:
                    value = None
                    if field in line:
                        if line[field] != None and len(line[field]) > 0:
                            value = line[field]

                    mapping[line['destination']].update({
                        field: value
                    })
            csvfile.close()

            return mapping

        except OSError as e:
            print('Error opening file: {}, {}'.format(mapfile, e))
            sys.exit(0)


if __name__ == '__main__':
    fire.Fire(DataLoad)
