## Deploy LambdaYamlToJson tool

### Step 0: Open AWS Lambda Console

Open [Console](https://console.aws.amazon.com/lambda/home), confirm the Region in the right up corner is right.


### Step 1: Create a Lambda Layer
- Download the [layer file](./lambda_yaml_to_json/pyyaml-layer-2a8a5288-fd9a-4177-bda9-7d7c0e91905c.zip) into local computer
- Click `Layers` in the left nav panel
- Click `Create layer`
    - Name: pyyaml-layer
    - Upload the .zip file
    - Compatible architectures: x86_64
    - Compatible runtimes: Python 3.12

### Step 2: Create the Lambda Function
- Download the [Lambda code](./lambda_yaml_to_json/yaml_to_json-cc18ca28-6010-442e-9a86-f128d285d179.zip) into local computer
- Click `Functions` in the left nav panel
- Click `Create function`
- Choose `Author from scratch`
    - Function name: yaml_to_json
    - Runtime: Python 3.12
    - Architecture: x86_64
- Click `Create function`
- In the `Code` tab:
    - Choose `Upload from` / `.zip file`
    - Upload the .zip file
- In the `Configuration` tab:
    - Click `General configuration`
    - Click `Edit` and increase `Timeout` to 30 sec
