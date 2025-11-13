#!/usr/bin/env python3
"""最终测试PDF加载功能"""

import sys
import os

# 添加项目路径
sys.path.insert(0, 'src')

# 创建一个简单的PDF文件
pdf_path = 'doc/test_pdf.pdf'
os.makedirs('doc', exist_ok=True)

pdf_content = '''%PDF-1.1
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 33
>>
stream
BT /F1 12 Tf 100 700 Td (PDF Test Content) Tj ET
endstream
endobj
trailer
<<
/Root 1 0 R
/Size 5
>>
startxref
140
%%EOF
'''

with open(pdf_path, 'w') as f:
    f.write(pdf_content)

print('Created PDF:', pdf_path)

# 测试pdfminer导入
try:
    from pdfminer.high_level import extract_text
    print('✓ pdfminer.six imported successfully')
except ImportError as e:
    print('✗ Failed to import pdfminer:', str(e))
    sys.exit(1)

# 测试PDF提取
try:
    text = extract_text(pdf_path)
    print(f'✓ Extracted text: "{text.strip()}"')
except Exception as e:
    print(f'✗ Failed to extract text: {str(e)}')
    sys.exit(1)

# 测试rag_loader的load_documents
try:
    from chotbot.utils.rag_loader import load_documents
    docs = load_documents()
    print(f'✓ load_documents loaded {len(docs)} documents')
    
    # 检查是否有PDF内容
    has_pdf_content = False
    for doc in docs:
        if 'PDF Test Content' in doc:
            has_pdf_content = True
            break
    
    if has_pdf_content:
        print('✓ PDF content found in documents!')
    else:
        print('✗ PDF content not found in documents')
        print('  Loaded content:')
        for i, doc in enumerate(docs):
            print(f'  {i+1}: {doc[:50]}...')
            
except Exception as e:
    print(f'✗ Failed to load documents: {str(e)}')
    import traceback
    traceback.print_exc()

# 清理
os.remove(pdf_path)
print('\n✅ All tests completed!')
