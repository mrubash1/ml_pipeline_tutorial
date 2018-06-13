# ML_Pipeline_Tutorial

### Requisites
- gcloud command line tool
- set the [google application credentials](https://cloud.google.com/docs/authentication/getting-started)
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
python src/python/stub_image_uploader.py \
  --project=myproject-204318 \
  --bucket_name='ml_pipeline_tutorial_v0' \
  --local_filename='/Users/mattrubashkin/ml_pipeline_tutorial/data/caltrain.jpg' \
  --output_name='caltrain'
```



