# FloTorch Postman Collection 🧑‍🚀

This folder contains the **Postman collection** and **environment templates** for the FloTorch API. It is designed to let you run all API requests for multiple cloud platforms (AWS, GCP, Azure).

## Folder Structure

```bash
postman/
├─ collections/
├─── flotorch.postman_collection.json           # collection file
├─ environments/                        
├─── aws.postman_environment.json.example
├─── azure.postman_environment.json.example     # environment files
└─── gcp.postman_environment.json.example
```

- `flotorch.postman_collection.json` – The main Postman collection containing all requests.
- `{cloud_platform}.postman_environment.json.example` – Template environment file with placeholders (do **not** commit real API keys).

## Setup Instructions

### 1. Import the collection

1. Open Postman.

2. Go to **File → Import → Upload Files**.

3. Select `flotorch.postman_collection.json`.

4. The collection will appear in your workspace.

### 2. Create your environment

1. Duplicate the example environment files based on the cloud platforms you're using.

    `aws.postman_environment.json.example` → `your_project.postman_environment.json`

2. Open Postman → **Environments → Import**.

3. Select your environment file.

4. Add your real values:

   - `flotorch_base_url` → Cloud platorm-specific FloTorch base URL (This should be filled in already)
   - `flotorch_api_key` → Your FloTorch API key
   - Any other variables as needed

> We recommend you create a seperate Postman environment for each FloTorch workspace you are a part of to keep things tidy.

### 3. Select the environment

- In Postman, select your newly created environment from the top-right dropdown.
- All requests in the collection now use the variables from this environment.

### 4. Using the requests

- All requests are platform-agnostic; the `{{flotorch_base_url}}` variable switches between cloud platforms.
- The collection is organized in folders by resource (Models, Agents, Workflows, etc.).
- Utilize the path variables to easily insert resource names and IDs into the request URL.
- Pre-request scripts and tests run automatically as defined in the collection.

## ⚠️ Security Note

- **Never commit your real `postman_environment.json` file.**
- Only commit the `postman_environment.json.example` file to GitHub if necessary.

## Optional: Running with Newman

If you want to run the collection via CLI:

```bash
# Install Newman if needed
npm install -g newman

# Run the collection with your local environment
newman run tools/postman/flotorch.postman_collection.json \
    -e tools/postman/environments/your_postman_environment.json \
    --reporters cli,html
```

- This will execute all requests and generate a CLI and HTML report.
- Useful for CI/CD pipelines or automated testing.

## Adding New Requests

1. Add requests to the appropriate folder in the collection. Create new folders for new resource types if needed.
2. Use `{{flotorch_base_url}}` in the request URL instead of hardcoding gateway URLs.
3. Use path variables in the request url to insert resource-specific values.
4. Use environment variables for tokens, API keys, or dynamic values.
