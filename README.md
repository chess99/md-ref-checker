# Markdown Reference Checker

一个用于检查 Markdown 文件中引用完整性的工具。它可以：

- 检查图片引用是否有效
- 检查文件链接是否有效
- 检查未使用的图片文件
- 生成引用统计信息

## 安装

```bash
pip install .
```

## 使用方法

基本用法：

```bash
md-ref-checker [目录路径]
```

如果不指定目录路径，将检查当前目录。

### 命令行选项

- `--ignore`, `-i`: 指定要忽略的文件或目录的 glob 模式（可多次指定）
  ```bash
  md-ref-checker --ignore "node_modules/**" --ignore "*.tmp"
  ```

- `--no-unused`: 不检查未使用的图片文件
  ```bash
  md-ref-checker --no-unused
  ```

- `--json`: 以 JSON 格式输出结果
  ```bash
  md-ref-checker --json
  ```

### 示例输出

```
损坏的引用：

docs/guide.md:
  - images/missing.png
  - api/nonexistent.md

未使用的图片：
  - assets/unused.png
  - images/old.jpg

统计信息：
  Markdown 文件总数：15
  图片文件总数：8
  损坏的引用总数：2
  包含损坏引用的文件数：1
  未使用的图片数：2
```

## 开发

### 环境设置

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/md-ref-checker.git
   cd md-ref-checker
   ```

2. 创建虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. 安装开发依赖：
   ```bash
   pip install -e ".[dev]"
   ```

### 运行测试

```bash
pytest
```

## 许可证

MIT License 