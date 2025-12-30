# 数据分析工具模块

## 1. 模块概述

### 1.1 模块职责

数据分析工具提供数据分析功能，用于分析任务执行产生的数据。

### 1.2 模块位置

- 文件路径：`app/tools/data_analyzer.py`
- 类名：`DataAnalyzer`

## 2. API文档

### 2.1 类/函数列表

- `DataAnalyzer`: 数据分析工具类
  - `analyze_data()`: 分析数据
  - `generate_summary()`: 生成数据摘要

### 2.2 详细API说明

#### DataAnalyzer

数据分析工具类。

**方法列表**:

- `analyze_data(data, metrics) -> Dict`: 分析数据
- `generate_summary(data, summary_type) -> str`: 生成摘要

**示例**:

```python
from app.tools.data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()
data = [{"value": 100}, {"value": 200}]
result = analyzer.analyze_data(data)
summary = analyzer.generate_summary(data)
```

## 3. 配置说明

无需额外配置。

## 4. 使用示例

```python
from app.tools.data_analyzer import DataAnalyzer

analyzer = DataAnalyzer()

# 分析数据
data = [
    {"date": "2024-01-01", "visitors": 1000},
    {"date": "2024-01-02", "visitors": 1200}
]
analysis = analyzer.analyze_data(data)

# 生成摘要
summary = analyzer.generate_summary(data, summary_type="detailed")
```

