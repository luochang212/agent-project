#!/bin/bash
# REFS:
# - GitHub: https://github.com/lobehub/lobe-chat
# - Doc: https://lobehub.com/zh/docs/self-hosting/platform/docker
# - Docker: https://hub.docker.com/r/lobehub/lobe-chat-pglite/tags
# - GitHub Issue: https://github.com/lobehub/lobe-chat/issues/7857#issuecomment-2885883417

# 1. 下载 lobe-chat-pglite
docker pull lobehub/lobe-chat-pglite:latest

# 2. 启动 lobe-chat-pglite
docker run -d -p 3210:3210 \
  -e ACCESS_CODE=lobe66 \
  --name lobe-chat \
  lobehub/lobe-chat-pglite:latest
