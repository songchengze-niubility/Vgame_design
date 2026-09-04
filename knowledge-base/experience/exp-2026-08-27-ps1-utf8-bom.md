---
id: EXP-20260827-01
date: 2026-08-27
title: Windows PowerShell 下含中文的 .ps1 必须保存为 UTF-8 with BOM
category: harness
tags: powershell, encoding, bom, gate-script
triggerTerms: check.ps1 报错; 表达式或语句中包含意外的标记; ps1 语法错误; 一键安装第5步失败; 检查驾驭工程失败; GBK 解析脚本
status: active
source: 驾驭工程完整性修复对话 2026-08-27
refs: scripts/check.ps1, 驾驭工程/一键安装.bat
---

## 现象

`powershell -File scripts/check.ps1` 报 `表达式或语句中包含意外的标记“}”`，行号指向某个 foreach 的收尾花括号，
但该处语法肉眼检查完全正确；同一文件用 pwsh(PowerShell 7) 运行正常。

## 根因

Windows PowerShell 5.1 对无 BOM 的 .ps1 按 ANSI(中文系统为 GBK) 解码。
含中文的字符串字面量（如白名单正则里的"源表"）在 UTF-8→GBK 错误解码下会吞掉后续字节，
导致括号配平被破坏，解析器在远离真实原因的位置报错。HEAD 提交里同样存在此问题，
说明是入库规范缺失而非本地改动引入。

## 处理

给文件补 3 字节 UTF-8 BOM：读全部字节后前置 `EF BB BF` 写回，内容零改动、换行符不受影响。

## 规则化建议

任何 .ps1 只要包含非 ASCII 字符就必须带 BOM 再提交；
新建门禁/启动脚本时用 `head -c 3 | od -An -tx1` 验证前三是 `ef bb bf`。
报错样式吻合("意外标记 + 行号处语法看起来没问题 + pwsh 正常")时直接怀疑编码。
