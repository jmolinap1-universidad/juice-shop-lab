Imagen: bkimminich/juice-shop:v20.3.0@sha256:cea5a4af4aacee498c491491af0408934ec81d004035c0a02ef3e54395e3bf27
SO base: debian 13.7
Vulnerabilidades únicas (vuln×paquete): 126

| Severidad | Cantidad |
|---|---|
| CRITICAL | 11 |
| HIGH | 32 |
| MEDIUM | 71 |
| LOW | 11 |
| UNKNOWN | 1 | 

| Origen | Cantidad |
|---|---|
| Dependencias Node.js | 81 |
| Sistema operativo | 45 | 

Secretos detectados: 5
- /juice-shop/build/lib/insecurity.js: private-key (HIGH)
- /juice-shop/frontend/src/app/app.guard.spec.ts: jwt-token (MEDIUM)
- /juice-shop/frontend/src/app/last-login-ip/last-login-ip.component.spec.ts: jwt-token (MEDIUM)
- /juice-shop/infrastructure/terraform/networking.tf: private-key (HIGH)
- /juice-shop/lib/insecurity.ts: private-key (HIGH)

Malas configuraciones: 66
- AWS-0037 EFS Encryption has not been enabled (HIGH)
- AWS-0052 Load balancers should drop invalid headers (HIGH)
- AWS-0053 Load balancer is exposed to the internet. (HIGH)
- AWS-0054 Use of plain HTTP. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0164 Instances in a subnet should not receive a public IP address by default. (HIGH)
- AWS-0178 VPC Flow Logs is a feature that enables you to capture information about the IP traffic going to and from network interfaces in your VPC. After you've created a flow log, you can view and retrieve its data in Amazon CloudWatch Logs. It is recommended that VPC Flow Logs be enabled for packet "Rejects" for VPCs. (MEDIUM)
- AWS-0037 EFS Encryption has not been enabled (HIGH)
- AWS-0052 Load balancers should drop invalid headers (HIGH)
- AWS-0053 Load balancer is exposed to the internet. (HIGH)
- AWS-0054 Use of plain HTTP. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0164 Instances in a subnet should not receive a public IP address by default. (HIGH)
- AWS-0178 VPC Flow Logs is a feature that enables you to capture information about the IP traffic going to and from network interfaces in your VPC. After you've created a flow log, you can view and retrieve its data in Amazon CloudWatch Logs. It is recommended that VPC Flow Logs be enabled for packet "Rejects" for VPCs. (MEDIUM)
- AWS-0037 EFS Encryption has not been enabled (HIGH)
- AWS-0052 Load balancers should drop invalid headers (HIGH)
- AWS-0053 Load balancer is exposed to the internet. (HIGH)
- AWS-0054 Use of plain HTTP. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0164 Instances in a subnet should not receive a public IP address by default. (HIGH)
- AWS-0178 VPC Flow Logs is a feature that enables you to capture information about the IP traffic going to and from network interfaces in your VPC. After you've created a flow log, you can view and retrieve its data in Amazon CloudWatch Logs. It is recommended that VPC Flow Logs be enabled for packet "Rejects" for VPCs. (MEDIUM)
- DS-0026 No HEALTHCHECK defined (LOW)
- AWS-0017 CloudWatch log groups should be encrypted using CMK (LOW)
- AWS-0052 Load balancers should drop invalid headers (HIGH)
- AWS-0053 Load balancer is exposed to the internet. (HIGH)
- AWS-0054 Use of plain HTTP. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0104 A security group rule should not allow unrestricted egress to any IP address. (CRITICAL)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0124 Missing description for security group rule. (LOW)
- AWS-0164 Instances in a subnet should not receive a public IP address by default. (HIGH)
- AWS-0164 Instances in a subnet should not receive a public IP address by default. (HIGH)
- AWS-0178 VPC Flow Logs is a feature that enables you to capture information about the IP traffic going to and from network interfaces in your VPC. After you've created a flow log, you can view and retrieve its data in Amazon CloudWatch Logs. It is recommended that VPC Flow Logs be enabled for packet "Rejects" for VPCs. (MEDIUM)

| ID | Sev. | Paquete | Instalada | Corregida |
|---|---|---|---|---|
| CVE-2023-46233 | CRITICAL | crypto-js | 3.3.0 | 4.2.0 |
| CVE-2026-71851 | CRITICAL | crypto-js | 3.3.0 | 4.0.0 |
| CVE-2026-101894 | CRITICAL | decompress | 4.2.1 | — |
| CVE-2026-53486 | CRITICAL | decompress | 4.2.1 | — |
| CVE-2026-106445 | CRITICAL | handlebars | 4.7.9 | 4.7.10 |
| CVE-2026-106446 | CRITICAL | handlebars | 4.7.9 | 4.7.10 |
| CVE-2015-9235 | CRITICAL | jsonwebtoken | 0.1.0 | 4.2.2 |
| CVE-2015-9235 | CRITICAL | jsonwebtoken | 0.4.0 | 4.2.2 |
| CVE-2019-10744 | CRITICAL | lodash | 2.4.2 | 4.17.12 |
| GHSA-5mrr-rgp6-x4gr | CRITICAL | marsdb | 0.6.11 | — |
| CVE-2026-59873 | CRITICAL | tar | 6.2.1 | 7.5.19 |
