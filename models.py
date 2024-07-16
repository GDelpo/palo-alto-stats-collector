from datetime import datetime

class License:
    def __init__(self, feature, issued, expired):
        self.feature = feature
        self.issued = datetime.strptime(issued, "%B %d, %Y").strftime("%d/%m/%Y")
        self.expired = True if expired == 'yes' else False

    def to_dict(self):
        return {
            'feature': self.feature,
            'issued': self.issued,
            'expired': self.expired
        }    
    
    def __str__(self):
        return f"Feature: {self.feature}\nIssued: {self.issued}\nExpired: {self.expired}"        


class Device:
    def __init__(self, hostname, model, serial, ip_address, sw_version, gpc_version, app_version, av_version, threat_version, wildfire_version, url_filtering_version, device_certificate_status):
        self.create_report_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.hostname = hostname
        self.model = model
        self.serial = serial
        self.ip_address = ip_address
        self.sw_version = sw_version
        self.sw_version_prefered = None
        self.gpc_version = gpc_version
        self.app_version = app_version
        self.av_version = av_version
        self.threat_version = threat_version
        self.wildfire_version = wildfire_version
        self.url_filtering_version = url_filtering_version
        self.device_certificate_status = device_certificate_status
        self.licenses = []
    
    def identify_model(self):
        type_model = self.model[0:2]
        match type_model:
            case 'PA':
                type_model = 'PAN-OS for Firewalls'
            case 'VM':
                type_model = 'Panorama on VM / M-series'
            case _:
                type_model = None
        return type_model
    
    def add_license(self, feature, issued, expired):
        self.licenses.append(License(feature, issued, expired))

    def to_dict(self):
        licenses_dict = [license.to_dict() for license in self.licenses]
        return {
            'create_report_datetime': self.create_report_datetime,
            'hostname': self.hostname,
            'model': self.model,
            'serial': self.serial,
            'ip_address': self.ip_address,
            'sw_version': self.sw_version,
            'sw_version_prefered': self.sw_version_prefered,
            'gpc_version': self.gpc_version,
            'app_version': self.app_version,
            'av_version': self.av_version,
            'threat_version': self.threat_version,
            'wildfire_version': self.wildfire_version,
            'url_filtering_version': self.url_filtering_version,
            'device_certificate_status': self.device_certificate_status,
            'licenses': licenses_dict
        }

    def __str__(self):
        licenses_str = '\n\n'.join([str(license) for license in self.licenses])
        return (f"IP Address: {self.ip_address}\nHostname: {self.hostname}\nModel: {self.model}\nSW Version: {self.sw_version}\n"
                f"Serial: {self.serial}\nGlobal Protect Client Package Version: {self.gpc_version}\n"
                f"App Version: {self.app_version}\nAV Version: {self.av_version}\nThreat Version: {self.threat_version}\n"
                f"Wildfire Version: {self.wildfire_version}\nURL Filtering Version: {self.url_filtering_version}\n"
                f"Device Certificate Status: {self.device_certificate_status}\nLicenses:\n{licenses_str}")