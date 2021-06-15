# Copyright (C) 2021 Red Hat, Inc.
# Author: Beraldo Leal <bleal@redhat.com>
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


import socket

from lavocado import LibvirtTest


class LibVirtHypervisorBasic(LibvirtTest):
    def test_hypervisor_version(self):
        version = self.conn.getVersion()
        self.assertEqual(type(version), int)
        self.assertGreater(version, 400000)

    def test_libvirt_version(self):
        version = self.conn.getLibVersion()
        self.assertEqual(type(version), int)
        self.assertGreater(version, 600000)

    def test_getinfo(self):
        info = self.conn.getInfo()
        self.assertEqual(type(info), list)

    def test_get_hostname(self):
        hostname = self.conn.getHostname()
        self.assertEqual(type(hostname), str)
        self.assertEqual(socket.gethostname(), hostname)
