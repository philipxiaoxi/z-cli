"""skills 命令 —— 管理 AI skills 的安装。"""

import shutil
import sys
from pathlib import Path

from .base import Command

AGENTS = ["opencode", "claude", "codex"]


def _skills_dir(agent: str) -> Path:
    home = Path.home()
    paths = {
        "opencode": home / ".config" / "opencode" / "skills",
        "claude": home / ".claude" / "skills",
        "codex": home / ".agents" / "skills",
    }
    return paths[agent]


class SkillsCommand(Command):
    name = "skills"
    help = "管理 AI skills"

    def register(self, parser):
        sub = parser.add_subparsers(dest="skills_action", required=True)

        p = sub.add_parser("install", help="安装 skill 到指定 AI agent")
        p.add_argument("name", help="skill 名称（src/zspace/skills/<name>/ 目录）")
        p.add_argument(
            "--agent",
            action="append",
            required=True,
            choices=AGENTS,
            dest="agents",
            help="目标 AI agent（可多次指定）",
        )

        p = sub.add_parser("uninstall", help="卸载指定 AI agent 的 skill")
        p.add_argument("name", help="skill 名称")
        p.add_argument(
            "--agent",
            action="append",
            required=True,
            choices=AGENTS,
            dest="agents",
            help="目标 AI agent（可多次指定）",
        )

    def handle(self, args):
        if args.skills_action == "install":
            self._install(args)
        elif args.skills_action == "uninstall":
            self._uninstall(args)

    def _install(self, args):
        src = Path(__file__).resolve().parent.parent / "skills" / args.name
        if not src.is_dir():
            names = [p.name for p in src.parent.iterdir() if p.is_dir()]
            print(
                f"错误: skill '{args.name}' 不存在",
                file=sys.stderr,
            )
            if names:
                print(f"可用的 skills: {', '.join(names)}", file=sys.stderr)
            sys.exit(1)

        installed = []

        for agent in args.agents:
            dst = _skills_dir(agent) / args.name
            if dst.exists():
                print(f"⚠ {agent}: {dst} 已存在，跳过")
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
            installed.append(agent)

        if installed:
            print(f"\n已安装到: {', '.join(installed)}")
            print("AI 助手将在下次对话时自动加载该 skill。")

    def _uninstall(self, args):
        removed = []

        for agent in args.agents:
            dst = _skills_dir(agent) / args.name
            if not dst.exists():
                print(f"⚠ {agent}: {dst} 不存在，跳过")
                continue
            shutil.rmtree(dst)
            removed.append(agent)

        if removed:
            print(f"\n已从 {', '.join(removed)} 卸载")
