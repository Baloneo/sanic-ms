import consul
health = consul.health
checks = health.service(service_name)
res = {}
for check in checks:
    res[check['ServiceID']] = check
return res