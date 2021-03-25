import psutil


def stop_dns():
    with open("C:/Users/StudyUser/PycharmProjects/HU_Cloud-Infrastructure-and-Management/dns-server/pid.id", "r") as pid_file:
        pid = int(pid_file.read())

    try:
         p = psutil.Process(pid)
         p.terminate()
    except psutil.NoSuchProcess:
        return """ <a>No process found with pid: {}</a>""".format(pid)

    try:
        import dns.resolver
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = ['127.0.0.1']
        resolver.lifetime = 1
        [ns.to_text() for ns in resolver.query('example.com', 'a')]
    except:
        pass

    return """ <a>The DNS-server has been stopped with de PID of: {}</a>""".format(pid)