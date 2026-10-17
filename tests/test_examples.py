import ast
import importlib.util
import inspect
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("client", ROOT / "scripts" / "client.py")
client = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(client)


class ExampleTests(unittest.TestCase):
    def test_fenced_examples_parse_without_execution(self):
        root = Path(__file__).parents[1]
        for name in ("README.md", "SKILL.md", "STARTER_RELAY.md"):
            text = (root / name).read_text(encoding="utf-8")
            for number, match in enumerate(re.finditer(r"```(python|bash)\n(.*?)```", text, re.S)):
                with self.subTest(file=name, block=number):
                    if match[1] == "python":
                        ast.parse(match[2])
                    else:
                        subprocess.run(["bash", "-n"], input=match[2], text=True, check=True, capture_output=True, encoding="utf-8")
            self.assertNotIn("ND_KEY=$(jq", text)
            self.assertNotIn("# 3. Fetch data =", text)

    def test_documented_polling_matches_helper_defaults(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"\*\*Polling interval:\*\* every (\d+) seconds?, for up to (\d+) seconds by default", text)
        self.assertIsNotNone(match)
        seen = []
        with patch.object(client, "execute", side_effect=lambda args: seen.append(args) or {"status": "ready"}), \
                patch.object(sys, "argv", ["client.py", "check"]), patch("sys.stdout"):
            client.main()
        self.assertEqual(int(match[1]), inspect.signature(client.poll).parameters["interval"].default)
        self.assertEqual(int(match[2]), seen[0].timeout)


if __name__ == "__main__":
    unittest.main()
