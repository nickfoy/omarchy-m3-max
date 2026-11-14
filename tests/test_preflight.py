import importlib.util
import pathlib
import unittest
p = pathlib.Path(__file__).resolve().parents[1] / 'lib/update_preflight.py'
spec = importlib.util.spec_from_file_location('preflight', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class PreflightTests(unittest.TestCase):
    def plan(self, name='example-editor'):
        return dict(schema_version=1,hardware_status='VERIFIED',complete=True,solver_success=True,metadata_fresh=True,transactions=[dict(name=name,old_version='1',new_version='2',operation='upgrade',depends=[],provides=[],conflicts=[],replaces=[],files=[])],ignored_packages=[],incompatibilities=[])
    def test_application(self): self.assertEqual(m.assess(self.plan())['status'],'SAFE')
    def test_actual_aurora_names(self):
        for name in ('mesa-aurora','vulkan-aurora','omarchy-aurora-firmware','hyprgraphics','asahi-alarm-keyring'):
            self.assertEqual(m.assess(self.plan(name))['status'],'REVIEW REQUIRED',name)
    def test_omitted_metadata(self):
        p=self.plan(); del p['transactions'][0]['files']; self.assertEqual(m.assess(p)['status'],'BLOCKED')
    def test_candidates_visible(self):
        p=self.plan(); self.assertEqual(m.assess(p)['transactions'],p['transactions'])
    def test_kernel_review(self): self.assertEqual(m.assess(self.plan('linux-aurora'))['status'],'REVIEW REQUIRED')
    def test_incompatibility(self):
        p=self.plan(); p['incompatibilities']=['unsatisfied platform ABI']; self.assertEqual(m.assess(p)['status'],'BLOCKED')
    def test_ignored_partial(self):
        p=self.plan(); p['ignored_packages']=['linux-aurora']; self.assertEqual(m.assess(p)['status'],'BLOCKED')
    def test_solver(self):
        for key in ['complete','solver_success']:
            p=self.plan(); p[key]=False; self.assertEqual(m.assess(p)['status'],'BLOCKED')
    def test_hardware(self):
        p=self.plan(); p['hardware_status']='UNKNOWN'; self.assertEqual(m.assess(p)['status'],'BLOCKED')
    def test_missing_metadata(self): self.assertEqual(m.assess({})['status'],'BLOCKED')
    def test_dependency_alias(self):
        p=self.plan(); p['transactions'][0]['provides']=['linux-aurora=2']; self.assertEqual(m.assess(p)['status'],'REVIEW REQUIRED')
    def test_runtime_uninspected(self):
        p=self.plan(); p['runtime_uninspected']=True; self.assertEqual(m.assess(p)['status'],'REVIEW REQUIRED')
    def test_malformed_repository_comparison_is_blocked(self):
        for comparisons in (None, ['invalid'], [{'relation':'local-newer'}]):
            p=self.plan(); p['repository_comparisons']=comparisons
            self.assertEqual(m.assess(p)['status'],'BLOCKED')
    def test_omarchy_scope(self): self.assertEqual(m.assess(self.plan(), 'omarchy')['status'],'REVIEW REQUIRED')
if __name__ == '__main__': unittest.main()
