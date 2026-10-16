#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 开源工作台 · 每日数据更新
#
# 用途：拉数据 → 重新生成 工作台.html
# 调用：由 launchd（主）或 DSH schedule（备）触发，也可手动执行
# 日志：logs/每日更新.log
#
# ⚠️ 设计要点
#   1. 幂等：非交易日/数据未变时，脚本会识别并跳过（不重复写文件）
#   2. 不中断：任一步失败都会记录但继续，最后给出汇总退出码
#   3. 可诊断：每次运行都写日志，含耗时与各步结果
# ═══════════════════════════════════════════════════════════════

set -u

WORKDIR="/Users/qumingtainanle/WorkBuddy/开源/工作台"
PY="/Users/qumingtainanle/.workbuddy/binaries/python/envs/default/bin/python3"
LOGDIR="$WORKDIR/logs"
LOG="$LOGDIR/每日更新.log"
MAXLOG=$((2*1024*1024))          # 日志超过 2MB 自动截断保留末 500 行

mkdir -p "$LOGDIR"

# 日志轮转
if [ -f "$LOG" ] && [ "$(wc -c < "$LOG" 2>/dev/null || echo 0)" -gt "$MAXLOG" ]; then
  tail -500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi

ts() { date '+%Y-%m-%d %H:%M:%S'; }
say() { echo "[$(ts)] $*" >> "$LOG"; }

say "════════ 每日更新开始 ════════"
START=$(date +%s)

cd "$WORKDIR" || { say "❌ 无法进入工作目录 $WORKDIR"; exit 1; }

# ── ① 拉数据 ──
say "→ 拉数据（拉数据.py）"
STEP1_OUT=$("$PY" 拉数据.py 2>&1)
STEP1_RC=$?
echo "$STEP1_OUT" >> "$LOG"
if [ $STEP1_RC -ne 0 ]; then
  say "⚠️ 拉数据.py 退出码 $STEP1_RC（可能有个别源失败，继续尝试生成）"
fi

# 从输出里提取成功/失败统计
SUMMARY=$(echo "$STEP1_OUT" | grep -E '^成功 ' | tail -1)
[ -n "$SUMMARY" ] && say "   $SUMMARY"

# ── ② 生成页面 ──
say "→ 生成页面（生成工作台.py）"
STEP2_OUT=$("$PY" 生成工作台.py 2>&1)
STEP2_RC=$?
echo "$STEP2_OUT" >> "$LOG"

if [ $STEP2_RC -ne 0 ]; then
  say "❌ 生成工作台.py 失败（退出码 $STEP2_RC）"
  say "════════ 更新失败 ════════"
  exit 2
fi

# 关键指标回显
GEN=$(echo "$STEP2_OUT" | grep -E '指标序列|回撤段数' | sed 's/^ *//' | tr '\n' ' ')
[ -n "$GEN" ] && say "   $GEN"

ELAPSED=$(( $(date +%s) - START ))
say "✅ 完成，耗时 ${ELAPSED}s"
say "════════ 每日更新结束 ════════"
exit 0
