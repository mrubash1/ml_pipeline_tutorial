import base64
import io
import json
from PIL import Image
import tensorflow as tf
import os

# configs
width = 1024
height = 768
predict_instance_json = "data/processed/inputs.json"
predict_instance_tfr = "data/processed/inputs.tfr"
file_destination = "data/examples/trains"

# create a list of files in the folder
images = []
for root, dirs, files in os.walk(file_destination):
    for file in files:
        if file.endswith('.jpg'):
            images.append(file)

# write the record
with tf.python_io.TFRecordWriter(predict_instance_tfr) as tfr_writer:
  with open(predict_instance_json, "wb") as fp:
    for image in images:
      img = Image.open(os.path.join(file_destination,image))
      img = img.resize((width, height), Image.ANTIALIAS)
      output_str = io.BytesIO()
      img.save(output_str, "JPEG")
      fp.write(
          json.dumps({"b64": base64.b64encode(output_str.getvalue()) }) + "\n")
      tfr_writer.write(output_str.getvalue())
      output_str.close()