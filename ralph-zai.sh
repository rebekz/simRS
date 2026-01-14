#!/bin/bash
# ralph-zai.sh
# Autonomous iteration loop for SIMRS development
# Usage: ./ralph-zai.sh <iterations>

# Don't exit on error - continue to next iteration
# set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <iterations>"
  exit 1
fi

# Log file for debugging
LOG_FILE="ralph-$(date +%Y%m%d-%H%M%S).log"
echo "Logging to $LOG_FILE"

# Initialize progress file if it doesn't exist
if [ ! -f "progress.txt" ]; then
  echo "# SIMRS Development Progress Log" > progress.txt
  echo "Started: $(date)" >> progress.txt
  echo "" >> progress.txt
fi

# For each iteration, run Claude Code with the following prompt.
for ((i=1; i<=$1; i++)); do
  echo "=== Iteration $i of $1 ===" | tee -a "$LOG_FILE"
  echo "Started: $(date)" | tee -a "$LOG_FILE"

  result=$(zai --dangerously-skip-permissions -p \
"@_bmad-output/prd.md \
@_bmad-output/architecture.md \
@_bmad-output/epics.md \
@_bmad-output/stories.md \
@_bmad-output/ux-design-system.md \
@_bmad-output/web-stories.md \
@docs/plans \
@progress.txt \

You are implementing SIMRS (Sistem Informasi Manajemen Rumah Sakit).

1. Read the PRD, architecture, epics, stories, and UX design to understand the full scope.
2. Check progress.txt to see what has been completed.
3. Decide which story to work on next based on:
   - Dependencies (earlier milestones before later ones)
   - Logical ordering within epics
   - YOUR assessment of highest priority
   - NOT necessarily the first uncompleted item
4. Implement the chosen story completely:
   - Write the necessary code
   - Run type checks and tests if applicable
   - Ensure acceptance criteria are met
5. Append your progress to progress.txt with:
   - Story ID completed (e.g., M1-E1-S1)
   - Brief summary of what was implemented
   - Any blockers or notes for next iteration
6. Make a git commit for the completed work.

ONLY WORK ON A SINGLE STORY PER ITERATION.

If all epics and stories are complete, output <promise>COMPLETE</promise>.
")

  echo "$result" | tee -a "$LOG_FILE"

  # Check for errors
  if [ -z "$result" ]; then
    echo "Warning: Empty result from claude, continuing..." | tee -a "$LOG_FILE"
    sleep 5
    continue
  fi

  if [[ "$result" == *"<promise>COMPLETE</promise>"* ]]; then
    echo "SIMRS development complete, exiting." | tee -a "$LOG_FILE"
    exit 0
  fi

  echo "=== Iteration $i complete at $(date) ===" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"

  # Brief pause between iterations
  sleep 2
done

echo "Completed $1 iterations." | tee -a "$LOG_FILE"

