"""CLI 入口 —— 命令注册与分发，不包含具体业务逻辑。"""

import argparse

from .commands import register_all


def main():
    parser = argparse.ArgumentParser(
        prog="zcli",
        description="zspace私有云命令行工具",
    )
    # 创建子命令容器：每个子命令注册时通过 set_defaults(_handler=...) 绑定自己的 handle 方法
    # dest="command"：子命令名称存入 args.command（argparse 要求必填）
    # required=True：用户必须输入子命令，否则报错
    register_all(parser.add_subparsers(dest="command", required=True))

    # 解析命令行参数，自动路由到对应子命令
    args = parser.parse_args()

    # 执行命令：直接调注册时绑定的 handle 方法，无需 if/elif 判断
    args._handler(args)


if __name__ == "__main__":
    main()
