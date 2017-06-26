# Unix SMB/CIFS implementation.
# Copyright (C) Lumír Balhar <lbalhar@redhat.com> 2017
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""Tests for the Credentials Python bindings.

Note that this just tests the bindings work. It does not intend to test
the functionality, that's already done in other tests.
"""

from samba import netbios, NTSTATUSError
import samba.tests


class NetbiosTests(samba.tests.TestCase):

    def setUp(self):
        super(NetbiosTests, self).setUp()
        self.node = netbios.Node()

    def test_timeout(self):
        self.assertRaises(NTSTATUSError,
                          self.node.query_name, 'test', '127.0.0.7', timeout=0)

    def test_unreachable_system(self):
        self.assertRaises(NTSTATUSError,
                          self.node.query_name, 'test', '0.0.0.0', timeout=5)

    def test_name_release(self):
        # This method is not implemented yet
        self.assertIsNone(self.node.release_name())
