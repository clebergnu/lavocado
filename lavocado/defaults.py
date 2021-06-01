LIBVIRT_URI = "qemu:///system"

TEMPLATE_PATH = "./templates/domain.xml.jinja"

VMIMAGE = {
        'provider': 'fedora',
        'version': '33',
        'checksum': '67daa956d8c82ef799f8b0a191c1753c9bda3bca'
        }

CACHE_DIR = '/tmp/lavocado-cache'
