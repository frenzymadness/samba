# Unix SMB/CIFS implementation.
# Copyright (C) Jelmer Vernooij <jelmer@samba.org> 2007
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

from samba import credentials
import samba.tests
import os

class CredentialsTests(samba.tests.TestCase):

    def setUp(self):
        super(CredentialsTests, self).setUp()
        self.creds = credentials.Credentials()

    def test_set_username(self):
        self.creds.set_username("somebody")
        self.assertEqual("somebody", self.creds.get_username())

    def test_set_password(self):
        self.creds.set_password("S3CreT")
        self.assertEqual("S3CreT", self.creds.get_password())

    def test_set_utf16_password(self):
        password = 'S3cRet'
        passbytes = password.encode('utf-16-le')
        self.assertTrue(self.creds.set_utf16_password(passbytes))
        self.assertEqual(password, self.creds.get_password())

    def test_set_old_password(self):
        self.assertEqual(None, self.creds.get_old_password())
        self.assertTrue(self.creds.set_old_password("S3c0ndS3CreT"))
        self.assertEqual("S3c0ndS3CreT", self.creds.get_old_password())

    def test_set_old_utf16_password(self):
        password = '0ldS3cRet'
        passbytes = password.encode('utf-16-le')
        self.assertTrue(self.creds.set_old_utf16_password(passbytes))
        self.assertEqual(password, self.creds.get_old_password())

    def test_set_domain(self):
        self.creds.set_domain("ABMAS")
        self.assertEqual("ABMAS", self.creds.get_domain())

    def test_set_realm(self):
        self.creds.set_realm("myrealm")
        self.assertEqual("MYREALM", self.creds.get_realm())

    def test_parse_string_anon(self):
        self.creds.parse_string("%")
        self.assertEqual("", self.creds.get_username())
        self.assertEqual(None, self.creds.get_password())

    def test_parse_string_user_pw_domain(self):
        self.creds.parse_string("dom\\someone%secr")
        self.assertEqual("someone", self.creds.get_username())
        self.assertEqual("secr", self.creds.get_password())
        self.assertEqual("DOM", self.creds.get_domain())

    def test_bind_dn(self):
        self.assertEqual(None, self.creds.get_bind_dn())
        self.creds.set_bind_dn("dc=foo,cn=bar")
        self.assertEqual("dc=foo,cn=bar", self.creds.get_bind_dn())

    def test_is_anon(self):
        self.creds.set_username("")
        self.assertTrue(self.creds.is_anonymous())
        self.creds.set_username("somebody")
        self.assertFalse(self.creds.is_anonymous())
        self.creds.set_anonymous()
        self.assertTrue(self.creds.is_anonymous())

    def test_workstation(self):
        # FIXME: This is uninitialised, it should be None
        #self.assertEqual(None, self.creds.get_workstation())
        self.creds.set_workstation("myworksta")
        self.assertEqual("myworksta", self.creds.get_workstation())

    def test_get_nt_hash(self):
        self.creds.set_password("geheim")
        self.assertEqual(b'\xc2\xae\x1f\xe6\xe6H\x84cRE>\x81o*\xeb\x93',
                         self.creds.get_nt_hash())

    def test_set_cmdline_callbacks(self):
        self.creds.set_cmdline_callbacks()

    def test_authentication_requested(self):
        self.creds.set_username("")
        self.assertFalse(self.creds.authentication_requested())
        self.creds.set_username("somebody")
        self.assertTrue(self.creds.authentication_requested())

    def test_wrong_password(self):
        self.assertFalse(self.creds.wrong_password())

    def test_guess(self):
        creds = credentials.Credentials()
        lp = samba.tests.env_loadparm()
        os.environ["USER"] = "env_user"
        creds.guess(lp)
        self.assertEqual(creds.get_username(), "env_user")
        self.assertEqual(creds.get_domain(), lp.get("workgroup").upper())
        self.assertEqual(creds.get_realm(), lp.get("realm").upper())
        self.assertEqual(creds.is_anonymous(), False)
        self.assertEqual(creds.authentication_requested(), False)

    def test_set_anonymous(self):
        creds = credentials.Credentials()
        lp = samba.tests.env_loadparm()
        os.environ["USER"] = "env_user"
        creds.guess(lp)
        creds.set_anonymous()
        self.assertEqual(creds.get_username(), "")
        self.assertEqual(creds.get_domain(), "")
        self.assertEqual(creds.get_realm(), None)
        self.assertEqual(creds.is_anonymous(), True)
        self.assertEqual(creds.authentication_requested(), False)

    def test_parse_username(self):
        creds = credentials.Credentials()
        lp = samba.tests.env_loadparm()
        os.environ["USER"] = "env_user"
        creds.guess(lp)
        creds.parse_string("user")
        self.assertEqual(creds.get_username(), "user")
        self.assertEqual(creds.get_domain(), lp.get("workgroup").upper())
        self.assertEqual(creds.get_realm(), lp.get("realm").upper())
        self.assertEqual(creds.is_anonymous(), False)
        self.assertEqual(creds.authentication_requested(), True)

    def test_parse_username_with_domain(self):
        creds = credentials.Credentials()
        lp = samba.tests.env_loadparm()
        os.environ["USER"] = "env_user"
        creds.guess(lp)
        creds.parse_string("domain\\user")
        self.assertEqual(creds.get_username(), "user")
        self.assertEqual(creds.get_domain(), "DOMAIN")
        self.assertEqual(creds.get_realm(), lp.get("realm").upper())
        self.assertEqual(creds.is_anonymous(), False)
        self.assertEqual(creds.authentication_requested(), True)

    def test_parse_username_with_realm(self):
        creds = credentials.Credentials()
        lp = samba.tests.env_loadparm()
        os.environ["USER"] = "env_user"
        creds.guess(lp)
        creds.parse_string("user@samba.org")
        self.assertEqual(creds.get_username(), "env_user")
        self.assertEqual(creds.get_domain(), lp.get("workgroup").upper())
        self.assertEqual(creds.get_realm(), "SAMBA.ORG")
        self.assertEqual(creds.is_anonymous(), False)
        self.assertEqual(creds.authentication_requested(), True)

    def test_parse_username_pw(self):
        creds = credentials.Credentials()
        lp = samba.tests.env_loadparm()
        os.environ["USER"] = "env_user"
        creds.guess(lp)
        creds.parse_string("user%pass")
        self.assertEqual(creds.get_username(), "user")
        self.assertEqual(creds.get_password(), "pass")
        self.assertEqual(creds.get_domain(), lp.get("workgroup"))
        self.assertEqual(creds.get_realm(), lp.get("realm"))
        self.assertEqual(creds.is_anonymous(), False)
        self.assertEqual(creds.authentication_requested(), True)

    def test_parse_username_with_domain_pw(self):
        creds = credentials.Credentials()
        lp = samba.tests.env_loadparm()
        os.environ["USER"] = "env_user"
        creds.guess(lp)
        creds.parse_string("domain\\user%pass")
        self.assertEqual(creds.get_username(), "user")
        self.assertEqual(creds.get_domain(), "DOMAIN")
        self.assertEqual(creds.get_password(), "pass")
        self.assertEqual(creds.get_realm(), lp.get("realm"))
        self.assertEqual(creds.is_anonymous(), False)
        self.assertEqual(creds.authentication_requested(), True)

    def test_parse_username_with_realm_pw(self):
        creds = credentials.Credentials()
        lp = samba.tests.env_loadparm()
        os.environ["USER"] = "env_user"
        creds.guess(lp)
        creds.parse_string("user@samba.org%pass")
        self.assertEqual(creds.get_username(), "env_user")
        self.assertEqual(creds.get_domain(), lp.get("workgroup").upper())
        self.assertEqual(creds.get_password(), "pass")
        self.assertEqual(creds.get_realm(), "SAMBA.ORG")
        self.assertEqual(creds.get_principal(), "user@samba.org")
        self.assertEqual(creds.is_anonymous(), False)
        self.assertEqual(creds.authentication_requested(), True)
