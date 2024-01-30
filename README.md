Look at this link for continuing trying: https://github.com/google-github-actions/auth?tab=readme-ov-file#indirect-wif

This has been done with research from multiple, at least 20 different sites.

# Testing FastAPI Deployment with GitHub Actions
The goal of this repository is to plan, design, and test the deployment of a FastAPI application into Google Cloud.

## Develop FastAPI application
The application in the repository is a very simple mock API done for purposes of testing.

## Build the application in a Docker image
Building a docker image with the help of a Dockerfile (look into it to understand what is occurring). Then run it. The idea eventually, will be to push it into Google Cloud Run.
```
docker build -t $NAME_OF_IMAGE .
```

Run the image with
```
docker run -p 80:80 $NAME_OF_IMAGE
```

Remember to commit and push changes to github repository once the Dockerfile is used and tested.

## Create a Google Cloud Project
1. Create project (if you have not)
2. Take a note or copy the ProjectID that is produced when creating the project (it will be needed further)
3. Make sure there is a billing account linked to the project

## GCloud set up (through the CLI)
### 1. If you want, in your terminal session create some environment variables for the ease of writing the scripts.
```
export PROJECT_ID=$YOUR_PROJECT_ID
export SERVICE_ACCOUNT_NAME=github-actions-service-account
export WORKLOAD_IDENTITY_POOL=gh-pool
export WORKLOAD_IDENTITY_PROVIDER=gh-provider
export REPO=username/name_of_repo
```

### 2. Now, lets start using the gcloud CLI
I would suggest to go to google and research how to download it and use it in your machine.
Once you can use it:
  - Make sure that you have set it up and when you run the command `gcloud init` you can reuse the previous configuration and log in with your account.
  - Set the project to be working with running the command `gcloud config set project $PROJECT_ID`

### 3. Enable the APIs that are needed for the project to work
We will use the Artifact Registry, IAM Credential, Container Registry and Cloud Run.

To accomplish it can be done with:
```
gcloud services enable \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  containerregistry.googleapis.com \
  run.googleapis.com
```

### 4. Create a Service Account that will be used by GitHub Actions
A service account is a special kind of account used by an application or compute workload, rather than a person. Service accounts are managed by Identity and Access Management (IAM).

In this case, it will be GitHub Actions the one interacting with our Google Cloud Project.

Run the following command to create the service account
```
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --project "${PROJECT_ID}" \
  --display-name="GitHub Actions Service Account"
```

<!---### 5. Bind the Service Account to the Roles that the Services must interact with
This is personally something new for me. However, I believe that this binds some roles to the service account so that different tasks can be accomplished later by this service account that we created. Which again, is the service account that github actions will be using.

**Service Account User**
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

**Developer User**
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.developer"
```

**Storage Admin**
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```
--->

### 6. Create a Workload Identity Pool for GitHub
A workload identity pool is an entity that lets you manage external identities. In general, we recommend creating a new pool for each non-Google Cloud environment that needs to access Google Cloud resources, such as development, staging, or production environments.

Run the command:
```
gcloud iam workload-identity-pools create $WORKLOAD_IDENTITY_POOL \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Pool"
```

### 7. Retrieve the Workload Identity Pool ID
I am not sure what is this, but I believe it's only getting the ID Google gave to the workload identity pool we inserted previously.

Run the command:
```
WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools \
  describe $WORKLOAD_IDENTITY_POOL \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)")
```

This value should be in the format of:
`projects/123456789/locations/global/workloadIdentityPools/github`

### 8. Create a Workload Identity Provider for GitHub
A workload identity pool provider is an entity that describes a relationship between Google Cloud and your IdP (Identity Provider).

Run the command:
```
gcloud iam workload-identity-pools providers create-oidc $WORKLOAD_IDENTITY_PROVIDER \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool=$WORKLOAD_IDENTITY_POOL \
  --display-name="GitHub Action Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

### 9. Allow authentications from the Workload Identity Provider originating from the repository
I would suggest putting the GitHub repository name in an environmental variable as it will be reused multiple times
```
export GITHUB_REPO_NAME=$NAME_OF_REPO
```

Then, run this command:
```
gcloud iam service-accounts add-iam-policy-binding \
  $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${REPO}"
```

### 10. Finally, extract the Workload Identity Provider resource name:
I believe this is mainly getting the location of the workload identity provider.

Run the following command:
```
WORKLOAD_IDENTITY_PROVIDER_LOCATION=$(gcloud iam workload-identity-pools providers \
  describe $WORKLOAD_IDENTITY_PROVIDER \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool=$WORKLOAD_IDENTITY_POOL \
  --format="value(name)")
```

<!---
** Important: We need to make the application public, therefore, give access to the service url. Run the following command: **
```
gcloud run services add-iam-policy-binding app \
  --member="allUsers" \
  --role="roles/run.invoker"
```
--->

### GitHub Actions Workflow
Before editing the GitHub action yml file, make sure to get the Workload Identity Provider Location and the Service Account URL

Run the commands:
- ```echo $WORKLOAD_IDENTITY_PROVIDER_LOCATION```
- ```echo $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com```

At this point, the best to do is to the GitHub action file itself. Then, study what is happening and read the comments





