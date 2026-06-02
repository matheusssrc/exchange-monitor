# Terraform — Deploy esquemático na AWS (Trillia Exchange Monitor)

> **Esta é uma infraestrutura como código esquemática. Ela nunca é aplicada.**
> Documenta a topologia de produção pretendida e é mantida `validate`-clean.
> Não há backend remoto nem credenciais reais; os defaults são placeholders.

## Topologia alvo

- **VPC** com subnets públicas (ALB) e privadas (tasks ECS + RDS).
- **ECR** para as imagens do backend e do frontend.
- **RDS PostgreSQL 16** em subnets privadas, acessível apenas pelo ECS.
- **ECS Fargate** rodando a task da API atrás do ALB (o worker é substituído pelo Airflow;
  um deploy real adicionaria uma task/serviço de Airflow ou um ambiente MWAA gerenciado).
- **ALB** com listener HTTP encaminhando para o target group da API (health check em `/health`).
- **Secrets Manager** para a URL do banco.
- **CloudWatch Logs** por container.

## Comandos (apenas validação)

```bash
cd terraform
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

`terraform plan` / `terraform apply` **não** fazem parte deste entregável — intencionalmente.

---

Licença MIT · Matheus Rossi Carvalho.
