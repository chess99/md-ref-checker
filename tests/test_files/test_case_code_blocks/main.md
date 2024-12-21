# 测试文档

这是一个正常的引用 [[valid_doc]]。

这里有一个图片引用 ![[real_image.png]]。

这是另一个正常引用 [[real_doc]]。

## 代码块中的引用

### 围栏式代码块
```markdown
这是一个代码块中的引用 [[ignored_doc1]]
这是另一个代码块中的图片引用 ![[ignored_image1.png]]
```

### 行内代码
这是一个行内代码 `[[ignored_doc2]]` 和另一个 `![[ignored_image2.png]]`。

### 缩进式代码块
    这是一个缩进代码块
    [[ignored_doc3]]
    ![[ignored_image3.png]]

## 混合内容

这是一个正常引用 [[real_doc]]，后面跟着一个代码块：

```python
def test():
    # 这是代码块中的引用
    print("[[ignored_doc4]]")
    print("![[ignored_image4.png]]")
```

## 复杂代码块

### 嵌套代码块
````markdown
```python
print("[[ignored_doc5]]")
print("![[ignored_image5.png]]")
```
````

### 带别名的引用
这是一个带别名的正常引用 [[real_doc|带别名]]。

### 混合语法
这里混合了 `行内代码` 和 [[valid_doc|别名]] 以及 ![[real_image.png]]。

```javascript
// 代码���中的各种引用形式
const doc = "[[ignored_doc6]]";
const img = "![[ignored_image6.png]]";
const alias = "[[ignored_doc7|别名]]";
const mixed = `
    [[ignored_doc8]]
    ![[ignored_image7.png]]
    [[ignored_doc9|另一个别名]]
`;