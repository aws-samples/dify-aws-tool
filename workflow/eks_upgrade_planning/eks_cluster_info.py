import boto3
import argparse
import sys
from botocore.exceptions import ClientError

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
                addon_info['suggested_version_range'] = 'N/A'
                upgrade_recommended = False
            elif not target_compatible:
                # Not compatible with target version
                addon_info['status'] = f'Not compatible with target version {target_version}'
                addon_info['suggested_version_range'] = 'N/A'
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
                        addon_info['suggested_version_range'] = 'N/A'
                        upgrade_recommended = False
                else:
                    addon_info['status'] = 'No compatible versions found'
                    addon_info['suggested_version_range'] = 'N/A'
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

def main(cluster_name, region, target_version, profile=None):
    cluster_info = get_cluster_info(cluster_name, region, profile)
    current_version = get_current_version(cluster_info)
    health_issues = get_health_issues(cluster_info)
    # Cluster Insights API is not available in China Regions.
    if region not in ["cn-north-1", "cn-northwest-1"]:
        compatibility_issues = get_compatibility_issues(cluster_name, region, profile)
    else:
        compatibility_issues = []
    
    nodegroups, min_nodegroup_version = get_nodegroups(cluster_name, region, profile)
    fargate_profiles = get_fargate_profiles(cluster_name, region, profile)
    addon_upgrade_info, upgrade_recommended = get_addon_upgrade_info(cluster_name, region, current_version, target_version, profile)
    
    # Find kube-proxy addon version
    kube_proxy_version = next((addon['current_version'] for addon in addon_upgrade_info if addon['name'] == 'kube-proxy'), None)
    
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
    print(f"   Minimum Nodegroup Version: {min_nodegroup_version}")
    for ng in nodegroups:
        print(f"   - {ng['name']}: {ng['version']}")

    print("\n7. Fargate Profile List:")
    if fargate_profiles:
        for profile in fargate_profiles:
            print(f"   - {profile}")
    else:
        print("   No Fargate profiles found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EKS Cluster Information Tool")
    parser.add_argument("cluster_name", help="Name of the EKS cluster")
    parser.add_argument("--region", help="AWS region of the EKS cluster")
    parser.add_argument("target_version", help="Target EKS version for compatibility checks")
    parser.add_argument("--profile", help="AWS profile to use")
    args = parser.parse_args()

    if not args.region:
        session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
        args.region = session.region_name

    if not args.region:
        print("Error: AWS region is required. Please provide it using --region or set it in your AWS configuration.")
        sys.exit(1)

    main(args.cluster_name, args.region, args.target_version, args.profile)
