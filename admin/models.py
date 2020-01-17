from django.db import models

# Create your models here.


class HostInfo(models.Model):
    '''hostinfo db table model'''
    hostname = models.CharField(max_length=100, unique=True)
    sn = models.CharField(max_length=80)
    idrc_ip = models.GenericIPAddressField(max_length=15)
    host_ip = models.GenericIPAddressField(max_length=15)
    cluster_tag = models.CharField(max_length=20)
    cpu = models.CharField(max_length=50, null=True)
    disk = models.CharField(max_length=50, null=True)
    dev_model = models.CharField(max_length=50, null=True)
    memory = models.CharField(max_length=50)
    os = models.CharField(max_length=20)
    desc = models.TextField(null=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.hostname


class VmInfo(models.Model):
    '''vminfo db table model'''
    vm_hostname = models.CharField(max_length=100)
    vm_ip = models.GenericIPAddressField(max_length=15)
    vlan_tag = models.CharField(max_length=30)
    vlan_id = models.IntegerField()
    host = models.ForeignKey(HostInfo, on_delete=models.CASCADE)
    vm_cpu = models.CharField(max_length=10)
    vm_disk = models.CharField(max_length=10, null=True)
    vm_memory = models.CharField(max_length=10)
    vm_os = models.CharField(max_length=20)
    vm_desc = models.TextField(null=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vm_hostname
