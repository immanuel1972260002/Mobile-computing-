"""Deterministic smoke tests for Assignment 5 simulations."""
import unittest
from background_pipeline import Job,Env,run
from feed_optimizer import exact,adaptive
from video_encoder_selector import choose

class Assignment5Tests(unittest.TestCase):
    def test_good_network_delivers(self):
        r=run([Job("x",5,1)],Env(80,"good",False,True),"priority")
        self.assertEqual(r["successful"],1); self.assertEqual(r["residual_backlog"],0)
    def test_doze_defers(self):
        r=run([Job("x",5,1)],Env(80,"good",True,True),"priority")
        self.assertEqual(r["deferred"],1); self.assertEqual(r["successful"],0)
    def test_mid_execution_permission_revocation_cancels(self):
        r=run([Job("x",5,1)],Env(80,"good",False,True,20,True),"priority")
        self.assertEqual(r["cancelled"],1); self.assertEqual(r["successful"],0)
    def test_exact_enumerates_27(self):
        _,n=exact("balanced"); self.assertEqual(n,27)
    def test_trap_is_not_globally_optimal(self):
        (best,_),_=exact("trap"); _,approx,_,_=adaptive("trap",14,60)
        self.assertGreater(approx,best)
    def test_video_selector_returns_valid_resolution(self):
        out=choose({"cpu":1.2,"battery":58,"network_mbps":8,"camera_max":1080})
        self.assertIn(out["resolution"],[480,720,1080,2160])

if __name__=="__main__":
    unittest.main(verbosity=2)
