
您可以设置多个变量，例如:

* `PROJECT_NAME`：项目名称，用于API文档和邮件。
* `STACK_NAME`：堆栈名称，用于Docker Compose标签和项目名称，这应该对于`staging`、`production`等有所不同。您可以使用相同的域名，将点替换为破折号，例如`fastapi-project-example-com`和`staging-fastapi-project-example-com`。
* `BACKEND_CORS_ORIGINS`：允许的CORS来源列表，用逗号分隔。
* `SECRET_KEY`：FastAPI项目的密钥，用于签名令牌。
* `FIRST_SUPERUSER`：第一位超级用户的电子邮件，此超级用户将能创建新用户。
* `FIRST_SUPERUSER_PASSWORD`：第一位超级用户的密码。
* `USERS_OPEN_REGISTRATION`：是否允许新用户开放注册。
* `SMTP_HOST`：发送邮件的SMTP服务器主机，这将来自您的电子邮件提供商（例如Mailgun、Sparkpost、Sendgrid等）。
* `SMTP_USER`：发送邮件的SMTP服务器用户。
* `SMTP_PASSWORD`：发送邮件的SMTP服务器密码。
* `EMAILS_FROM_EMAIL`：发送邮件的电子邮件账户。
* `POSTGRES_SERVER`：PostgreSQL服务器的主机名。您可以保留默认的`db`，由同一个Docker Compose提供。通常您不需要更改这个，除非您使用第三方提供商。
* `POSTGRES_PORT`：PostgreSQL服务器的端口。您可以保留默认值。通常您不需要更改这个，除非您使用第三方提供商。
* `POSTGRES_PASSWORD`：Postgres密码。
* `POSTGRES_USER`：Postgres用户，您可以保留默认值。
* `POSTGRES_DB`：用于此应用程序的数据库名称。您可以保留默认的`app`。
* `SENTRY_DSN`：如果您使用Sentry，这是Sentry的DSN。

### 生成密钥

`.env` 文件中的一些环境变量默认值为 `changethis`。

您需要使用一个密钥来更改它们，要生成密钥，您可以运行以下命令：

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

复制输出内容并将其用作密码/密钥。然后再次运行该命令以生成另一个安全密钥。

## 持续部署（CD）

您可以使用 GitHub Actions 来自动部署您的项目。😎

您可以配置多个环境进行部署。

已经配置了两个环境，`staging`（预发布环境）和 `production`（生产环境）。🚀