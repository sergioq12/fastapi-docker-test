# Testing FastAPI Deployment with GitHub Actions
The goal of this repository is to plan, design, and test the deployment of a FastAPI application into Google Cloud.

## Steps to be made

### Develop FastAPI application
The application in the repository is a very simple mock API done for purposes of testing.

### Build the application in a Docker image
Building a docker image with the help of a Dockerfile (look into it to understand what is occurring). Then run it. The idea eventually, will be to push it into Google Cloud Run.
```
docker build -t $NAME_OF_IMAGE .
```

Run the image with
```
docker run -p 80:80 $NAME_OF_IMAGE
```

Remember to commit and push changes to github repository once the Dockerfile is used and tested.

### Create a Google Cloud Project
1. Create project (if you have not)
2. Take a note or copy the ProjectID that is produced when creating the project (it will be needed further)
3. Make sure there is a billing account linked to the project

### GCloud set up (through the CLI)
1. If you want, in your terminal session create some environment variables for the ease of writing the scripts.
```
export PROJECT_ID=$YOUR_PROJECT_ID
export SERVICE_ACCOUNT_NAME=github-actions-service-account
export WORKLOAD_IDENTITY_POOL=gh-pool
export WORKLOAD_IDENTITY_PROVIDER=gh-provider
```

2. Now, lets start using the gcloud CLI
I would suggest to go to google and research how to download it and use it in your machine.
Once you can use it:
  - Make sure that you have set it up and when you run the command `gcloud init` you can reuse the previous configuration and log in with your account.
  - Set the project to be working with running the command `gcloud config set project $PROJECT_ID`





