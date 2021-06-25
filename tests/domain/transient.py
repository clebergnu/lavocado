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

import libvirt

from lavocado import LibvirtTest


class TransientDomain(LibvirtTest):
    """Transient domain basic operations.

    The test case validates the core lifecycle and operations on transient
    domains.
    """

    def setUp(self):
        super().setUp()
        self.image = self.get_generic_image()
        self.domain = self.create_domain(arguments={'image': self.image.path})

    def test_lifecycle(self):
        """Creating and destroying a new transient domain.

        A transient domain has no configuration file so, once destroyed, all
        trace of the domain should disappear.
        """
        name = self.domain.name()
        state, _ = self.domain.state()
        self.assertTrue(state, libvirt.VIR_DOMAIN_RUNNING)

        try:
            self.domain.destroy()
        except Exception as ex:
            self.fail(f"destroy() raised an exception: {ex}")

        with self.assertRaises(libvirt.libvirtError) as context:
            self.conn.lookupByName(name)

        expected = f"no domain with matching name '{self.domain.name()}'"
        self.assertTrue(expected in str(context.exception))

    def test_autostart(self):
        """Makes sure autostart is disabled and not allowed on a transient domain.

        The test case validates that the autostart command returns a suitable
        error message when used on a transient domain.
        """

        self.assertFalse(self.domain.autostart())

        with self.assertRaises(libvirt.libvirtError) as context:
            self.domain.setAutostart(True)

        expected = "cannot set autostart for transient domain"
        self.assertTrue(expected in str(context.exception))

    def test_convert_transient_to_persistent(self):
        """Converting transient to persistent should work fine.

        This test case validates that a transient domain can be converted to a
        persistent one. This is achieved by defining a configuration file while
        the transient domain is running.
        """
        # Creating a new transient domain
        name = self.domain.name()

        # Make sure is running and not persistent
        state, _ = self.domain.state()
        self.assertTrue(state, libvirt.VIR_DOMAIN_RUNNING)
        self.assertFalse(self.domain.isPersistent())

        # Defining config for transient guest
        new_domain = self.conn.defineXML(self.domain.XMLDesc())
        self.assertTrue(new_domain.isPersistent())

        # Destroying active domain
        self.domain.destroy()

        # Checking that an inactive domain config still exists
        found = self.conn.lookupByName(name)
        self.assertEqual(found.name(), name)

        # Removing inactive domain config
        new_domain.undefine()

        # Checking that inactive domain has really gone
        with self.assertRaises(libvirt.libvirtError) as context:
            self.conn.lookupByName(name)
        expected = f"no domain with matching name '{name}'"
        self.assertTrue(expected in str(context.exception))
