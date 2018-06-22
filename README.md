# ML_Pipeline_Tutorial
![Pipeline](https://github.com/mrubash1/ml_pipeline_tutorial/blob/master/content/ml_pipeline.png)

## Requisites
- gcloud command line tool
- set the [google application credentials](https://cloud.google.com/docs/authentication/getting-started)
- enable the following GCP APIs (cloud functions, cloud vision api, cloud pubsub, cloud storage, cloud translate api, ml)
- conda

## Setup 
Download repo and setup python path
```
git clone https://github.com/mrubash1/ml_pipeline_tutorial
cd ml_pipeline_tutorial
echo "export ml_pipeline_tutorial=${PWD}" >> ~/.bash_profile
echo "export PYTHONPATH=$ml_pipeline_tutorial/src:${PYTHONPATH}" >> ~/.bash_profile
source ~/.bash_profile
```
Setup conda environment and activate
```
conda create --name ml_pipeline python=2.7
source activate ml_pipeline
cd $ml_pipeline_tutorial
pip install -r requirements.txt
```

## Upload file to cloud storage for analysis
```
python $ml_pipeline_tutorial/src/python/stub_image_uploader.py \
  --project=myproject-204318 \
  --bucket_name='ml_pipeline_tutorial_v0' \
  --local_filename='/Users/mattrubashkin/ml_pipeline_tutorial/data/french_sign.jpg' \
  --output_name='signs'
```
This specific bucket can be found [here](https://console.cloud.google.com/storage/browser/ml_pipeline_tutorial_v0?project=myproject-204318)

## OCR pipeline with Google Cloud Functions 
TODO: Show pipeline here
To see the logs after images are uploaded to the bucket:
```
gcloud beta functions logs read --limit 100
```

### OCR pipeline setup
_The following section borrows extensively from [Google's OCR Tutorial](https://cloud.google.com/functions/docs/tutorials/ocr)_
Set up the app/config.json file
```
{
  "RESULT_TOPIC": "ml_pipeline_v0_result_topic",
  "RESULT_BUCKET": "ml_pipeline_v0_result_bucket",
  "TRANSLATE_TOPIC": "ml_pipeline_v0_translate_topic",
  "TRANSLATE": true,
  "TO_LANG": ["en", "fr", "es", "ja", "ru"]
}
```
**And make sure to create these buckets!**

The Node file app/index.js does several functions:
- import several dependencies in order to communicate with Google Cloud Platform services
- reads an uploaded image file from Cloud Storage and calls the detectText function
- extracts text from the image using the Cloud Vision API and queues the text for translation:
- translates the extracted text and queues the translated text to be saved back to Cloud Storage
- receives the translated text and saves it back to Cloud Storage

**Navigate to $ml_pipeline_tutorial/app**
To deploy the process image function:
```
gcloud beta functions deploy ocr-extract --trigger-bucket ml_pipeline_tutorial_v0 --entry-point processImage
```
To deploy the translateText function with a Cloud Pub/Sub trigger:
```
gcloud beta functions deploy ocr-translate --trigger-topic ml_pipeline_v0_translate_topic --entry-point translateText
```
To deploy the saveResult function with a Cloud Pub/Sub trigger:
```
gcloud beta functions deploy ocr-save --trigger-topic ml_pipeline_v0_result_topic --entry-point saveResult

```

### Work in Progress - Install Object Detection Model
```
source activate ml_pipeline
pip install tensorflow
pip install Cython
pip install jupyter
pip install matplotlib
pip install pillow
pip install lxml
```
Install a clean version of tensorflow models within the library
Then move the cocodataset to tensorflow/models/research directory
```
cd $ml_pipeline_tutorial
git clone https://github.com/tensorflow/models
git clone https://github.com/cocodataset/cocoapi.git
cd cocoapi/PythonAPI
make
cp -r pycocotools ../../models/research/
```
Compile the protobuffs. If on a Mac, first:
```
brew install protobuf
```
When protobuf installed:
```
cd $ml_pipeline_tutorial/models/research
protoc object_detection/protos/*.proto --python_out=.
```
Add libraries to python path
```
echo "export PYTHONPATH=$PYTHONPATH:$ml_pipeline_tutorial/models/research/slim" >> ~/.bash_profile
source ~/.bash_profile
```
Test if successful
```
python $ml_pipeline_tutorial/models/research/object_detection/builders/model_builder_test.py
```

### Work with deploying model
Download standard object detection model and inference package
```
cd $ml_pipeline_tutorial/models/research/object_detection
curl http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz | tar -xz
rm faster_rcnn_inception_v2_coco_2018_01_28.tar.gz
```
Upload the trained model and pbtext to google cloud storage
```
cd $ml_pipeline_tutorial/models/research/object_detection
gsutil -m cp -R faster_rcnn_inception_v2_coco_2018_01_28/  gs://mr_faster_rcnn_inception_v2_coco_2018_01_28
$ gsutil -m cp -R data/mscoco_label_map.pbtxt  gs://mr_faster_rcnn_inception_v2_coco_2018_01_28/faster_rcnn_inception_v2_coco_2018_01_28/saved_model.pbtxt
```
Create a GCP ML Engine Model
```
MODEL_NAME="mr_faster_rcnn_inception_v2_coco_2018_01_28"
gcloud ml-engine models create $MODEL_NAME
DEPLOYMENT_SOURCE="gs://mr_faster_rcnn_inception_v2_coco_2018_01_28/faster_rcnn_inception_v2_coco_2018_01_28/saved_model"
gcloud ml-engine versions create "v1_0"\
    --model $MODEL_NAME --origin $DEPLOYMENT_SOURCE
```
Check that it worked
```
gcloud ml-engine versions describe "v1_0" \
    --model $MODEL_NAME
```
