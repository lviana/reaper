import _mysql

def collect():
    """ Plesk shared reselling"""
    dbuser = 'admin'
    with open('/etc/psa/.psa.shadow', 'ro') as f:
        dbpass = f.read()
        resellers = {}
        try:
            con = _mysql.connect('localhost', dbuser, dbpass.strip(), 'psa')
            con.query("SELECT id, login FROM clients WHERE type = 'reseller'")
            result = con.store_result()
            for item in result.fetch_row(0, 1):
                resellers[item['login']] = []
                con.query("SELECT login FROM clients WHERE parent_id = %s" % item['id'])
                cresult = con.store_result()
                for customer in cresult.fetch_row(0, 1):
                    resellers[item['login']].append(customer['login'])
        except _mysql.Error, e:
            print ("Could not connect to local MySQL server %d: %s" % (e.args[0], e.args[1]))
        finally:
            if con:
                con.close()
        return resellers
