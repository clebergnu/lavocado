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

"""Basic test helper module to avoid code redundancy."""

import os
import libvirt

from avocado import Test
from avocado.utils import vmimage

from lavocado import defaults
from lavocado.helpers.domains import Domain


class LibvirtTest(Test):
    """Main class helper for tests.

    Any test that inherits from this class, will have some methods and
    properties to assist on their jobs.
    """
    def setUp(self):
        """Setup to be executed before each test.

        Currently, this method is creating just a basic hypervisor connection.
        Please, extend this method when writing your tests for your own needs.

        Any error that happens here *will not* flag the test as "FAIL", instead
        tests will be flagged as "ERROR", meaning that some bootstrap error has
        happened.
        """
        self.defaults = defaults
        self.conn = self.connect()

    def connect(self):
        try:
            return libvirt.open(self.defaults.LIBVIRT_URI)
        except libvirt.libvirtError:
            msg = ("Failed to open connection with the hypervisor using "
                   + self.defaults.LIBVIRT_URI)
            self.cancel(msg)

    # TODO: Use @fail_on decorator
    def create_domain(self, arguments=None, fail=False):
        """Creates a libvirt domain based on a generic template.

        This will receive some arguments that will be rendered on the
        template.  For more information about the arguments, see
        templates/domain.xml.jinja. By default this method will not fail
        the test, instead will mark the test as ERROR if any issue
        happens here.

        :param dict arguments: A key,value dictionary with the arguments
                               to be replaced on the template. If
                               any missing argument, template will be
                               rendered with default values.
        :param bool fail: If True, any error during this execution will
                          trigger a test fail, otherwise, will trigger a
                          test error. Default is False.
        """
        try:
            return Domain.from_xml_template(self.conn, self.id(), arguments)
        except Exception as ex:
            msg = f"Failed to create domain: {ex}"
            if fail:
                self.fail(msg)
            else:
                self.error(msg)

    def get_generic_image(self, fail=False):
        """Ask Avocado to fetch an VM image snapshot.

        Avocado will handle if image is already downloaded into the
        cache dir and also will make sure the checksum is matching.

        This will return an Image object pointing to a snapshot file. So
        multiple calls of this method will never return the same object.

        :param bool fail: If True, any error during this execution will
                          trigger a test fail, otherwise, will trigger a
                          test error. Default is False.
        """
        image = self.defaults.VMIMAGE
        try:
            return vmimage.get(name=image.get('provider'),
                               version=image.get('version'),
                               cache_dir=self.defaults.CACHE_DIR,
                               checksum=image.get('checksum'))
        except Exception as ex:
            msg = f"Failed to get a generic image: {ex}"
            if fail:
                self.fail(msg)
            else:
                self.error(msg)

    def tearDown(self):
        """Shutdown after each test.

        This will destroy all previously created domains by this test, and
        remove any image snapshot if created.
        """
        # TODO: At this point, we need only transient machines, use always
        # destroy()
        for domain in self.conn.listAllDomains():
            if domain.name().endswith(self.id()):
                if domain.isPersistent():
                    domain.undefine()
                else:
                    domain.destroy()

        if hasattr(self, 'image') and isinstance(self.image, vmimage.Image):
            if os.path.exists(self.image.path):
                os.remove(self.image.path)
        self.conn.close()
