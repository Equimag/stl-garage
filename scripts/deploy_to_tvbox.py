#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sync updated config and news poster to X96 TV Box (/opt/stl-news-poster)
"""
import paramiko
from pathlib import Path

TVBOX_IP = "192.168.1.83"
TVBOX_USER = "root"
TVBOX_PASS = "1234"

print(f"Connecting to TV Box {TVBOX_IP}...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(TVBOX_IP, port=22, username=TVBOX_USER, password=TVBOX_PASS, timeout=6)

sftp = ssh.open_sftp()

# 1. Update config.py
local_cfg_path = Path("scripts/config.py")
if local_cfg_path.exists():
    with open(local_cfg_path, "r", encoding="utf-8") as f:
        cfg_content = f.read()
    with sftp.open("/opt/stl-news-poster/config.py", "w") as f:
        f.write(cfg_content)
    print("✔ Uploaded /opt/stl-news-poster/config.py")

# 2. Update channel_publisher.py
local_pub_path = Path("scripts/channel_publisher.py")
if local_pub_path.exists():
    with open(local_pub_path, "r", encoding="utf-8") as f:
        pub_content = f.read()
    with sftp.open("/opt/stl-news-poster/channel_publisher.py", "w") as f:
        f.write(pub_content)
    print("✔ Uploaded /opt/stl-news-poster/channel_publisher.py")

# 3. Update auto_news_poster.py
local_poster_path = Path("scripts/auto_news_poster.py")
if local_poster_path.exists():
    # Make sure auto_news_poster.py uses MASTER_USERNAME in buttons
    with open(local_poster_path, "r", encoding="utf-8") as f:
        poster_content = f.read()
    with sftp.open("/opt/stl-news-poster/auto_news_poster.py", "w") as f:
        f.write(poster_content)
    print("✔ Uploaded /opt/stl-news-poster/auto_news_poster.py")

sftp.close()

# Verify on TV Box
stdin, stdout, stderr = ssh.exec_command("grep SITE_URL /opt/stl-news-poster/config.py")
print("Verified config on TV Box:", stdout.read().decode().strip())

ssh.close()
print("Done!")
