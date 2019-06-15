import ldap3


def getComputerList(server, domain, usr, pwd):
    """ Get the list of all computers from an active directory. """
    srv = ldap3.Server(server, get_info=ldap3.ALL)
    conn = ldap3.Connection(srv,
                            user='{}\\{}'.format(domain, usr),
                            password=pwd,
                            authentication=ldap3.NTLM)

    if not conn.bind():
        return print('error in bind', conn.result)
    else:
        conn.search(srv.info.naming_contexts[0],
                    '(&(objectclass=computer)(!(operatingSystem=*Server*)))',
                    attributes=['cn', 'dNSHostName'])
        entries = conn.entries
        conn.unbind()
        return entries
