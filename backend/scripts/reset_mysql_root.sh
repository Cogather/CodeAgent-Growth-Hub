#!/bin/bash
# 重置本机 MySQL 8 root 密码（Oracle 官方 macOS 安装包）
# 用法: bash scripts/reset_mysql_root.sh [新密码，默认 root]
# 需要 macOS 管理员权限，会弹出系统密码框
set -euo pipefail

MYSQL_BASE="/usr/local/mysql"
NEW_PASSWORD="${1:-root}"
INIT_SQL="/tmp/mysql-init-reset.sql"
LOG="/tmp/mysqld-init-reset.log"

echo "ALTER USER 'root'@'localhost' IDENTIFIED BY '${NEW_PASSWORD}';" > "$INIT_SQL"
chmod 600 "$INIT_SQL"
chown _mysql "$INIT_SQL"

echo ">>> 停止 MySQL..."
launchctl stop com.oracle.oss.mysql.mysqld 2>/dev/null || true
pkill -9 mysqld 2>/dev/null || true
sleep 2

echo ">>> 以 init-file 模式启动（用户 _mysql）..."
su - _mysql -s /bin/sh -c "
  ${MYSQL_BASE}/bin/mysqld \
    --user=_mysql \
    --basedir=${MYSQL_BASE} \
    --datadir=${MYSQL_BASE}/data \
    --init-file=${INIT_SQL} \
    --log-error=${LOG} \
    --pid-file=${MYSQL_BASE}/data/mysqld-reset.pid
" &
MYSQL_PID=$!

for i in $(seq 1 60); do
  if ${MYSQL_BASE}/bin/mysqladmin ping -u root --silent 2>/dev/null; then
    echo ">>> MySQL 已就绪"
    break
  fi
  sleep 1
  if ! kill -0 "$MYSQL_PID" 2>/dev/null; then
    echo ">>> mysqld 启动失败，日志:"
    tail -20 "$LOG" 2>/dev/null || true
    exit 1
  fi
done

sleep 2
echo ">>> 停止临时实例..."
kill "$MYSQL_PID" 2>/dev/null || pkill mysqld || true
sleep 3
rm -f "$INIT_SQL"

echo ">>> 正常启动 MySQL 服务..."
launchctl start com.oracle.oss.mysql.mysqld
sleep 4

echo ">>> 验证..."
${MYSQL_BASE}/bin/mysql -u root -p"${NEW_PASSWORD}" -e "SELECT 'password reset OK' AS status;"
echo ">>> 完成，新密码: ${NEW_PASSWORD}"
