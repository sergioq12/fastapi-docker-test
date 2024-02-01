This has been done with research from multiple, at least 20 different sites. I am so happy right now.

# Testing FastAPI Deployment with GitHub Actions (Cloud Run Deployment From Source)
The goal of this repository is to plan, design, and test the deployment of a FastAPI application into Google Cloud.

## Develop FastAPI application
The application in the repository is a very simple mock API done for purposes of testing.

## Build the application in a Docker image (To test it Locally)
Building a docker image with the help of a Dockerfile (look into it to understand what is occurring). Then run it. The idea eventually, will be to push it into Google Cloud Run.
```
docker build -t $NAME_OF_IMAGE .
```

Run the image with
```
docker run -p 80:80 $NAME_OF_IMAGE
```

Remember to commit and push changes to GitHub repository once the Dockerfile is used and tested.

## Create a Google Cloud Project
1. Create a project (if you have not)
2. Take a note or copy the ProjectID that is produced when creating the project (it will be needed further)
3. Make sure there is a billing account linked to the project (it should be set by default if you already have a billing account created)

## GCloud set up (through the CLI)
### 1. If you want, in your terminal session create some environment variables for the ease of writing the scripts.
```
export PROJECT_ID=$YOUR_PROJECT_ID
export SERVICE_ACCOUNT_NAME=github-actions-service-account
export WORKLOAD_IDENTITY_POOL=github
export WORKLOAD_IDENTITY_PROVIDER=gha-provider
export REPO=username/name_of_repo
export REGION=us-east4
```
Note: us-east4 is the region for Northern Virginia (closest to me at the time)

### 2. Now, let's start using the GCloud CLI
I would suggest going to Google and researching how to download it and use it on your machine.
Once you can use it:
  - Make sure that you have set it up and when you run the command `gcloud init` you can reuse the previous configuration and log in with your account.
  - Set the project to be working by running the command `gcloud config set project $PROJECT_ID`

### 3. Enable the APIs that are needed for the project to work
We will use the Artifact Registry, IAM Credential, Cloud Build, and Cloud Run.

To accomplish it can be done with:
```
gcloud services enable \
  artifactregistry.googleapis.com \
  iamcredentials.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com
```
Note: Check in the GCP Web App that the IAM Service Credentials API is enabled as well!!
--> https://console.cloud.google.com/apis/api/iamcredentials.googleapis.com

### 4. Create a Service Account that will be used by GitHub Actions
A service account is a special kind of account used by an application or compute workload, rather than a person. Service accounts are managed by Identity and Access Management (IAM).

In this case, it will be GitHub Actions the one interacting with our Google Cloud Project.

Run the following command to create the service account
```
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --project "${PROJECT_ID}" \
  --display-name="GitHub Actions Service Account"
```

You can check that it was created with:
```
gcloud iam service-accounts list
```

### 5. Create a Workload Identity Pool for GitHub
A workload identity pool is an entity that lets you manage external identities. In general, we recommend creating a new pool for each non-Google Cloud environment that needs to access Google Cloud resources, such as development, staging, or production environments.

Run the command:
```
gcloud iam workload-identity-pools create $WORKLOAD_IDENTITY_POOL \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool"
```

### 6. Retrieve the Workload Identity Pool ID
I am not sure what is this, but I believe it's only getting the ID Google gave to the workload identity pool we inserted previously.

Run the command:
```
gcloud iam workload-identity-pools \
  describe $WORKLOAD_IDENTITY_POOL \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)"
```

This value should be in the format of:
`projects/123456789/locations/global/workloadIdentityPools/github`

Ideally, save it in an environmental variable called WORKLOAD_IDENTITY_POOL_ID

### 7. Create a Workload Identity Provider for GitHub
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

### 8. Allow authentications from the Workload Identity Provider originating from the repository
I believe this binds the github repository to the given service account so that it is allowed to be a workload identity user

```
gcloud iam service-accounts add-iam-policy-binding \
  $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${REPO}"
```
Note: $WORKLOAD_IDENTITY_POOL_ID refers to the string that was given by step #6

### 9. Extract the Workload Identity Provider resource name:
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

The value should be in the format of:
`projects/523245282810/locations/global/workloadIdentityPools/github/providers/github-actions-provider`

### 10. Bind the Service Account to the Roles that the Service Account needs

**This is CRUCIAL for the deployment to go correctly.**

You need to add the following roles to the service account:

**Service Account User**
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```
Note: Once you run this, the service account will start to appear in the GCP Web App

**Cloud Run Admin**
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

**Artifact Registry Admin**
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.admin"
```

**Storage Admin**
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

**Cloud Build Builds Editor**
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"
```


### GitHub Actions Workflow

We used the example workflow **Deploy To Cloud Run From Source**
Found in --> Go to your Repository > Actions > New Workflow > Search Cloud Run and choose the one with the name shown above.

Before editing the GitHub action yml file, make sure to get the Workload Identity Provider Location and the Service Account URL

Run the commands:
- `echo $WORKLOAD_IDENTITY_PROVIDER_LOCATION`
- `echo $SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com`

I strongly suggest making them repository secrets and then in the GitHub action refer to them as:
```
...
name: Google Auth
        id: auth
        uses: 'google-github-actions/auth@v2'
        with:
          workload_identity_provider: '${{ secrets.WIF_PROVIDER }}'
          service_account: '${{ secrets.WIF_SERVICE_ACCOUNT }}'
...
```

At this point, the best to do is to the GitHub action file itself, using the template shared. 

Some notes on things we had to change:
- Make sure to change the `uses: actions/checkout@v2` to `uses: actions/checkout@v4`
- Make sure to change the `google-github-actions/auth@v0` to `google-github-actions/auth@v2`
- Make sure to change the `google-github-actions/deploy-cloudrun@v0` to `google-github-actions/deploy-cloudrun@v2`

**Important: We need to make the application public, therefore, give access to the service URL. Run the following command:**
```
gcloud run services add-iam-policy-binding $NAME_OF_SERVICE_OF_CLOUD_RUN \
  --member="allUsers" \
  --role="roles/run.invoker"
```
Note: the name of the service of Cloud Run is the same name that is given in the GitHub action. It can also be found on the Google Cloud Run API page, and it will be the name of the deployed service.

If the previous command is not run, the app will be deployed but it won't be able to be accessed publicly by any user.

# Additional Notes

### What can you do when you want to shutdown, cut, or just don't allow users to insert your deployed application in Cloud Run?
After some research, the best thing you can do is make the app 'private'. This means disable the `allUsers` configuration in the **Cloud Run Invoker permission**. To accomplish I suggest going to your GCP project in the web app. Then, go search the **Cloud Run API**. Once you are there, click on the service running. Once inside go to **Security** tab, and in the **Authentication** card/board make the configuration to --> Require Authentication. This will disable the ability for public users to enter the application, only users with custom project saved authentication.



