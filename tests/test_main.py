import tempfile
import unittest
from pathlib import Path
import shutil
from main import generate_summary


class TestGenerateSummary(unittest.TestCase):
    def setUp(self):
        # テスト用の一時ディレクトリを作成
        self.test_dir = Path(tempfile.mkdtemp())

        # テスト用のファイルとディレクトリを作成
        (self.test_dir / "include_dir").mkdir()
        (self.test_dir / "exclude_dir").mkdir()

        with open(self.test_dir / "test_file.txt", "w") as f:
            f.write("Test content")

        with open(self.test_dir / "include_dir" / "included.py", "w") as f:
            f.write("print('This file should be included')")

        with open(self.test_dir / "exclude_dir" / "excluded.py", "w") as f:
            f.write("print('This file should be excluded')")

    def tearDown(self):
        # テスト用の一時ディレクトリを再帰的に削除
        shutil.rmtree(self.test_dir)

    def test_generate_summary(self):
        output_file = "test_summary.md"
        generate_summary(
            self.test_dir,
            exclude_dirs=["exclude_dir"],
            include_extensions=[".txt", ".py"],
            output_file=output_file,
            output_dir=self.test_dir,
            target_files=["test_file.txt"]
        )

        # 出力ファイルが生成されたことを確認
        self.assertTrue((self.test_dir / output_file).exists())

        # 出力ファイルの内容を確認
        with open(self.test_dir / output_file, "r") as f:
            content = f.read()
            self.assertIn("test_file.txt", content)
            self.assertIn("included.py", content)
            self.assertNotIn("excluded.py", content)


if __name__ == '__main__':
    unittest.main()