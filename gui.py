import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path
import subprocess
from preset_manager import PresetManager
from config import (
    EXCLUDE_DIRS, DEFAULT_TARGET_FILES,
    SUPPORTED_EXTENSIONS, DEFAULT_OUTPUT_DIR
)
from main import generate_summary

def main():
    window = tk.Tk()
    window.title("Context Generator")
    window.geometry("820x450")

    preset_manager = PresetManager()
    # 起動時のディレクトリを取得
    initial_dir = Path.cwd()

    def pick_root_dir():
        result = filedialog.askdirectory(initialdir=root_dir.get())
        if result:
            root_dir.set(result)
            load_preset(Path(result))

    def pick_output_dir():
        result = filedialog.askdirectory(initialdir=output_dir.get())
        if result:
            output_dir.set(result)

    def load_preset(directory: Path):
        preset_data = preset_manager.load_preset(directory)
        if preset_data:
            exclude_dirs.set(preset_data.get('exclude_dirs', exclude_dirs.get()))
            output_dir.set(preset_data.get('output_dir', output_dir.get()))
            target_files.set(preset_data.get('target_files', target_files.get()))
            preset_extensions = preset_data.get('include_extensions', [])
            for ext, var in extension_vars.items():
                var.set(ext in preset_extensions)
            output_format.set(preset_data.get('output_format', output_format.get()))

    root_dir = tk.StringVar(value=str(initial_dir))
    exclude_dirs = tk.StringVar(value=", ".join(EXCLUDE_DIRS))
    output_dir = tk.StringVar(value=str(DEFAULT_OUTPUT_DIR))
    output_format = tk.StringVar(value=".md")  # デフォルト値を .md に設定
    target_files = tk.StringVar(value=", ".join(DEFAULT_TARGET_FILES))

    extension_vars = {ext: tk.BooleanVar(value=ext in [".md", ".py"]) for ext in SUPPORTED_EXTENSIONS}

    # 起動時にJSONファイルをロード
    if (initial_dir / "summary.config.json").exists():
        load_preset(initial_dir)

    ttk.Label(window, text="ルートディレクトリ:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    ttk.Entry(window, textvariable=root_dir, width=50, state="readonly").grid(row=0, column=1, padx=10, pady=5)
    ttk.Button(window, text="参照", command=pick_root_dir).grid(row=0, column=2, padx=10, pady=5)

    ttk.Label(window, text="除外ディレクトリ (カンマ区切り):").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    ttk.Entry(window, textvariable=exclude_dirs, width=50).grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(window, text="含める拡張子:").grid(row=2, column=0, sticky=tk.NW, padx=10, pady=5)
    extension_frame = ttk.Frame(window)
    extension_frame.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
    for i, ext in enumerate(SUPPORTED_EXTENSIONS):
        ttk.Checkbutton(extension_frame, text=ext, variable=extension_vars[ext]).grid(row=i // 5, column=i % 5,
                                                                                      sticky=tk.W, padx=5, pady=2)

    ttk.Label(window, text="出力ディレクトリ:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
    ttk.Entry(window, textvariable=output_dir, width=50, state="readonly").grid(row=3, column=1, padx=10, pady=5)
    ttk.Button(window, text="参照", command=pick_output_dir).grid(row=3, column=2, padx=10, pady=5)

    ttk.Label(window, text="対象ファイル (カンマ区切り):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
    ttk.Entry(window, textvariable=target_files, width=50).grid(row=4, column=1, padx=10, pady=5)
    # ファイル形式選択のラジオボタンを追加
    ttk.Label(window, text="出力ファイル形式:").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
    format_frame = ttk.Frame(window)
    format_frame.grid(row=5, column=1, sticky=tk.W, padx=10, pady=5)
    ttk.Radiobutton(format_frame, text=".md", variable=output_format, value=".md").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(format_frame, text=".txt", variable=output_format, value=".txt").pack(side=tk.LEFT, padx=5)

    def open_output_directory(path: Path):
        if path.exists():
            if Path.cwd().drive:  # Windows
                subprocess.run(['explorer', str(path)])
            else:  # macOS and Linux
                subprocess.run(['open', str(path)])
        else:
            messagebox.showerror("エラー", f"ディレクトリが見つかりません：\n{path}")

    def generate_summary_callback():
        if not root_dir.get():
            messagebox.showerror("エラー", "ルートディレクトリを選択してください。")
            return

        selected_extensions = [ext for ext, var in extension_vars.items() if var.get()]
        output_filename = Path(root_dir.get()).name + output_format.get()

        # プリセットの保存
        preset_data = {
            'exclude_dirs': exclude_dirs.get(),
            'include_extensions': selected_extensions,
            'output_dir': output_dir.get(),
            'target_files': target_files.get(),
            'output_format': output_format.get()  # 出力形式も保存
        }
        preset_manager.save_preset(Path(root_dir.get()), preset_data)

        try:
            file_stats, total_chars = generate_summary(
                Path(root_dir.get()),
                [dir.strip() for dir in exclude_dirs.get().split(",")],
                selected_extensions,
                output_filename,
                Path(output_dir.get()),
                [file.strip() for file in target_files.get().split(",")]
            )

            # ファイル統計情報を整形
            stats_message = ""
            for ext, data in file_stats.items():
                stats_message += f"{ext}: {data['count']}個, {data['chars']}文字\n"

            # 成功メッセージとファイル統計情報を表示
            messagebox.showinfo("成功",
                                f"サマリーが生成されました。\n\n"
                                f"{stats_message}\n"
                                f"合計文字数: {total_chars}文字\n\n"
                                f"保存先: {Path(output_dir.get()) / output_filename}"
                                )
            open_output_directory(Path(output_dir.get()))
        except Exception as e:
            messagebox.showerror("エラー", f"サマリーの生成中にエラーが発生しました：\n{str(e)}")

    ttk.Button(window, text="サマリーを生成", command=generate_summary_callback).grid(row=6, column=1, pady=20)

    window.mainloop()

if __name__ == "__main__":
    main()