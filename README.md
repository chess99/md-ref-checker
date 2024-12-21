# Markdown Reference Checker

一个用于检查 Markdown 文件中引用完整性的命令行工具。

## 功能特点

- 检查文档引用 (`[[文件名]]` 或 `[[文件名|显示文本]]`)
- 检查图片引用 (`![[图片文件名]]`)
- 检查网络图片引用 (`![图片说明](https://图片地址)`)
- 检测单向引用（A引用了B，但B没有引用A）
- 生成引用统计信息
- 支持代码块中引用的智能识别（忽略代码示例中的引用）
- 支持自定义忽略规则

## 安装

```bash
pip install md-ref-checker
```

## 使用方法

```bash
md-ref-checker [--dir 目录路径] [-v 详细程度] [--no-color] [--ignore 忽略模式]
```

### 参数说明

- `--dir`: 要检查的目录路径，默认为当前目录
- `-v`: 输出详细程度（0-2），默认为0
  - 0: 只显示无效引用和未使用的图片
  - 1: 显示无效引用、未使用的图片和单向链接
  - 2: 显示所有引用统计信息
- `--no-color`: 禁用彩色输出
- `--ignore`: 添加要忽略的文件模式（可多次使用）

## 示例

```bash
# 检查当前目录
md-ref-checker

# 检查指定目录，���示详细信息
md-ref-checker --dir ./docs -v 2

# 忽略特定文件
md-ref-checker --ignore "*.draft.md" --ignore "temp/*"
```

## 开发说明

请查看 [DEVELOPMENT.md](docs/DEVELOPMENT.md) 了解开发相关信息。 