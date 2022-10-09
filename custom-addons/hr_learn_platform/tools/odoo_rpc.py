import xmlrpc.client


class OdooRPC:
    def __init__(self, base_url, db, user, password):
        self.db = db
        self.user = user
        self.password = password
        self.base_url = base_url
        common = xmlrpc.client.ServerProxy(f'{base_url}/xmlrpc/2/common')
        self.uid = common.authenticate(db, user, password, {})
        self.models = xmlrpc.client.ServerProxy(f'{base_url}/xmlrpc/2/object')

    def rpc(self, model, method, *args, **kwargs):
        return self.models.execute_kw(self.db, self.uid, self.password, model, method, args, kwargs)
