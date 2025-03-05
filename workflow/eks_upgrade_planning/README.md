# EKS Upgrade Planning with LLM

This project is a tool that leverages Large Language Models (LLMs) to generate Amazon EKS (Elastic Kubernetes Service) cluster upgrade plans. It collects EKS cluster information using the `eks_cluster_info.py` script and feeds this data into a GenAI workflow defined in `eks_upgrade_planning.yml` to produce comprehensive upgrade plans.

## Overview

The EKS Upgrade Planning Tool consists of two main components:

1. **EKS Cluster Information Collector (`eks_cluster_info.py`)**: A Python script that gathers detailed information about an EKS cluster, including its current version, health status, compatibility issues, and more.

2. **Dify Workflow Definition (`eks_upgrade_planning.yml`)**: A workflow configuration file that defines how the collected cluster information is processed by Claude (Anthropic's LLM) to generate a structured upgrade plan.

## Features

- **Comprehensive Cluster Information Collection**:
  - Current EKS version
  - Cluster health issues
  - Compatibility issues with target versions
  - EKS add-on compatibility
  - Version skew detection (kubelet, kube-proxy)
  - Deprecated API usage detection
  - Nodegroup and Fargate profile information
  - Self-managed nodes and Karpenter nodes version info
  - Self-managed addons

- **Intelligent Upgrade Planning**:
  - Version-specific upgrade recommendations
  - Control plane upgrade steps
  - Data plane (nodegroups) upgrade guidance
  - Add-on compatibility and upgrade paths
  - API version migration recommendations
  - Health issue remediation suggestions
  - Testing and validation guidance

## Prerequisites

- Python 3.6+
- AWS API client environment configured with appropriate EKS access permissions
- boto3 library 1.36.26+
- Access to Dify platform for workflow execution

## Installation

1. Clone this repository or download the script files.
2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Usage

### Step 1: Collect EKS Cluster Information

Run the `eks_cluster_info.py` script with the following parameters:

- `cluster_name`: Name of the EKS cluster
- `target_version`: Target EKS version for compatibility checks
- `--region` (optional): AWS region
- `--profile` (optional): AWS profile to use
- `--connect-k8s` (optional): Connect to Kubernetes API server to collect additional information

You will need Kubernetes permissions to run the script with `--connect-k8s`

Example:

```
python eks_cluster_info.py my-cluster 1.24 --region us-west-2 --connect-k8s
```

### Step 2: Use the Collected Information with the Dify Workflow

1. Copy the output from the `eks_cluster_info.py` script.
2. Import the `eks_upgrade_planning.yml` workflow definition into your Dify instance.
3. Start a new conversation in the workflow and paste the collected cluster information.
4. Select the target EKS version.
5. The workflow will process the information and generate a comprehensive upgrade plan.

## Workflow Structure

The `eks_upgrade_planning.yml` defines a Dify workflow that:

1. Extracts parameters from the cluster information input
2. Fetches relevant AWS documentation for reference
3. Analyzes various aspects of the upgrade:
   - Cluster health issues
   - Add-on compatibility
   - Version-specific changes
   - Deprecated API usage
   - Nodegroup and Fargate considerations
4. Generates a structured upgrade plan with specific recommendations for each component

## Output

The tool generates a comprehensive upgrade plan that includes:

- **Cluster Information Summary**
- **Pre-upgrade Checks**:
  - Version-specific changes and recommendations
  - Kubelet and kube-proxy version alignment
  - Add-on compatibility checks
  - Kubernetes API version compatibility
  - Cluster health checks and remediation
- **Control Plane Upgrade Steps**
- **Add-on Upgrade Guidance**
- **Data Plane Upgrade Instructions**
- **Testing and Validation Recommendations**

## Notes

- Ensure your AWS credentials are properly configured with sufficient permissions to access EKS resources.
- The script uses AWS EKS's describe_cluster, list-insights and describe-insight etc APIs to obtain compatibility information, providing more accurate and detailed insights.
- This tool provides a comprehensive EKS cluster information collection and upgrade planning capability that can be further customized and extended based on specific requirements.

## Contributing

Questions, suggestions, or code contributions to improve this tool are welcome. Please feel free to create issues or submit pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
