import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit',ROOT/'scripts/audit-publication.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
class PublicationTests(unittest.TestCase):
    def test_key_and_private_network_rejected_without_echoing_value(self):
        key='-----BEGIN '+'OPENSSH '+'PRIVATE KEY-----'
        address='10.'+'24.16.8'
        self.assertIn('private-key',audit.findings('notes.md',(key+' '+address).encode()))
        self.assertIn('private-network-address',audit.findings('notes.md',address.encode()))
    def test_recovery_artifacts_rejected(self):
        self.assertIn('private-or-binary-artifact',audit.findings('backups/boot.tar.gz',b'x'))
    def test_generic_reference_is_allowed(self):
        self.assertEqual([],audit.findings('docs/example.md',b'Mac15,10; see manifests/known-good.json and https://github.com/nickfoy/omarchy-m3-max'))
    def test_candidate_allows_only_public_firmware_fixtures(self):
        known=('F493F03E'+'-CC40-3D89-9A08-5F259BA2B246').encode()
        unknown=('12345678'+'-1234-1234-1234-123456789abc').encode()
        path='patches/linux-aurora-j514m-panel.patch'
        self.assertEqual([],audit.findings(path,known))
        self.assertIn('uuid',audit.findings(path,unknown))
        self.assertIn('uuid',audit.findings('notes.md',known))
    def test_agent_workflows_have_distinct_gates(self):
        install=(ROOT/'prompts/install.md').read_text();update=(ROOT/'prompts/update.md').read_text()
        for text in [install,update]:
            for token in ['check-hardware.sh','UNKNOWN','UNSUPPORTED','approval','suspend','recovery']:
                self.assertIn(token,text)
        self.assertIn('do not replace',install.lower())
        self.assertIn('baseline promotion only after validation',update.lower())
        self.assertIn('previous',update.lower())
if __name__=='__main__':unittest.main()
