import consul

c = consul.Consul()

# poll a key for updates
index = None
while True:
    index, data = c.kv.get('foo', index=index)
    print(data['Value'])

# in another process
# c.kv.put('foo', 'bar')