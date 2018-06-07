# osha_ai

## Setup
Requisties: 
 -gcloud

## Deploying stub image producer

### setup compute instanse
Set: $PROJECT_ID and $SERVICE-ACCOUNT
TODO: Create configuration file which pulls in this information
```
gcloud beta compute --project=$PROJECT_ID instances create ml-pipeline-test-1 --zone=us-east1-b --machine-type=n1-standard-1 --subnet=default --network-tier=PREMIUM --maintenance-policy=MIGRATE --service-account=$SERVICE-ACCOUNT --scopes=https://www.googleapis.com/auth/cloud-platform --tags=http-server,https-server --image=ubuntu-1604-xenial-v20180522 --image-project=ubuntu-os-cloud --boot-disk-size=10GB --no-boot-disk-auto-delete --boot-disk-type=pd-standard --boot-disk-device-name=ml-pipeline-test-1
gcloud compute --project=$PROJECT_ID firewall-rules create default-allow-http --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:80 --source-ranges=0.0.0.0/0 --target-tags=http-server
gcloud compute --project=$PROJECT_ID firewall-rules create default-allow-https --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:443 --source-ranges=0.0.0.0/0 --target-tags=https-server
```
Change the networking:
- By default, the external IP address is dynamic and we need to make it static to make our life easier. Click on the three horizontal lines on top left and then under networking, click on VPC network and then External IP addresses.
- Create a firewall rule following these [instructions](https://cdn-images-1.medium.com/max/1600/1*R3jRo09kec4ygt1fUcZ_uA.png)

### access compute instance
To SSH in:
```
gcloud compute --project $PROJECT_ID ssh --zone "us-east1-b" "ml-pipeline-test-1"
```

### setup instance
```
yes | wget http://repo.continuum.io/archive/Anaconda3-4.0.0-Linux-x86_64.sh
bash Anaconda3-4.0.0-Linux-x86_64.sh
source ~/.bashrc
pip install tensorflow
pip install keras
jupyter notebook --generate-config
```
Modify the notebook config to include
```
c = get_config()
c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 5000
```
Launch jupyter notebook
```
jupyter-notebook --no-browser --port=5000
```

