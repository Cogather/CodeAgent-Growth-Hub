#!/usr/bin/env python3
"""创建系统登录账号。cd backend && PYTHONPATH=. .venv/bin/python scripts/create_user.py --username admin --name 管理员 --role admin"""

from __future__ import annotations

import argparse
import sys

from app.database import SessionLocal
from app.models import SysUser
from app.services.password import generate_temporary_password, hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="创建系统登录账号")
    parser.add_argument("--username", required=True, help="登录用户名")
    parser.add_argument("--name", required=True, help="显示姓名")
    parser.add_argument("--role", choices=["admin", "viewer"], default="viewer", help="角色")
    parser.add_argument("--password", help="初始密码，不传则自动生成")
    args = parser.parse_args()

    username = args.username.strip()
    name = args.name.strip()
    temp_password = args.password or generate_temporary_password()

    if len(temp_password) < 8:
        print("密码长度至少 8 位", file=sys.stderr)
        sys.exit(1)

    db = SessionLocal()
    try:
        if db.query(SysUser).filter(SysUser.username == username).first():
            print(f"用户名「{username}」已存在", file=sys.stderr)
            sys.exit(1)

        user = SysUser(
            username=username,
            name=name,
            password_hash=hash_password(temp_password),
            role=args.role,
            is_active=True,
            must_change_password=True,
        )
        db.add(user)
        db.commit()
        print(f"已创建用户：{username}（{name}，{args.role}）")
        print(f"初始密码：{temp_password}")
        print("请私下发给本人，首次登录后需修改密码。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
