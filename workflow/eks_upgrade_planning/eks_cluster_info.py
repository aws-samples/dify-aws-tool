import boto3
import argparse
import sys
import base64
import tempfile
import os
from botocore.exceptions import ClientError
from kubernetes import client

URL_TIMEOUT = 60
TOKEN_EXPIRATION_MINS = 14
TOKEN_PREFIX = 'k8s-aws-v1.'
K8S_AWS_ID_HEADER = 'x-k8s-aws-id'

class TokenGenerator(object):
    def __init__(self, sts_client):
        self._sts_client = sts_client

    def get_token(self, k8s_aws_id):
        """Generate a presigned url token to pass to kubectl."""
        url = self._get_presigned_url(k8s_aws_id)
        token = TOKEN_PREFIX + base64.urlsafe_b64encode(
            url.encode('utf-8')
        ).decode('utf-8').rstrip('=')
        return token

    def _get_presigned_url(self, k8s_aws_id):
        return self._sts_client.generate_presigned_url(
            'get_caller_identity',
            Params={K8S_AWS_ID_HEADER: k8s_aws_id},
            ExpiresIn=URL_TIMEOUT,
            HttpMethod='GET',
        )

class STSClientFactory(object):
    def __init__(self, session):
        self._session = session

    def get_sts_client(self, region_name=None, role_arn=None):
        client_kwargs = {'region_name': region_name}
        if role_arn is not None:
            creds = self._get_role_credentials(region_name, role_arn)
            client_kwargs['aws_access_key_id'] = creds['AccessKeyId']
            client_kwargs['aws_secret_access_key'] = creds['SecretAccessKey']
            client_kwargs['aws_session_token'] = creds['SessionToken']
        sts = self._session.client('sts', **client_kwargs)
        self._register_k8s_aws_id_handlers(sts)
        return sts

    def _get_role_credentials(self, region_name, role_arn):
        sts = self._session.create_client('sts', region_name)
        return sts.assume_role(
            RoleArn=role_arn, RoleSessionName='EKSGetTokenAuth'
        )['Credentials']

    def _register_k8s_aws_id_handlers(self, sts_client):
        sts_client.meta.events.register(
            'provide-client-params.sts.GetCallerIdentity',
            self._retrieve_k8s_aws_id,
        )
        sts_client.meta.events.register(
            'before-sign.sts.GetCallerIdentity',
            self._inject_k8s_aws_id_header,
        )

    def _retrieve_k8s_aws_id(self, params, context, **kwargs):
        if K8S_AWS_ID_HEADER in params:
            context[K8S_AWS_ID_HEADER] = params.pop(K8S_AWS_ID_HEADER)

    def _inject_k8s_aws_id_header(self, request, **kwargs):
        if K8S_AWS_ID_HEADER in request.context:
            request.headers[K8S_AWS_ID_HEADER] = request.context[K8S_AWS_ID_HEADER]

def get_cluster_info(cluster_name, region, profile=None):
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    eks_client = session.client('eks', region_name=region)
    try:
        response = eks_client.describe_cluster(name=cluster_name)
        return response['cluster']
    except ClientError as e:
        print(f"Error getting cluster info: {e}")
        sys.exit(1)

def get_current_version(cluster_info):
    return cluster_info['version']

def get_health_issues(cluster_info):
    return cluster_info.get('health', {}).get('issues', [])

def get_compatibility_issues(cluster_name, region, profile=None):
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    eks_client = session.client('eks', region_name=region)
    try:
        insights = eks_client.list_insights(clusterName=cluster_name)['insights']
        compatibility_issues = []
        for insight in insights:
            if insight.get('category') == 'UPGRADE_READINESS':
                try:
                    detail = eks_client.describe_insight(clusterName=cluster_name, id=insight['id'])['insight']
                    issue = {
                        'name': detail.get('name', 'Unknown'),
                        'status': detail.get('insightStatus', {}).get('status', 'Unknown'),
                        'reason': detail.get('insightStatus', {}).get('reason', 'No reason provided'),
                        'recommendation': detail.get('recommendation', 'No recommendation available'),
                        'additionalInfo': detail.get('additionalInfo', {}),
                        'resources': detail.get('resources', []),
                        'categorySpecificSummary': detail.get('categorySpecificSummary', {})
                    }
                    compatibility_issues.append(issue)
                except ClientError as e:
                    print(f"Error describing insight {insight['id']}: {e}")
        return compatibility_issues
    except ClientError as e:
        print(f"Error listing insights: {e}")
        return []
    except KeyError as e:
        print(f"Unexpected response structure from list_insights: {e}")
        return []

def get_addon_compatibility_issues(compatibility_issues):
    addon_issues = []
    for issue in compatibility_issues:
        if issue['name'] == 'EKS add-on version compatibility':
            for resource in issue['resources']:
                if resource['insightStatus']['status'] == 'ERROR':
                    addon_issues.append({
                        'name': resource['arn'].split('/')[-2],
                        'status': resource['insightStatus']['status'],
                        'reason': resource['insightStatus']['reason']
                    })
    return addon_issues

def get_addon_compatible_versions(compatibility_issues):
    for issue in compatibility_issues:
        if issue['name'] == 'EKS add-on version compatibility':
            return issue['categorySpecificSummary'].get('addonCompatibilityDetails', [])
    return []

def get_deprecated_api_versions(compatibility_issues):
    deprecated_apis = []
    for issue in compatibility_issues:
        if issue['name'] == 'Deprecated APIs removed in Kubernetes v1.32':
            for detail in issue['categorySpecificSummary'].get('deprecationDetails', []):
                deprecated_apis.append({
                    'usage': detail['usage'],
                    'replacedWith': detail['replacedWith'],
                    'stopServingVersion': detail['stopServingVersion'],
                    'startServingReplacementVersion': detail['startServingReplacementVersion'],
                    'clientStats': detail['clientStats']
                })
    return deprecated_apis

def get_nodegroups(cluster_name, region, profile=None):
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    eks_client = session.client('eks', region_name=region)
    try:
        response = eks_client.list_nodegroups(clusterName=cluster_name)
        nodegroups = []
        min_version = None
        for ng_name in response['nodegroups']:
            ng_info = eks_client.describe_nodegroup(clusterName=cluster_name, nodegroupName=ng_name)
            version = ng_info['nodegroup']['version']
            nodegroups.append({
                'name': ng_name,
                'version': version
            })
            if min_version is None or version < min_version:
                min_version = version
        return nodegroups, min_version
    except ClientError as e:
        print(f"Error getting nodegroups: {e}")
        return [], None

def get_fargate_profiles(cluster_name, region, profile=None):
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    eks_client = session.client('eks', region_name=region)
    try:
        response = eks_client.list_fargate_profiles(clusterName=cluster_name)
        return response['fargateProfileNames']
    except ClientError as e:
        print(f"Error getting Fargate profiles: {e}")
        return []

def get_installed_addons(cluster_name, region, profile=None):
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    eks_client = session.client('eks', region_name=region)
    try:
        response = eks_client.list_addons(clusterName=cluster_name)
        addons = []
        for addon_name in response['addons']:
            addon_info = eks_client.describe_addon(clusterName=cluster_name, addonName=addon_name)
            addons.append({
                'name': addon_name,
                'version': addon_info['addon']['addonVersion']
            })
        return addons
    except ClientError as e:
        print(f"Error getting installed addons: {e}")
        return []

def get_addon_upgrade_info(cluster_name, region, current_version, target_version, profile=None):
    """
    Get addon upgrade compatibility information for EKS cluster.
    
    Args:
        cluster_name (str): Name of the EKS cluster
        region (str): AWS region
        current_version (str): Current Kubernetes version (e.g., '1.24')
        target_version (str): Target Kubernetes version (e.g., '1.25')
        profile (str, optional): AWS profile name
        
    Returns:
        tuple: (List of addon information dictionaries, boolean indicating if upgrade is recommended)
    """
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    eks_client = session.client('eks', region_name=region)
    
    # Get installed addons once
    try:
        installed_addons = get_installed_addons(cluster_name, region, profile)
    except Exception as e:
        print(f"Error getting installed addons: {e}")
        return [], False

    addon_upgrade_info = []
    upgrade_recommended = True

    # Parse versions
    current_major, current_minor = map(int, current_version.split('.')[:2])
    target_major, target_minor = map(int, target_version.split('.')[:2])
    
    # Generate version range from current to target (inclusive)
    versions = []
    for major in range(current_major, target_major + 1):
        min_minor = current_minor if major == current_major else 0
        max_minor = target_minor if major == target_major else 13
        for minor in range(min_minor, max_minor + 1):
            versions.append(f"{major}.{minor}")

    # Batch process addons
    for addon in installed_addons:
        addon_info = {
            'name': addon['name'],
            'current_version': addon['version']
        }
        
        try:
            # Get all compatible versions in one call per Kubernetes version
            compatible_versions = {}
            target_compatible = False
            
            for k8s_version in versions:
                response = eks_client.describe_addon_versions(
                    kubernetesVersion=k8s_version,
                    addonName=addon['name']
                )
                
                if not response.get('addons'):
                    # No compatible versions for this K8s version
                    compatible_versions[k8s_version] = []
                    continue
                
                # Extract versions
                version_list = [
                    v['addonVersion'].split('-')[0]
                    for v in response['addons'][0].get('addonVersions', [])
                    if v.get('compatibilities')
                ]
                
                compatible_versions[k8s_version] = version_list
                
                # Check if target version is compatible
                if k8s_version == target_version and version_list:
                    target_compatible = True
            
            # Check if there are any compatible versions
            has_versions = any(versions for versions in compatible_versions.values())
            
            if not has_versions:
                # No compatible versions for any K8s version
                addon_info['status'] = 'No compatible versions found for any Kubernetes version'
                addon_info['suggested_version_range'] = 'No supported version'
                upgrade_recommended = False
            elif not target_compatible:
                # Not compatible with target version
                addon_info['status'] = f'Not compatible with target version {target_version}'
                addon_info['suggested_version_range'] = 'No supported version'
                upgrade_recommended = False
            else:
                # Find versions compatible with all non-empty K8s versions
                non_empty_versions = {k: v for k, v in compatible_versions.items() if v}
                
                if non_empty_versions:
                    common_versions = set.intersection(*map(set, non_empty_versions.values()))
                    
                    if common_versions:
                        min_suggested = min(common_versions)
                        max_suggested = max(common_versions)
                        current_version_stripped = addon['version'].split('-')[0]
                        
                        # Compare versions using tuples for more accurate semantic versioning comparison
                        def version_to_tuple(v):
                            # Remove 'v' prefix if present
                            v = v.lstrip('v')
                            # Handle potential non-numeric parts
                            parts = []
                            for part in v.split('.'):
                                try:
                                    parts.append(int(part))
                                except ValueError:
                                    # If conversion fails, just use 0
                                    parts.append(0)
                            return tuple(parts)
                            
                        min_suggested_tuple = version_to_tuple(min_suggested)
                        max_suggested_tuple = version_to_tuple(max_suggested)
                        current_version_tuple = version_to_tuple(current_version_stripped)
                        
                        addon_info.update({
                            'suggested_version_range': f"{min_suggested} to {max_suggested}",
                            'status': 'Upgrade recommended' if (
                                current_version_tuple < min_suggested_tuple or 
                                current_version_tuple > max_suggested_tuple
                            ) else 'Compatible'
                        })
                    else:
                        addon_info['status'] = 'No common compatible version found across all Kubernetes versions'
                        addon_info['suggested_version_range'] = 'No supported version'
                        upgrade_recommended = False
                else:
                    addon_info['status'] = 'No compatible versions found'
                    addon_info['suggested_version_range'] = 'No supported version'
                    upgrade_recommended = False
            
            # Add information about compatible versions for each K8s version
            addon_info['compatible_versions'] = compatible_versions

        except ClientError as e:
            print(f"AWS API Error checking addon {addon['name']} compatibility: {e}")
            addon_info['status'] = f"Error checking compatibility: {e.response['Error']['Code']}"
            upgrade_recommended = False
        except Exception as e:
            print(f"Unexpected error checking addon {addon['name']} compatibility: {e}")
            addon_info['status'] = 'Unexpected error during compatibility check'
            upgrade_recommended = False

        addon_upgrade_info.append(addon_info)

    return addon_upgrade_info, upgrade_recommended

def check_version_skew(current_version, min_nodegroup_version, kube_proxy_version, target_version):
    """
    Check version skew between nodegroup, kube-proxy, and target version.
    
    Args:
        current_version (str): Current EKS version
        min_nodegroup_version (str): Minimum nodegroup version
        kube_proxy_version (str): kube-proxy addon version
        target_version (str): Target Kubernetes version
        
    Returns:
        tuple: (boolean indicating if upgrade is recommended, list of recommendations)
    """
    def parse_version(version):
        # Remove 'v' prefix if present and split by '.'
        return tuple(map(int, version.lstrip('v').split('.')[:2]))

    upgrade_recommended = False
    recommendations = []
    
    # Convert versions to tuples for comparison
    current = parse_version(current_version)
    min_nodegroup = parse_version(min_nodegroup_version) if min_nodegroup_version else None
    kube_proxy = parse_version(kube_proxy_version) if kube_proxy_version else None
    target = parse_version(target_version)
    
    # Determine the allowed version difference
    if current >= (1, 28):
        allowed_diff = 3
    else:
        allowed_diff = 2
    
    # Check nodegroup version
    if min_nodegroup and target[1] - min_nodegroup[1] > allowed_diff:
        upgrade_recommended = True
        recommendations.append(f"Nodegroup incompatible with target version. Upgrade nodegroup to at least {current_version}")
    
    # Check kube-proxy version
    if kube_proxy and target[1] - kube_proxy[1] > allowed_diff:
        upgrade_recommended = True
        recommendations.append(f"Kube-proxy incompatible with target version. Upgrade kube-proxy addon from {kube_proxy_version} to at least {current_version}")
    
    return upgrade_recommended, recommendations

def create_temp_cert_file(cert_data):
    try:
        # Create a temporary file with a reasonable name length
        cert_file = tempfile.NamedTemporaryFile(delete=False, suffix='.crt')
        cert_file.write(base64.b64decode(cert_data))
        cert_file.close()
        return cert_file.name
    except Exception as e:
        raise Exception(f"Failed to create certificate file: {e}")
    
def validate_target_version(current_version, target_version):
    """
    Validate that the target version is greater than the current version
    and less than or equal to current version + 3.
    
    Args:
        current_version (str): Current Kubernetes version (e.g., '1.24')
        target_version (str): Target Kubernetes version (e.g., '1.27')
        
    Returns:
        tuple: (boolean indicating if valid, error message if invalid)
    """
    try:
        # Parse versions
        current_major, current_minor = map(int, current_version.split('.')[:2])
        target_major, target_minor = map(int, target_version.split('.')[:2])
        
        # Check if target version is greater than current version
        if target_major < current_major or (target_major == current_major and target_minor <= current_minor):
            return False, f"Target version {target_version} must be greater than current version {current_version}"
        
        # Check if target version is less than or equal to current version + 3
        if target_major == current_major:
            version_diff = target_minor - current_minor
        else:
            # Handle major version difference
            version_diff = (target_major - current_major) * 100 + (target_minor - current_minor)
            
        if version_diff > 3:
            return False, f"Target version {target_version} must be less than or equal to 3 minor versions higher than current version {current_version}"
            
        return True, ""
    except Exception as e:
        return False, f"Error validating versions: {e}"

def connect_to_cluster(cluster_name, region=None, profile=None):
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    client_factory = STSClientFactory(session)
    sts_client = client_factory.get_sts_client(
        region_name=region
    )
    eks_client = session.client('eks', region_name=region)

    try:
        cluster_info = eks_client.describe_cluster(name=cluster_name)
        cluster = cluster_info['cluster']
        cert_data = cluster['certificateAuthority']['data']
        endpoint = cluster['endpoint']
        token = TokenGenerator(sts_client).get_token(cluster_name)
        # print(f"{token}")

        # Create temporary certificate file
        cert_file_path = create_temp_cert_file(cert_data)

        configuration = client.Configuration()
        configuration.host = endpoint
        configuration.api_key['authorization'] = f"Bearer {token}"
        configuration.verify_ssl = True
        configuration.ssl_ca_cert = cert_file_path

        api_client = client.ApiClient(configuration)
        v1 = client.CoreV1Api(api_client)
        
        try:
            v1.list_namespace()
            # print("Successfully connected to the cluster")
            return api_client
        except client.rest.ApiException as e:
            print(f"Failed to list namespaces: {e}")
            return None
        finally:
            # Clean up the temporary certificate file
            try:
                os.unlink(cert_file_path)
            except:
                pass
    except Exception as e:
        print(f"Error connecting to cluster: {e}")
        return None
    
def get_node_versions(api_client):
    """
    Get minimum versions of self-managed nodes and Karpenter nodes in the cluster.
    Optimized for large scale clusters by using label selectors and pagination.
    
    Args:
        api_client: Kubernetes API client
        
    Returns:
        tuple: (min_self_managed_version, min_karpenter_version, self_managed_count, karpenter_count)
    """
    if not api_client:
        return None, None, 0, 0
    
    try:
        v1 = client.CoreV1Api(api_client)
        
        # Set timeout and retry parameters
        timeout_seconds = 30
        max_retries = 3
        retry_delay = 2  # seconds
        
        # Use pagination to handle large clusters
        continue_token = None
        limit = 100  # Number of nodes to fetch per request
        
        self_managed_versions = []
        karpenter_versions = []
        
        # Process nodes in batches to avoid memory issues
        while True:
            try:
                # Add timeout and retry mechanism
                for attempt in range(max_retries):
                    try:
                        nodes = v1.list_node(
                            limit=limit,
                            _continue=continue_token,
                            timeout_seconds=timeout_seconds
                        )
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(retry_delay)
                            continue
                        raise e
                
                for node in nodes.items:
                    version = node.status.node_info.kubelet_version
                    labels = node.metadata.labels
                    
                    # Check if node is managed by Karpenter
                    if "karpenter.sh/provisioner-name" in labels or "karpenter.sh/nodepool" in labels:
                        karpenter_versions.append(version)
                    # Check if node is not managed by EKS (no eks.amazonaws.com/nodegroup label)
                    elif not any(label.startswith("eks.amazonaws.com/nodegroup") for label in labels):
                        self_managed_versions.append(version)
                
                # Check if there are more nodes to fetch
                continue_token = nodes.metadata._continue
                if not continue_token:
                    break
                    
            except Exception as e:
                print(f"Error fetching nodes batch: {e}")
                break
        
        # Get minimum versions if available
        min_self_managed_version = min(self_managed_versions) if self_managed_versions else None
        min_karpenter_version = min(karpenter_versions) if karpenter_versions else None
        
        return min_self_managed_version, min_karpenter_version, len(self_managed_versions), len(karpenter_versions)
    except Exception as e:
        print(f"Error getting node versions: {e}")
        return None, None, 0, 0

def get_opensource_addons(api_client, eks_addons=None):
    """
    Get information about opensource addons in the cluster.
    Check if they are installed by Helm and get their chart and app versions from labels.
    Optimized for large scale clusters by using batch operations and field selectors.
    
    Args:
        api_client: Kubernetes API client
        eks_addons: List of EKS addons to skip (optional)
        
    Returns:
        list: List of dictionaries containing addon name, version, and Helm info if available
    """
    if not api_client:
        return []
    
    # Extract EKS addon names if provided
    eks_addon_names = [addon['name'] for addon in eks_addons] if eks_addons else []
    
    try:
        apps_v1 = client.AppsV1Api(api_client)
        
        # Common Opensource Addons
        addons = []
        
        # Define the list of addons to check
        addon_configs = [
            {"name": "metrics-server", "namespace": "kube-system", "kind": "deployment", "eks_addon_name": "metrics-server"},
            {"name": "cluster-autoscaler", "namespace": "kube-system", "kind": "deployment", "eks_addon_name": None},
            {"name": "karpenter", "namespace": "karpenter", "kind": "deployment", "eks_addon_name": None},
            {"name": "karpenter", "namespace": "kube-system", "kind": "deployment", "eks_addon_name": None},
            {"name": "aws-load-balancer-controller", "namespace": "kube-system", "kind": "deployment", "eks_addon_name": None},
            {"name": "external-dns", "namespace": "kube-system", "kind": "deployment", "eks_addon_name": None},
            {"name": "cert-manager", "namespace": "cert-manager", "kind": "deployment", "eks_addon_name": None},
            {"name": "ingress-nginx-controller", "namespace": "ingress-nginx", "kind": "deployment", "display_name": "ingress-nginx", "eks_addon_name": None},
            {"name": "adot-collector", "namespace": "adot-system", "kind": "deployment", "display_name": "adot", "eks_addon_name": "adot"},
            {"name": "cloudwatch-observability-operator", "namespace": "amazon-cloudwatch", "kind": "deployment", "display_name": "Amazon CloudWatch Observability", "eks_addon_name": "amazon-cloudwatch-observability"},
            {"name": "sagemaker-hyperpod-task-governance", "namespace": "kube-system", "kind": "deployment", "display_name": "Amazon SageMaker HyperPod task governance", "eks_addon_name": "amazon-sagemaker-hyperpod-taskgovernance"},
            {"name": "aws-guardduty-agent", "namespace": "amazon-guardduty", "kind": "daemonset", "display_name": "Amazon GuardDuty EKS Runtime Monitoring", "eks_addon_name": "aws-guardduty-agent"},
            {"name": "mountpoint-s3-csi-controller", "namespace": "kube-system", "kind": "deployment", "display_name": "Mountpoint for Amazon S3 CSI Driver", "eks_addon_name": "aws-mountpoint-s3-csi-driver"},
            {"name": "aws-network-flow-monitor-agent", "namespace": "aws-network-flow-monitor", "kind": "daemonset", "display_name": "AWS Network Flow Monitor Agent", "eks_addon_name": "aws-network-flow-monitoring-agent"},
            {"name": "node-monitoring-agent", "namespace": "kube-system", "kind": "daemonset", "display_name": "Node monitoring agent", "eks_addon_name": "eks-node-monitoring-agent"},
            {"name": "eks-pod-identity-agent", "namespace": "kube-system", "kind": "daemonset", "display_name": "Amazon EKS Pod Identity Agent", "eks_addon_name": "eks-pod-identity-agent"},
            {"name": "snapshot-controller", "namespace": "kube-system", "kind": "deployment", "display_name": "CSI Snapshot Controller", "eks_addon_name": "snapshot-controller"},
            {"name": "ebs-csi-controller", "namespace": "kube-system", "kind": "deployment", "display_name": "ebs-csi-driver", "eks_addon_name": "aws-ebs-csi-driver"},
            {"name": "efs-csi-controller", "namespace": "kube-system", "kind": "deployment", "display_name": "efs-csi-driver", "eks_addon_name": "aws-efs-csi-driver"}
        ]
        
        # Filter out addons that are already installed as EKS addons
        filtered_configs = []
        for config in addon_configs:
            eks_addon_name = config.get("eks_addon_name")
            if eks_addon_name is None or eks_addon_name not in eks_addon_names:
                filtered_configs.append(config)
        
        # Group by namespace and resource type to reduce API calls
        namespaces_deployments = {}
        namespaces_daemonsets = {}
        
        for addon_config in filtered_configs:
            namespace = addon_config["namespace"]
            kind = addon_config["kind"]
            
            if kind == "deployment":
                if namespace not in namespaces_deployments:
                    namespaces_deployments[namespace] = []
                namespaces_deployments[namespace].append(addon_config)
            elif kind == "daemonset":
                if namespace not in namespaces_daemonsets:
                    namespaces_daemonsets[namespace] = []
                namespaces_daemonsets[namespace].append(addon_config)
        
        # Set timeout and retry parameters
        timeout_seconds = 30
        max_retries = 3
        retry_delay = 2  # seconds
        
        # Batch fetch Deployments
        for namespace, configs in namespaces_deployments.items():
            try:
                # Use field selector to limit returned resources
                field_selector = None
                if len(configs) <= 5:  # If fewer resources, field selector is more efficient
                    names = [config["name"] for config in configs]
                    field_selector = "metadata.name=" + ",metadata.name=".join(names)
                
                # Add timeout and retry mechanism
                for attempt in range(max_retries):
                    try:
                        deployments = apps_v1.list_namespaced_deployment(
                            namespace=namespace,
                            field_selector=field_selector,
                            timeout_seconds=timeout_seconds
                        )
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(retry_delay)
                            continue
                        raise e
                
                # Process returned Deployments
                for deployment in deployments.items:
                    name = deployment.metadata.name
                    # Find matching configuration
                    matching_configs = [c for c in configs if c["name"] == name]
                    if matching_configs:
                        config = matching_configs[0]
                        display_name = config.get("display_name", name)
                        
                        if deployment.spec.template.spec.containers:
                            version = get_image_version(deployment.spec.template.spec.containers[0].image)
                            addon_info = {"name": display_name, "version": version}
                            # Extract Helm info from labels
                            extract_helm_info_from_labels(deployment.metadata.labels, addon_info)
                            addons.append(addon_info)
            except Exception as e:
                print(f"Error fetching deployments in namespace {namespace}: {e}")
        
        # Batch fetch DaemonSets
        for namespace, configs in namespaces_daemonsets.items():
            try:
                # Use field selector to limit returned resources
                field_selector = None
                if len(configs) <= 5:  # If fewer resources, field selector is more efficient
                    names = [config["name"] for config in configs]
                    field_selector = "metadata.name=" + ",metadata.name=".join(names)
                
                # Add timeout and retry mechanism
                for attempt in range(max_retries):
                    try:
                        daemonsets = apps_v1.list_namespaced_daemon_set(
                            namespace=namespace,
                            field_selector=field_selector,
                            timeout_seconds=timeout_seconds
                        )
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            import time
                            time.sleep(retry_delay)
                            continue
                        raise e
                
                # Process returned DaemonSets
                for daemonset in daemonsets.items:
                    name = daemonset.metadata.name
                    # Find matching configuration
                    matching_configs = [c for c in configs if c["name"] == name]
                    if matching_configs:
                        config = matching_configs[0]
                        display_name = config.get("display_name", name)
                        
                        if daemonset.spec.template.spec.containers:
                            version = get_image_version(daemonset.spec.template.spec.containers[0].image)
                            addon_info = {"name": display_name, "version": version}
                            # Extract Helm info from labels
                            extract_helm_info_from_labels(daemonset.metadata.labels, addon_info)
                            addons.append(addon_info)
            except Exception as e:
                print(f"Error fetching daemonsets in namespace {namespace}: {e}")
            
        return addons
    except Exception as e:
        print(f"Error getting opensource addons: {e}")
        return []

def extract_helm_info_from_labels(labels, addon_info):
    """
    Extract Helm related information from Kubernetes resource labels
    
    Args:
        labels: Dictionary of resource labels
        addon_info: Addon information dictionary to update
    """
    if not labels:
        return
    
    # Check if managed by Helm
    if labels.get("app.kubernetes.io/managed-by") == "Helm" or "helm.sh/chart" in labels:
        addon_info["helm_installed"] = True
        
        # Extract chart information
        if "helm.sh/chart" in labels:
            chart_info = labels["helm.sh/chart"]
            # Chart format is typically name-version
            chart_parts = chart_info.split("-")
            if len(chart_parts) >= 2:
                # Last part is version, the rest is chart name
                chart_version = chart_parts[-1]
                chart_name = "-".join(chart_parts[:-1])
                addon_info["helm_chart_name"] = chart_name
                addon_info["helm_chart_version"] = chart_version
        
        # Extract App Version
        if "app.kubernetes.io/version" in labels:
            addon_info["helm_app_version"] = labels["app.kubernetes.io/version"]
        elif "app.kubernetes.io/instance" in labels:
            addon_info["helm_app_version"] = labels["app.kubernetes.io/instance"]

def get_image_version(image_string):
    """
    Extract version from container image string.
    
    Args:
        image_string: Container image string (e.g., "registry.k8s.io/metrics-server/metrics-server:v0.6.3")
        
    Returns:
        str: Version string or "unknown" if version cannot be determined
    """
    try:
        # Try to extract version from image tag
        if ":" in image_string:
            tag = image_string.split(":")[-1]
            # If tag starts with 'v', remove it
            if tag.startswith("v"):
                return tag[1:]
            return tag
        return "unknown"
    except:
        return "unknown"

def get_core_components_version(api_client, eks_addons):
    """
    Get version information for core components (coredns, kube-proxy, vpccni) 
    if they are not in the EKS addons list.
    Optimized for large scale clusters with timeout and retry mechanisms.
    
    Args:
        api_client: Kubernetes API client
        eks_addons: List of EKS addons
        
    Returns:
        list: List of dictionaries containing component name and version
    """
    if not api_client:
        return []
    
    # Extract EKS addon name list
    eks_addon_names = [addon['name'] for addon in eks_addons]
    core_components = []
    
    # Set timeout and retry parameters
    timeout_seconds = 30
    max_retries = 3
    retry_delay = 2  # seconds
    
    try:
        apps_v1 = client.AppsV1Api(api_client)
        
        # Define core components to check
        components = [
            {"name": "coredns", "namespace": "kube-system", "kind": "deployment", "addon_name": "coredns"},
            {"name": "kube-proxy", "namespace": "kube-system", "kind": "daemonset", "addon_name": "kube-proxy"},
            {"name": "aws-node", "namespace": "kube-system", "kind": "daemonset", "addon_name": "vpc-cni"}
        ]
        
        # Check each component only if not installed as an EKS addon
        for component in components:
            if component["addon_name"] not in eks_addon_names:
                try:
                    # Add timeout and retry mechanism
                    for attempt in range(max_retries):
                        try:
                            if component["kind"] == "deployment":
                                resource = apps_v1.read_namespaced_deployment(
                                    component["name"], 
                                    component["namespace"],
                                    _request_timeout=timeout_seconds
                                )
                            else:  # daemonset
                                resource = apps_v1.read_namespaced_daemon_set(
                                    component["name"], 
                                    component["namespace"],
                                    _request_timeout=timeout_seconds
                                )
                            break
                        except Exception as e:
                            if attempt < max_retries - 1:
                                import time
                                time.sleep(retry_delay)
                                continue
                            raise e
                    
                    if resource and resource.spec.template.spec.containers:
                        version = get_image_version(resource.spec.template.spec.containers[0].image)
                        core_components.append({"name": component["addon_name"], "version": version})
                except Exception as e:
                    print(f"Error fetching {component['name']}: {e}")
                    pass
                
        return core_components
    except Exception as e:
        print(f"Error getting core components version: {e}")
        return []

def main(cluster_name, region, target_version, profile=None):
    cluster_info = get_cluster_info(cluster_name, region, profile)
    current_version = get_current_version(cluster_info)
    
    # Validate target version
    is_valid, error_message = validate_target_version(current_version, target_version)
    if not is_valid:
        print(f"Error: {error_message}")
        sys.exit(1)
    
    health_issues = get_health_issues(cluster_info)
    # Cluster Insights API is not available in China Regions.
    if region not in ["cn-north-1", "cn-northwest-1"]:
        compatibility_issues = get_compatibility_issues(cluster_name, region, profile)
    else:
        compatibility_issues = []
    
    nodegroups, min_nodegroup_version = get_nodegroups(cluster_name, region, profile)
    fargate_profiles = get_fargate_profiles(cluster_name, region, profile)
    installed_addons = get_installed_addons(cluster_name, region, profile)
    addon_upgrade_info, upgrade_recommended = get_addon_upgrade_info(cluster_name, region, current_version, target_version, profile)
    
    # Find kube-proxy addon version
    kube_proxy_version = next((addon['current_version'] for addon in addon_upgrade_info if addon['name'] == 'kube-proxy'), None)
    
    # Get self-managed and Karpenter nodes minimum versions
    min_self_managed_version = None
    min_karpenter_version = None
    self_managed_count = 0
    karpenter_count = 0
    
    # Connect to kube-apiserver only when connect_k8s is True
    if args.connect_k8s:
        api_client = connect_to_cluster(cluster_name, region, profile)
    
        # Get minimum versions of self-managed and Karpenter nodes
        if api_client:
            min_self_managed_version, min_karpenter_version, self_managed_count, karpenter_count = get_node_versions(api_client)
        
            # Get open source addon information
            opensource_addons = get_opensource_addons(api_client, installed_addons)
            
            # Get core component version information (if not in EKS addon list)
            core_components = get_core_components_version(api_client, installed_addons)
        else:
            print("Failed to connect to kube-apiserver!")
            sys.exit(1)
    else:
        api_client = None
        min_self_managed_version = None
        min_karpenter_version = None
        self_managed_count = 0
        karpenter_count = 0
        opensource_addons = []
        core_components = []
    
    print("1. Cluster Info:")
    print(f"   EKS Cluster: {cluster_name}")
    print(f"   Region: {region}")
    print(f"   Current Version: {current_version}")
    print(f"   Target Version: {target_version}")

    print("\n2. Version Skew:")
    if kube_proxy_version is None:
        print("   WARNING: kube-proxy is not installed as an EKS addon. This may affect cluster upgrades and version compatibility.")
        
    if kube_proxy_version and min_nodegroup_version:
        version_skew_recommended, recommendations = check_version_skew(current_version, min_nodegroup_version, kube_proxy_version, target_version)
        if version_skew_recommended:
            print("   Upgrade recommended:")
            for recommendation in recommendations:
                print(f"   - {recommendation}")
        else:
            print("   No version skew issues detected.")
    else:
        print("   Unable to check version skew due to missing information.")

    print("\n3. Addon Compatibility Issues:")
    for addon in addon_upgrade_info:
        print(f"   - {addon['name']}:")
        print(f"     Current Version: {addon['current_version']}")
        print(f"     Status: {addon['status']}")
        if 'suggested_version_range' in addon:
            print(f"     Suggested Version: {addon['suggested_version_range']}")

    print("\n4. Cluster Health Issues:")
    if health_issues:
        for issue in health_issues:
            print(f"   - {issue}")
    else:
        print("   No health issues detected.")

    print("\n5. Deprecated APIs:")
    if region not in ["cn-north-1", "cn-northwest-1"]:
        deprecated_apis = get_deprecated_api_versions(compatibility_issues)
        if deprecated_apis:
            for api in deprecated_apis:
                print(f"   - Current API: {api['usage']}")
                print(f"     Replaced With: {api['replacedWith']}")
                print(f"     Stop Serving Version: {api['stopServingVersion']}")
                print(f"     Start Serving Replacement Version: {api['startServingReplacementVersion']}")
                if api['clientStats']:
                    print("     Client Stats:")
                    for stat in api['clientStats']:
                        print(f"       User Agent: {stat['userAgent']}")
                        print(f"       Number of Requests (Last 30 Days): {stat['numberOfRequestsLast30Days']}")
                        print(f"       Last Request Time: {stat['lastRequestTime']}")
                print()
        else:
            print("   No deprecated APIs detected.")
    else:
        print("   Not provided")

    print("\n6. Nodegroup List:")
    for ng in nodegroups:
        print(f"   - {ng['name']}: {ng['version']}")
    print(f"   Summary: The minimum nodegroup version is: {min_nodegroup_version}")

    print("\n7. Fargate Profile List:")
    if fargate_profiles:
        for profile in fargate_profiles:
            print(f"   - {profile}")
    else:
        print("   No Fargate profiles found.")
        
    # Print only when connect_k8s is True
    if args.connect_k8s:
        print("\n8. Self-Managed Nodes:")
        if self_managed_count > 0:
            print(f"   {self_managed_count} self-managed nodes in this cluster.")
            print(f"   Minimum Version: {min_self_managed_version}")
        else:
            print("   No self-managed nodes found.")
        
        print("\n9. Karpenter Nodes:")
        if karpenter_count > 0:
            print(f"   {karpenter_count} Karpenter nodes in this cluster.")
            print(f"   Minimum Version: {min_karpenter_version}")
        else:
            print("   No Karpenter nodes found.")
        
        print("\n10. Open Source Addons:")
        if opensource_addons:
            for addon in opensource_addons:
                if "helm_installed" in addon and addon["helm_installed"]:
                    print(f"   - {addon['name']}: image version: {addon['version']} (Helm: chart={addon.get('helm_chart_name', 'unknown')}:{addon.get('helm_chart_version', 'unknown')}, app={addon.get('helm_app_version', 'unknown')})")
                else:
                    print(f"   - {addon['name']}: image version: {addon['version']}")
        else:
            print("   No open source addons found.")
            
        print("\n11. Core Addons (self-managed):")
        if core_components:
            for component in core_components:
                print(f"   - {component['name']}: {component['version']}")
        else:
            print("   No additional core components found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EKS Cluster Information Tool")
    parser.add_argument("cluster_name", help="Name of the EKS cluster")
    parser.add_argument("--region", help="AWS region of the EKS cluster")
    parser.add_argument("target_version", help="Target EKS version for compatibility checks")
    parser.add_argument("--profile", help="AWS profile to use")
    parser.add_argument("--connect-k8s", action="store_true", 
                    help="Connect to Kubernetes API server to collect additional information")
    args = parser.parse_args()

    if not args.region:
        session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
        args.region = session.region_name

    if not args.region:
        print("Error: AWS region is required. Please provide it using --region or set it in your AWS configuration.")
        sys.exit(1)

    main(args.cluster_name, args.region, args.target_version, args.profile)
