import os
from src.check_references import ReferenceChecker

def test_image_reference_resolution(test_files_root):
    """测试图片引用解析"""
    test_dir = os.path.join(test_files_root, 'test_case_1')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
    # 测试正常的图片引用
    resolved = checker.resolve_link(
        "20241025-地址组件长期规划.png",
        "test.md",
        is_image=True
    )
    assert resolved == "assets/20241025-地址组件长期规划.png", \
        "应该正确解析图片引用"
    
    # 测试不存在的图片引用
    resolved = checker.resolve_link(
        "image_not_exist.png",
        "test.md",
        is_image=True
    )
    assert resolved == "image_not_exist.png", \
        "对不存在的图片引用应该返回原始路径"

def test_markdown_reference_resolution(test_files_root):
    """测试Markdown文档引用解析"""
    test_dir = os.path.join(test_files_root, 'test_case_1')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
    # 测试正常的文档引用
    resolved = checker.resolve_link(
        "existing_doc",
        "test.md",
        is_image=False
    )
    assert resolved == "existing_doc.md", \
        "应该正确解析文档引用"
    
    # 测试不存在的文档引用
    resolved = checker.resolve_link(
        "non_existing_doc",
        "test.md",
        is_image=False
    )
    assert resolved == "non_existing_doc", \
        "对不存在的文档引用应该返回原始路径"

def test_reference_checking(test_files_root):
    """测试引用检查功能"""
    test_dir = os.path.join(test_files_root, 'test_case_1')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    checker.check_all_references()
    
    # 验证无效引用
    invalid_links = [(link, source) for source, (link, _, _, _) in checker.invalid_links]
    assert ('image_not_exist.png', 'test.md') in invalid_links, \
        "应该检测到无效的图片引用"
    
    # 验证图片引用统计
    assert "assets/20241025-地址组件长期规划.png" in checker.referenced_images, \
        "应该正确统计图片引用"

def test_file_mapping(test_files_root):
    """测试文件映射功能"""
    test_dir = os.path.join(test_files_root, 'test_case_1')
    
    checker = ReferenceChecker(test_dir)
    checker.scan_files()
    
    # 测试图片文件映射
    assert "assets/20241025-地址组件长期规划.png" in checker.image_files, \
        "应该正确识别图片文件"
    
    # 测试文件名到实际文件的映射
    assert "20241025-地址组件长期规划.png" in checker.file_map, \
        "应该正确建立文件名映射"
    assert "assets/20241025-地址组件长期规划.png" in checker.file_map["20241025-地址组件长期规划.png"], \
        "应该正确映射图片文件路径" 