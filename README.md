# AWS EC2 自动化创建系统 / AWS EC2 Automated Creation System

本项目提供了一个基于 GitLab CI/CD 的自动化系统，用于创建 AWS EC2 实例。

## 系统要求

- GitLab Runner
- AWS 账号和相应的访问权限
- Python 3.9 或更高版本

## 前置条件

1. AWS 凭证配置
   - 确保你有有效的 AWS Access Key ID 和 Secret Access Key
   - 在 GitLab 项目的 CI/CD 设置中配置以下变量：
     - `AWS_ACCESS_KEY_ID`：你的 AWS Access Key ID
     - `AWS_SECRET_ACCESS_KEY`：你的 AWS Secret Access Key

2. GitLab Runner 配置
   - 确保 GitLab Runner 已正确安装和配置
   - Runner 需要有 `aws` 标签

## 文件结构

```
.
├── .gitlab-ci.yml      # GitLab CI/CD 配置文件
├── create_ec2.py       # EC2 创建脚本
├── requirements.txt    # Python 依赖项
└── README.md          # 说明文档
```

## 使用方法

### 1. 配置变量

在 GitLab CI/CD pipeline 中，你需要配置以下变量：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| EC2_NAME | EC2 实例名称 | my-ec2-instance |
| EC2_REGION | AWS 区域 | us-east-1 |
| EC2_VOLUME_SIZE | 硬盘大小(GB) | 30 |
| EC2_VPC_ID | VPC ID | vpc-xxxxxx |
| EC2_PUBLIC_IP | 是否需要公网IP（true表示需要，false表示不需要） | true/false |
| EC2_INSTANCE_TYPE | 实例类型 | t2.micro |

### 2. 运行 Pipeline

1. 进入 GitLab 项目的 CI/CD > Pipelines 页面
2. 点击 "Run Pipeline" 按钮
3. 填写所需的变量值
4. 点击 "Run Pipeline" 开始创建 EC2 实例

### 3. 查看结果

Pipeline 运行完成后，你可以：
- 在 Job 日志中查看创建结果
- 获取新创建的 EC2 实例 ID
- 如果配置了公网 IP，可以查看分配的 IP 地址

## 输出信息

成功创建实例后，系统会输出以下信息：
```
Successfully created EC2 instance!
Instance ID: i-xxxxxxxxxxxxxxxxx
Instance State: running
Public IP: xxx.xxx.xxx.xxx (如果启用了公网IP)
```

## 注意事项

1. 安全考虑
   - 请确保 AWS 凭证安全，不要在代码中硬编码
   - 建议配置适当的安全组规则
   - 定期轮换 AWS 访问密钥

2. 成本控制
   - 请选择适合你需求的实例类型
   - 注意监控 EC2 实例的运行时间
   - 不需要时及时终止实例

3. 故障排查
   - 检查 AWS 凭证是否正确配置
   - 确认 VPC 和子网配置正确
   - 查看 GitLab CI/CD 日志获取详细错误信息

## 支持的 AWS 区域

你可以在以下常用区域中创建 EC2 实例：
- us-east-1 (弗吉尼亚北部)
- us-west-2 (俄勒冈)
- ap-northeast-1 (东京)
- ap-southeast-1 (新加坡)
- eu-west-1 (爱尔兰)
- cn-north-1 (北京)
- cn-northwest-1 (宁夏)

## 常见问题

1. Q: 创建失败，提示权限不足？
   A: 检查 AWS IAM 权限配置，确保有足够的 EC2 创建权限。

2. Q: 如何确认是否成功分配了公网 IP？
   A: 如果在创建时设置 EC2_PUBLIC_IP 为 "true"，AWS 会自动分配一个公网 IP。创建完成后，可以在输出信息中查看分配的公网 IP 地址。

3. Q: 如何选择合适的实例类型？
   A: 根据应用需求选择，可参考 AWS 实例类型说明文档。 