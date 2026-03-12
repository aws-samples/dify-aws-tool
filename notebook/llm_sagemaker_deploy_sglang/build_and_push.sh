#!/bin/bash
SGLANG_REPO=${SGLANG_REPO:-"lmsysorg/sglang"}
SGLANG_VERSION=${SGLANG_VERSION:-"latest"}

REPO_NAMESPACE=${REPO_NAMESPACE:-"sagemaker_endpoint/sglang"}

# Get the ACCOUNT and REGION defined in the current configuration (default to us-west-2 if none defined)

ACCOUNT=${ACCOUNT:-$(aws sts get-caller-identity --query Account --output text)}
REGION=${REGION:-$(aws configure get region)}

# If the repository doesn't exist in ECR, create it.
aws ecr describe-repositories --repository-names "${REPO_NAMESPACE}" > /dev/null 2>&1
if [ $? -ne 0 ]
then
echo "create repository:" "${REPO_NAMESPACE}"
aws ecr create-repository --repository-name "${REPO_NAMESPACE}" > /dev/null
fi

# Log into Docker
if [[ "$REGION" = cn* ]]; then
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com.cn
    REPO_NAME="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com.cn/${REPO_NAMESPACE}:${SGLANG_VERSION}"
else
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com
    REPO_NAME="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${REPO_NAMESPACE}:${SGLANG_VERSION}"
fi

echo ${REPO_NAME}

# Build docker
DOCKER_BUILDKIT=1 docker build --progress=plain --build-arg SGLANG_VERSION=${SGLANG_VERSION} --build-arg SGLANG_REPO=${SGLANG_REPO} -t ${REPO_NAMESPACE}:${SGLANG_VERSION} .

# Push it
docker tag ${REPO_NAMESPACE}:${SGLANG_VERSION} ${REPO_NAME}
docker push ${REPO_NAME}
