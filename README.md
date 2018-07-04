# ML_Pipeline_Tutorial
![Pipeline](https://github.com/mrubash1/ml_pipeline_tutorial/blob/master/content/ml_pipeline.png)

## Requisites
- gcloud command line tool
- set the [google application credentials](https://cloud.google.com/docs/authentication/getting-started)
- enable the following GCP APIs (cloud functions, cloud vision api, cloud pubsub, cloud storage, cloud translate api, ml, cloud firestore api)
- conda
- npm
- firebase CLI

## Setup Environment
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

### Work in Progress - Install Object Detection Model
Install a clean version of tensorflow models within the library
Then move the cocodataset to tensorflow/models/research directory
```
source activate ml_pipeline
cd $ml_pipeline_tutorial
git clone https://github.com/tensorflow/models
git clone https://github.com/cocodataset/cocoapi.git
cd cocoapi/PythonAPI
make
cp -r pycocotools ../../models/research/
```
Create the protocol buffers, and add libraries to the python paht
```
cd $ml_pipeline_tutorial/models/research
protoc object_detection/protos/*.proto --python_out=.
echo "export PYTHONPATH=$PYTHONPATH:$ml_pipeline_tutorial/models/research/slim" >> ~/.bash_profile
source ~/.bash_profile
source activate ml_pipeline
```
Test if successful
```
python $ml_pipeline_tutorial/models/research/object_detection/builders/model_builder_test.py
```

### Deploy a model on Google Cloud ML Engine
Download standard object detection model and inference package
```
cd $ml_pipeline_tutorial/models/research/object_detection
curl http://download.tensorflow.org/models/object_detection/faster_rcnn_inception_v2_coco_2018_01_28.tar.gz | tar -xz
```
Export a model for GCP ML Engine
```
cd $ml_pipeline_tutorial/models/research/object_detection
OBJECT_DETECTION_CONFIG=$ml_pipeline_tutorial/models/research/object_detection/samples/configs/faster_rcnn_inception_v2_coco.config
python export_inference_graph.py \
    --input_type encoded_image_string_tensor \
    --pipeline_config_path ${OBJECT_DETECTION_CONFIG} \
    --trained_checkpoint_prefix $ml_pipeline_tutorial/models/research/object_detection/faster_rcnn_inception_v2_coco_2018_01_28/model.ckpt \
    --output_directory $ml_pipeline_tutorial/models/research/object_detection/faster_rcnn_inception_v2_coco_2018_01_28/output
```
You can inspect the exported graph to make sure it is complete via:
```
cd $ml_pipeline_tutorial/models/research/object_detection
saved_model_cli show --dir faster_rcnn_inception_v2_coco_2018_01_28/output/saved_model --all
```
Prepare the inputs as a list of JSON objects as the inputs for the prediction service.
```
cd $ml_pipeline_tutorial
python src/python/image_formatter.py
```
Verify that the inference can run locally
```
gcloud ml-engine local predict \
    --model-dir $ml_pipeline_tutorial/models/research/object_detection/faster_rcnn_inception_v2_coco_2018_01_28/output/saved_model \
    --json-instances $ml_pipeline_tutorial/data/processed/inputs.json
```
Upload the trained model to google cloud storage
```
cd $ml_pipeline_tutorial/models/research/object_detection
gsutil -m cp -R faster_rcnn_inception_v2_coco_2018_01_28/output/saved_model/saved_model.pb gs://mr_faster_rcnn_inception_v2_coco_2018_01_28
```
Create a GCP ML Engine Model
```
MODEL_NAME="mr_faster_rcnn_inception_v2_coco_2018_01_28"
gcloud ml-engine models create $MODEL_NAME
DEPLOYMENT_SOURCE="gs://mr_faster_rcnn_inception_v2_coco_2018_01_28"
gcloud ml-engine versions create "v1_7" --model $MODEL_NAME \
  --origin $DEPLOYMENT_SOURCE \
  --runtime-version 1.4
```
Check that it worked
```
gcloud ml-engine versions describe "v1_0" \
    --model $MODEL_NAME
```
## Making predictions on the model via Cloud Functions & Firebase
This code is based off of [Sara Robinson's Taylor Swift](https://github.com/sararob/tswift-detection) detection code 
* In `cd $ml_pipeline_tutorial/firebase` initialize a project via `firebase init` with Storage, Functions, and Firestore. 
* Then go to https://console.firebase.google.com to add the firebase project to your existing gcp project, and run `firebase use --add` to add the project
* Make sure Cloud Firestore is enabled in GCP conosle and Firebase console
* Make sure v0.9.1 of Cloud Functions is installed, 1.0 and beyond is incompatible!
* Then deploy the function in `cd $ml_pipeline_tutorial/tswift-detection` by running: `firebase deploy`. 
* Once the function deploys, test it out: create an `images/` subdirectory in the Storage bucket in your Firebase console
* Then  upload an image (ideally it contains whatever you're trying to detect). If you're detection model finds an object in the image with > 70% confidence (I chose 70%, you can change it in the functions code), you should see something like the following written to your Firestore database:





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

