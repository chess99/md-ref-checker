# Markdown Reference Checker

一个用于检查 Markdown 文件中引用完整性的工具，特别适用于 Obsidian 风格的 wiki 链接。

## 特性

- 检查文件引用 (`[[file]]` 或 `[[file|alias]]`)
- 检查标题引用 (`[[file#heading]]`)
- 检查图片引用 (`![[image]]` 和 `![alt](image)`)
- 检测未使用的图片
- 检测单向链接（A引用B但B没有引用A）
- 支持 `.gitignore` 和自定义忽略规则
- 详细的错误报告（包含行号和列号）
- 生成引用统计信息

## 安装

### 使用 pip 安装

```bash
pip install md-ref-checker
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/md-ref-checker.git
cd md-ref-checker

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

## 使用方法

### 命令行工具

```bash
# 检查当前目录
md-ref-checker

# 检查指定目录
md-ref-checker -d /path/to/docs

# 显示详细信息
md-ref-checker -v 2

# 忽略特定文件
md-ref-checker -i "*.tmp" -i "draft/*"

# 删除未使用的图片
md-ref-checker -r

# 显示调试信息
md-ref-checker -D
```

### 命令行选项

- `-d, --dir`: 要检查的目录路径（默认为当前目录）
- `-v, --verbosity`: 输出详细程度（0-2）
  - 0: 只显示无效引用和未使用的图片
  - 1: 显示无效引用、未使用的图片和单向链接
  - 2: 显示所有引用统计信息
- `-n, --no-color`: 禁用彩色输出
- `-i, --ignore`: 添加要忽略的文件模式（可多次使用）
- `-r, --delete-unused-images`: 删除未被引用的图片文件
- `-D, --debug`: 显示调试信息

### Python API

```python
from md_ref_checker import ReferenceChecker

# 创建检查器
checker = ReferenceChecker("docs")

# 添加忽略规则
checker.fs.ignore_patterns.extend(["*.tmp", "draft/*"])

# 检查整个目录
result = checker.check_directory()

# 检查单个文件
result = checker.check_file("docs/note.md")

# 处理结果
if result.invalid_refs:
    print("发现无效引用:")
    for ref in result.invalid_refs:
        print(f"{ref.source_file}:{ref.line_number} - {ref.target}")

if result.unused_images:
    print("未使用的图片:")
    for image in result.unused_images:
        print(image)

if result.unidirectional_links:
    print("单向链接:")
    for source, target in result.unidirectional_links:
        print(f"{source} -> {target}")
```

## 开发

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_models.py

# 显示测试覆盖率
pytest --cov=md_ref_checker
```

### 代码风格

项目使用以下工具保证代码质量：

- Black: 代码格式化
- Ruff: 代码检查
- MyPy: 类型检查

```bash
# 格式化代码
black src tests

# 运行代码检查
ruff check src tests

# 运行类型检查
mypy src tests
```

## 贡献

欢迎贡献！请参考以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。 