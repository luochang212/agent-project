# 简单的 RAG

文件结构如下：

```
.
├── README.md
├── chroma_langchain_db
│   ├── 193db982-8590-484b-88b5-129e919d338f
│   │   ├── data_level0.bin
│   │   ├── header.bin
│   │   ├── length.bin
│   │   └── link_lists.bin
│   └── chroma.sqlite3
├── simple_rag.ipynb
└── simple_rag.py
```

其中，

- `chroma_langchain_db`: chroma 的存储目录
- `simple_rag.ipynb`: 开发简单的 RAG（包括 llm server, embedding server 的启动脚本）
- `simple_rag.py`: 完整的 RAG 代码
