# 开发文档

## 项目背景

这个项目源于对 Markdown 文档引用完整性的需求。在使用 Markdown 编写大量互相关联的文档时，经常会遇到以下问题：

1. 引用的文件被移动或重命名后，原引用失效
2. 文档之间的引用关系不清晰
3. 图片资源未被使用但仍占用存储空间
4. 代码示例中的引用可能被误识别

为了解决这些问题，我们开发了这个引用检查工具。

## 代码结构

```
md-ref-checker/
├── src/
│   ├── __init__.py
│   ├── checker.py      # 核心检查逻辑
│   ├── cli.py         # 命令行接口
│   └── utils.py       # 工具函数
├── tests/
│   ├── __init__.py
│   ├── test_checker.py
│   ├── test_cli.py
│   └── test_files/    # 测试用例文件
├── docs/
│   ├── DEVELOPMENT.md
│   └── API.md
└── README.md
```

## 核心功能实现

### 引用检查器 (checker.py)

引用检查器的主要功能：

1. 文件扫描：递归扫描指定目录下的所有 Markdown 文件
2. 引用提取：
   - 使用正���表达式识别文档引用和图片引用
   - 智能识别并忽略代码块中的引用
3. 引用验证：
   - 检查引用文件是否存在
   - 检查图片文件是否存在
   - 分析单向引用关系
4. 结果统计：生成详细的引用统计信息

### 代码块识别

代码块识别是一个重要特性，支持以下类型：

1. 围栏式代码块 (```code```)
2. 行内代码块 (`code`)
3. 缩进式代码块（4个空格或1个制表符）
4. 嵌套代码块

### 测试用例

测试覆盖了以下场景：

1. 正常引用检测
2. 代码块中引用的忽略
3. 特殊字符处理
4. 单向引用检测
5. 忽略规则处理

## 开发指南

### 环境设置

1. 克隆仓库
```bash
git clone https://github.com/yourusername/md-ref-checker.git
cd md-ref-checker
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

### 运行测试

```bash
python -m pytest tests/
```

### 代码风格

- 遵循 PEP 8 规范
- 使用 type hints 进行类型注解
- 编写详细的文档字符串
- 保持代码简洁清晰

### 提交规范

- 使用清晰的提交信息
- 每个功能或修复使用单独的分支
- 提交前运行测试确��通过
- 更新相关文档

## 待办事项

- [ ] 支持更多的引用格式
- [ ] 添加引用关系可视化
- [ ] 优化性能
- [ ] 支持更多的忽略规则
- [ ] 添加自动修复功能 