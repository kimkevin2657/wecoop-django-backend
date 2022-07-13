# ECS
### Requirement
1. `~/.aws/config`의 `profile`등록
2. github secret에 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`등록
3. `.github/workflows/main.yml`의 PROJECT_NAME 등록
4. `main`브랜치에 푸시
   1. 처음 푸시할 경우 head commit message에 `[nginx]`포함 필요
---

### Set up Project Name and Profile Name
- 터미널을 새로 열었을 때마다 실행
```
export PROJECT_NAME={project_name}
export PROFILE_NAME={profile_name}
```
---

### Create ECS
- `additional_service`(추가서비스) 입력 필요 (오름차순, `/`로 구분)
  - value:
    - 0: nothing(only web)
    - 1: websocket
    - 2: celery
    - 3: celerybeat(require celery)
  - ex:
    - 추가적인 서비스가 없는 경우
      - `ParameterValue=0`
    - celery, celerybeat가 필요한 경우
      - `ParameterValue=2/3`
```
aws cloudformation create-stack \
    --stack-name ${PROJECT_NAME} \
    --profile $PROFILE_NAME \
    --template-body file://.cloudformation/ecs.yml \
    --capabilities CAPABILITY_IAM \
    --parameters ParameterKey=AdditionalService,ParameterValue={additional_service}
```
---

### Update ECS
- 서비스를 추가하거나 제거가 필요한 경우
```
aws cloudformation update-stack \
    --stack-name ${PROJECT_NAME} \
    --profile $PROFILE_NAME \
    --template-body file://.cloudformation/ecs.yml \
    --capabilities CAPABILITY_IAM \
    --parameters ParameterKey=AdditionalService,ParameterValue={additional_service}
```
---

### Set up Loadbalancer
1. AWS EC2 로드밸런서 콘솔접속
2. 로드밸런서의 리스너 기존 포트를 `80`에서 `443`으로 변경
3. 로드밸런서의 리스터 포트에 `80`포트 추가 후 규칙을 `443`으로 리다이렉트로 변경
