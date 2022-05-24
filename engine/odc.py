import urllib3
import xmltodict
import logging
import re

logging.basicConfig(filename='/tmp/myapp.log', filemode='w', level=logging.DEBUG,
                    format='[%(asctime)s]: %(levelname)-7s : %(message)s')


class ODCServer(object):
    def __init__(self, ip, family, serial, timeout=60):
        self.http = urllib3.PoolManager(timeout=timeout)
        self.ip = ip
        self.family = family
        self.serial = serial
        self.get_data = ''

    def request_data(self, url):
        try:
            r = self.http.request('GET', f'http://{self.ip}/des/{self.family}/{url}', preload_content=False)
            return r.data.decode('utf-8') if r.status == 200 else False
        except Exception as err:
            logging.error(err, exc_info=True)
            raise Exception(err)

    def clear_ticket(self):
        tk = self.get_ticket()
        self.get_data = self.request_data(f'clearticket.asp?SN={self.serial}&ticket={tk}')
        return self.get_data

    def request_ticket(self):
        self.get_data = self.request_data(f'getticket.asp?SN={self.serial}')
        return self.get_data

    def get_ticket(self):
        self.get_data = self.request_data(f'getparameter.asp?SN={self.serial}&profile=ticket')
        return self.get_data

    def get_data_odc(self, profile, serial=None):
        self.get_data = dict()
        serial = serial if serial else self.serial
        for i in profile if isinstance(profile, list) else [profile]:
            data_odc = ''
            try:
                data_odc = self.request_data(f'getparameter.asp?profile={i}&SN={serial}')
                data_odc = xmltodict.parse(data_odc)
                for k, v in data_odc['Parameter'].items():
                    v = re.sub(r'-', '', str(v))
                    v = v.split(',') if ',' in v else v
                    data_odc['Parameter'].update({k: None if isinstance(v, str) and v in ['None'] else v})
                self.get_data.update(**data_odc['Parameter'])
            except xmltodict.expat.ExpatError:
                self.get_data = data_odc
        return self.get_data

    def get_current_station(self):
        self.get_data = self.request_data(f'check.asp?SN={self.serial}')
        return self.get_data

    def get_process_ticket(self, ticket):
        self.get_data = self.request_data(f'process.asp?ticket={ticket}&process=true')
        return self.get_data

    def put_data_odc(self, data):
        try:
            r = self.http.request('POST', f'http://{self.ip}/des/{self.family}/result.asp', body=data,
                                  headers={'Content-Type': 'text/xml'})
            return r.data.decode('utf-8') if r.status == 200 else False
        except Exception as err:
            logging.error(err, exc_info=True)
            raise Exception(err)

