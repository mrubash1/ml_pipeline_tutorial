# saving images and vision analysis
from PIL import Image

# general imports
import io
import os
import time
import click

# uploading to google cloud storage
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials

# functions
def write_to_storage(project, bucket_name, local_filename, output_name):
    # get time stamp into name
    formatted_time = time.strftime('%Y_%m_%d-%H_%M_%S',time.localtime(time.time())) 
    output_name_with_timestamp=output_name + formatted_time + '.jpg'
    # bucket orientation
    client = storage.Client(project)
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(output_name_with_timestamp)
    # load file
    blob.upload_from_filename(local_filename)
    # location of upload
    output_bucket_and_filename=bucket_name+'/'+output_name_with_timestamp
    return output_bucket_and_filename

# to run in console
if __name__ == '__main__':


    project='myproject-204318'
    bucket_name='ml_pipeline_tutorial_v0'
    local_filename='caltrain.jpg'
    output_name='caltrain'

    # Use click to parse command line arguments
    @click.command()
    @click.option('--project', default='myproject-204318', help='GCloud project name', type=str)
    @click.option('--bucket_name', default='ml_pipeline_tutorial_v0', help='Cloud storage bucket name', type=str)
    @click.option('--local_filename', default='/Users/mattrubashkin/ml_pipeline_tutorial/notebooks/caltrain.jpg',
         help='Local filename location', type=str)
    @click.option('--output_name', default='caltrain', help='Base output filename for cloud storage', type=str)

    # Train RNN model using a given configuration file
    def main(project, bucket_name, local_filename, output_name):
        output_bucket_and_filename = \
            write_to_storage(project, bucket_name, local_filename, output_name)
        print ('Upload complete: %s' % (output_bucket_and_filename))

    main()