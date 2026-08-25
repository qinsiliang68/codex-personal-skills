# Personal Codex Skills

这是 `qinsiliang68` 维护的个人 Codex Skill 仓库，用于公开、版本化和复用自定义工作流。

This is a public, versioned collection of personal Codex skills maintained by `qinsiliang68`.

## Scope

仓库只收录个人编写的 Skill。它明确不包含：

- Codex 自带的 `.system` Skill；
- 插件提供的 Skill；
- 插件缓存、运行时缓存、memory、会话记录或日志；
- API key、访问令牌、密码或其他凭据；
- 用户私有绝对路径。

本仓库不是 OpenAI 官方 Skill 仓库，也不代表 OpenAI 的产品承诺或支持范围。

## Included skills

| Skill | Purpose |
| --- | --- |
| `data-topic-plotting` | 将实验数据整理成易读表格、图表和 HTML 报告，强调可见差异与轴尺度诚实性。 |
| `jgsjdq-migration-workflow` | 以强 JSON 合同、计算/展示一致性和 Word/Open XML 验收迁移工程计算书项目。 |
| `parser-output-manual-annotation` | 对 OCR/PDF parser 的 Markdown 输出执行人工标注、保真检查和训练数据准备。 |
| `repo-development-protocol` | 对代码、配置、schema、管线和文档修改执行 DAA、TDD、验证和小回滚单元。 |
| `repo-file-management` | 管理仓库文件身份、生命周期、目录边界、清单、生成物和发布资产。 |
| `windows-powershell-efficiency` | 在原生 Windows PowerShell 中执行有界查询、精确路径操作、失败归因和渐进式验证。 |

每个 Skill 位于 `skills/<skill-name>/`，入口文件固定为 `SKILL.md`。若存在 `agents/openai.yaml`，它只定义该 Skill 的展示元数据和默认提示词。

## Install one skill on Windows

先克隆仓库，再复制所需 Skill：

```powershell
git clone https://github.com/qinsiliang68/codex-personal-skills.git
$skillName = 'repo-development-protocol'
$source = Join-Path (Resolve-Path '.\codex-personal-skills\skills').Path $skillName
$destinationRoot = Join-Path $env:USERPROFILE '.codex\skills'
Copy-Item -LiteralPath $source -Destination $destinationRoot -Recurse
```

若目标 Skill 已存在，请先人工比较差异；不要用递归覆盖命令静默替换本地定制内容。安装后，在新的 Codex 任务中确认 Skill 已出现在可用列表。

## Integrity and validation

`manifest.json` 登记每个公开 Skill 的文件路径、字节数和 SHA-256。修改 Skill 后重新生成清单并运行验证：

```powershell
uv run python scripts/build_manifest.py
uv run python -m unittest tests.validate_repository -v
uv run python scripts/build_manifest.py --check
git diff --check
```

验证会 fail closed：Skill 数量或身份不符、清单漂移、出现官方/运行时目录、用户私有绝对路径、symlink 或常见凭据模式都会失败。

## Repository policy

新增或修改 Skill 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [AGENTS.md](AGENTS.md)。公开发布前必须人工复核内容；自动扫描只能作为补充，不能证明不存在所有隐私或安全问题。

## License

MIT，见 [LICENSE](LICENSE)。
