import unittest

from installer.ui import InstallPlan


class InstallerUiTests(unittest.TestCase):
    def test_plan_defaults(self) -> None:
        plan = InstallPlan()
        self.assertEqual(plan.mode, "standard")
        self.assertTrue(plan.create_shortcut)

    def test_quick_plan(self) -> None:
        plan = InstallPlan(mode="quick", create_shortcut=False)
        self.assertEqual(plan.mode, "quick")
        self.assertFalse(plan.create_shortcut)


if __name__ == "__main__":
    unittest.main()
