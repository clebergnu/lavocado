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
from lavocado.exceptions import TestSetupException
from lavocado.helpers.domains import Domain


class BaseLibvirtTest(Test):
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

    def create_domain(self, arguments=None):
        """Creates a libvirt domain based on a generic template.

        This will receive some arguments that will be rendered on the
        template.  For more information about the arguments, see
        templates/domain.xml.jinja.

        If you are using this method from a test method (different from
        setUp()), AND you would like to count its call as a "setup/bootstrap"
        stage, consider using the following Avocado decorator:

        from avocado.core.decorators import cancel_on

        @cancel_on(TestSetupException)
        def test_foo(self):
          ...

        In that way, your test will not FAIL, instead it will be cancelled in
        case of any problem during this bootstrap.

        :param dict arguments: A key,value dictionary with the arguments
                               to be replaced on the template. If
                               any missing argument, template will be
                               rendered with default values.
        """
        try:
            return Domain.from_xml_template(self.conn, self.id(), arguments)
        # This will catch any avocado exception plus any os error
        except Exception as ex:
            msg = f"Failed to create domain: {ex}"
            raise TestSetupException(msg) from ex

    def get_generic_image(self):
        """Ask Avocado to fetch an VM image snapshot.

        Avocado will handle if image is already downloaded into the
        cache dir and also will make sure the checksum is matching.

        This will return an Image object pointing to a snapshot file. So
        multiple calls of this method will never return the same object.

        If you are using this method from a test method (different from
        setUp()), AND you would like to count its call as a "setup/bootstrap"
        stage, consider using the following Avocado decorator:

        from avocado.core.decorators import cancel_on

        @cancel_on(TestSetupException)
        def test_foo(self):
          ...

        In that way, your test will not FAIL, instead it will be cancelled in
        case of any problem during this bootstrap.
        """
        image = self.defaults.VMIMAGE
        try:
            return vmimage.get(name=image.get('provider'),
                               version=image.get('version'),
                               cache_dir=self.defaults.CACHE_DIR,
                               checksum=image.get('checksum'))
        # This will catch any error, including avocado exceptions + OS errors
        except Exception as ex:
            msg = f"Failed to get a generic image: {ex}"
            raise TestSetupException(msg) from ex

    def tearDown(self):
        """Shutdown after each test.

        This will destroy all previously created domains by this test, and
        remove any image snapshot if created.
        """
        for domain in self.conn.listAllDomains():
            if domain.name().endswith(self.id()):
                domain.destroy()

        if hasattr(self, 'image') and isinstance(self.image, vmimage.Image):
            if os.path.exists(self.image.path):
                os.remove(self.image.path)
        self.conn.close()
