import contextlib
import io
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('verification', Path(__file__).parents[1] / 'lib/verification.py')
v = importlib.util.module_from_spec(SPEC)
if SPEC.loader and Path(SPEC.origin).exists():
    SPEC.loader.exec_module(v)

class VerificationTests(unittest.TestCase):
    def test_machine_name_alone_is_not_verified(self):
        self.assertTrue(hasattr(v, 'hardware_gate'), 'hardware gate must exist')
        self.assertEqual(v.hardware_gate({'model_identifier':'Mac15,10','compatible':[], 'architecture':'aarch64','cpu_cores':14,'memory_gib':36,'os_id':'archarm','omarchy_version':'4.5.0-3'})['status'], 'UNKNOWN')

    def test_exact_hardware_and_other_board(self):
        hw = {'model_identifier':'Mac15,10','compatible':['apple,j514m','apple,t6034'],'architecture':'aarch64','cpu_cores':14,'memory_gib':36,'os_id':'archarm','omarchy_version':'4.5.0-3'}
        self.assertEqual(v.hardware_gate(hw)['status'], 'VERIFIED')
        hw['compatible'] = ['apple,j516c','apple,t6034']
        self.assertEqual(v.hardware_gate(hw)['status'], 'UNSUPPORTED')

    def test_gpu_software_and_missing_evidence(self):
        self.assertEqual(v.gpu_result('llvmpipe (LLVM 19)', ['asahi-g15'])['status'], 'FAIL')
        self.assertEqual(v.gpu_result(None, ['asahi-g15'])['status'], 'UNKNOWN')
        self.assertEqual(v.gpu_result('Apple M3 Max', ['asahi-g15'])['status'], 'PASS')
        self.assertEqual(v.gpu_result('Apple M3 Max', [None])['status'], 'FAIL')

    def test_disconnected_external_is_ok(self):
        drm = {'eDP-1':'connected','DP-1':'disconnected','DP-2':'disconnected'}
        monitors = [{'name':'eDP-1','width':3024,'height':1964,'refreshRate':120.0,'disabled':False}]
        self.assertEqual(v.display_result(drm, monitors, False)['status'], 'PASS')
        monitors[0]['refreshRate'] = 60
        self.assertEqual(v.display_result(drm, monitors, False)['status'], 'FAIL')

    def test_clamshell_and_disabled_external(self):
        drm = {'eDP-1':'connected','DP-1':'connected'}
        monitors = [{'name':'DP-1','width':3840,'height':2160,'refreshRate':60}]
        self.assertEqual(v.display_result(drm, monitors, True)['status'], 'PASS')
        self.assertEqual(v.display_result(drm, monitors, None)['status'], 'UNKNOWN')
        monitors[0]['width'] = 0
        self.assertEqual(v.display_result(drm, monitors, True)['status'], 'FAIL')

    def test_sysfs_and_public_inventory_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'sys/class/dmi/id').mkdir(parents=True)
            (root/'sys/class/dmi/id/product_name').write_text('Mac15,10\n')
            (root/'proc/device-tree').mkdir(parents=True)
            (root/'proc/device-tree/compatible').write_bytes(b'apple,j514m\0apple,t6034\0')
            (root/'proc/meminfo').write_text('MemTotal:       36800000 kB\n')
            with patch.object(v.os, 'cpu_count', return_value=14), patch.object(v.platform, 'machine', return_value='aarch64'):
                hw = v.read_hardware(root)
            self.assertEqual(hw['compatible'], ['apple,j514m','apple,t6034'])
            self.assertNotIn('hostname', hw)
            self.assertNotIn('/home/', str(hw))

    def test_os_identity_required(self):
        hw={'model_identifier':'Mac15,10','compatible':['apple,j514m','apple,t6034'], 'architecture':'aarch64','cpu_cores':14,'memory_gib':36}
        self.assertEqual(v.hardware_gate(hw)['status'],'UNKNOWN')
        hw.update(os_id='ubuntu',omarchy_version='4.5.0-3')
        self.assertEqual(v.hardware_gate(hw)['status'],'UNSUPPORTED')
        hw.update(os_id='archarm',architecture=None)
        self.assertEqual(v.hardware_gate(hw)['status'],'UNKNOWN')

    def test_missing_internal_is_unknown(self):
        self.assertEqual(v.display_result({'DP-1':'disconnected'}, [], False)['status'],'UNKNOWN')

    def test_inventory_missing_packages_is_unknown(self):
        with patch.object(v,'packages',return_value=None):
            self.assertEqual(v.inventory()['status'],'UNKNOWN')

    def test_capture_failure_leaves_private_files_and_restores_umask(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'failed'
            old=v.os.umask(0o022)
            try:
                with patch.object(v,'inventory',return_value={}), patch.object(v.tarfile,'open',side_effect=OSError('fixture')):
                    with self.assertRaises(OSError): v.capture(output)
                self.assertEqual(output.stat().st_mode & 0o777,0o700)
                self.assertEqual((output/'inventory.json').stat().st_mode & 0o777,0o600)
                restored=v.os.umask(0o022)
                self.assertEqual(restored,0o022)
            finally:
                v.os.umask(old)

    def test_capture_refuses_repository(self):
        with self.assertRaises(ValueError):
            v.capture(v.ROOT/'ignored-private-capture')

    def test_public_baseline_compares_only_critical_subset(self):
        self.assertEqual(v.package_comparison({'mesa':'1'},{'mesa':'1','other':'2'}, critical_only=True)['status'],'PASS')
        self.assertEqual(v.package_comparison({'mesa':'1'},{'mesa':'1','other':'2'})['status'],'DIFFERENT')

    def test_vulkan_public_properties_exclude_identifiers(self):
        raw=bytearray(4096)
        struct.pack_into('=IIIII',raw,0,4202496,123,0x106b,999,1)
        raw[20:20+len(b'Apple M3 Max')]=b'Apple M3 Max'
        raw[276:292]=b'private-uuid-1234'
        data=v.vulkan_properties(raw)
        self.assertEqual(data['name'],'Apple M3 Max')
        self.assertEqual(data['vendorID'],0x106b)
        self.assertNotIn('private',str(data))
        self.assertNotIn('deviceID',data)
        with patch.object(v.ctypes, 'CDLL', side_effect=OSError):
            self.assertEqual(v.vulkan_devices()['state'],'unavailable')

    def test_zero_external_refresh_is_failure(self):
        self.assertEqual(v.display_result({'DP-1':'connected','eDP-1':'disconnected'}, [{'name':'DP-1','width':1920,'height':1080,'refreshRate':0}], True)['status'], 'FAIL')

    def test_private_capture_and_unsupported_compare(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'capture'
            with patch.object(v, 'inventory', return_value={'status':'PASS','packages':{'mesa':'1'}}), patch.object(v.Path, 'home', return_value=Path(tmp)/'empty'):
                self.assertEqual(v.capture(output)['status'], 'PASS')
            self.assertEqual(output.stat().st_mode & 0o777, 0o700)
            self.assertEqual((output/'inventory.json').stat().st_mode & 0o777, 0o600)
            with patch.object(v, 'read_hardware', return_value={'model_identifier':'Other','compatible':['other']}), patch.object(v, 'packages', side_effect=AssertionError('must not query packages')):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(v.main(['compare-baseline', str(output), '--json']), 1)

    def test_inactive_internal_cannot_pass_with_open_or_unknown_lid(self):
        self.assertEqual(v.display_result({'eDP-1':'disconnected'}, [], False)['status'], 'FAIL')
        self.assertEqual(v.display_result({'eDP-1':None}, [], None)['status'], 'UNKNOWN')
        self.assertEqual(v.display_result({'eDP-1':'disconnected'}, [], True)['status'], 'PASS')

    def test_capture_incomplete_inventory_is_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(v,'inventory',return_value={'status':'UNKNOWN','packages':None}), patch.object(v.Path,'home',return_value=Path(tmp)/'empty'):
                self.assertEqual(v.capture(Path(tmp)/'capture')['status'],'UNKNOWN')

    def test_logind_lid_missing_and_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            switch = root/'sys/class/input/input0/capabilities'
            switch.mkdir(parents=True)
            (switch/'sw').write_text('1\n')
            with patch.object(v, 'run', return_value='b true\n'):
                self.assertIs(v.lid_state(root), True)
            with patch.object(v, 'run', return_value=None):
                self.assertIsNone(v.lid_state(root))

    def test_package_difference_is_not_failure(self):
        self.assertEqual(v.package_comparison({'mesa':'1'}, {'mesa':'2'})['status'], 'DIFFERENT')

if __name__ == '__main__':
    unittest.main()
