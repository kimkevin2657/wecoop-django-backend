# RDS
### Set up Project Name and Profile Name
- 터미널을 새로 열었을 때마다 실행
```
export PROJECT_NAME={project_name}
export PROFILE_NAME={profile_name}
```
---

### Create RDS
- `{db_password}`입력 필요
- 특수문자의 경우 특수문자 앞에 `\ `필요
  - ex) `ParameterValue=test123\!\!`
```
aws cloudformation create-stack \
    --stack-name ${PROJECT_NAME}-rds \
    --profile $PROFILE_NAME \
    --template-body file://.cloudformation/rds.yml \
    --capabilities CAPABILITY_IAM \
    --parameters ParameterKey=DBPassword,ParameterValue={db_password}
```
---

### Confirm RDS Host
- DB가 생성된 후 확인 가능
```
aws cloudformation describe-stacks \
    --stack-name ${PROJECT_NAME}-rds \
    --query "Stacks[0].Outputs" \
    --output text
```
---

### Set up Database Host
 - settings에 `DB_WRITER_HOST`, `DB_READER_HOST`등록
---