# Copyright (C) 2021 Red Hat, Inc.
# Copyright (C) 2021 Beraldo Leal <bleal@redhat.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.  If not, see
# <http://www.gnu.org/licenses/>.


import libvirt
import os

from jinja2 import Template
from xml.dom import minidom

from lavocado import defaults
from lavocado.utils import read_file
from lavocado.exceptions import TestSetupException


class Domain:
    # TODO: Document this on README.rst
    @classmethod
    def from_xml_path(cls, conn, xml_path):
        xml_content = read_file(xml_path)
        return conn.createXML(xml_content)

    # TODO: Catch TestSetupException on @fail_on
    @classmethod
    def from_xml_template(cls, conn, suffix, arguments=None):
        template_path = defaults.TEMPLATE_PATH
        arguments = arguments or {}

        if not os.path.isfile(template_path):
            error = f"Template {template_path} not found."
            raise TestSetupException(error)

        # Adding a suffix to the name
        name = arguments.get('name', 'lavocado-test')
        arguments['name'] = f"{name}-{suffix}"

        template = Template(read_file(template_path))
        xml_content = template.render(**arguments)
        return conn.createXML(xml_content)

    @classmethod
    def get_or_create_from_xml_path(cls, conn, xml_path):
        xml_content = read_file(xml_path)
        dom = minidom.parseString(xml_content)
        try:
            name = dom.getElementsByTagName('name')[0].firstChild.nodeValue
        except KeyError:
            error = "Invalid XML, domain name not found."
            raise TestSetupException(error)

        try:
            return conn.lookupByName(name)
        except libvirt.libvirtError:
            return conn.createXML(xml_content)
