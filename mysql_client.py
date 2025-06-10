# -*- coding: utf-8 -*-

"""
MySQL 查询工具

提供一系列工具函数，可查询 MySQL 元数据，包括表名、表结构、表注释、字段注释、数据样例等

主要功能:
- 查询数据库中所有表及其注释信息
- 查询指定表的所有字段定义和注释
- 查询指定表的所有字段的样例数据
- 查询指定表的指定字段的样例数据
- 查询指定表的指定字段的枚举值

安装依赖：
  uv pip install pymysql python-dotenv
"""

import pymysql
import pymysql.cursors


def get_table_info(conn):
    """
    获取 MySQL 数据库中所有表及其表注释信息

    :param conn: 数据库连接对象
    :return: 当前数据库中的所有表及注释
    """
    with conn.cursor() as cursor:
        # 执行查询所有表及表注释的 SQL
        cursor.execute("""
            SELECT 
                TABLE_NAME as table_name,
                TABLE_COMMENT as table_comment
            FROM 
                information_schema.tables 
            WHERE 
                table_schema = DATABASE()
                AND table_type = 'BASE TABLE'
            ORDER BY 
                TABLE_NAME;
        """)

        # 获取并打印结果
        records = cursor.fetchall()

        table_info = [
            f"当前数据库中包含 {len(records)} 张数据表：\n"
        ]

        for idx, row in enumerate(records):
            table_name = row['table_name']
            comment = row['table_comment']
            table_info.append(f"数据表 #{idx}:")
            table_info.append(f"  - 名称: {table_name}")
            table_info.append(f"  - 注释: {comment if comment else '（无注释）'}")

    return "\n".join(table_info)


def get_table_columns_info(conn, table_name):
    """
    获取 MySQL 数据库中指定表的所有字段及字段注释

    :param conn: 数据库连接对象
    :param table_name: 需要查询的表名
    :return: 表的所有字段信息
    """
    with conn.cursor() as cursor:
        # 执行查询表字段信息的 SQL
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                COLUMN_TYPE,
                COLUMN_COMMENT
            FROM 
                information_schema.COLUMNS 
            WHERE 
                TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = %s
            ORDER BY 
                ORDINAL_POSITION;
        """, (table_name,))

        # 获取查询结果
        records = cursor.fetchall()

        # 如果没有找到表
        if not records:
            return f"数据表 {table_name} 不存在或没有用户字段"

        # 构建结果字符串
        result = [
            f"数据表 {table_name} 的字段信息如下：\n"
        ]

        for i, row in enumerate(records):
            column_name = row['COLUMN_NAME']
            data_type = row['COLUMN_TYPE']
            comment = row['COLUMN_COMMENT']
            result.append(f"字段 #{i+1}:")
            result.append(f"  - 名称: {column_name}")
            result.append(f"  - 类型: {data_type}")
            result.append(f"  - 注释: {comment if comment else '（无注释）'}")

        return "\n".join(result)


def get_random_sample(conn, table_name, columns=None):
    """
    获取 MySQL 表中随机 10 条数据，并输出为 Markdown 表格

    :param conn: 数据库连接对象
    :param table_name: 需要查询的表名
    :param columns: 需要输出的字段名列表（None 表示所有字段）
    :return: Markdown 格式的表格字符串
    """

    with conn.cursor() as cursor:
        # 构建字段选择部分
        if columns:
            # 使用反引号包围字段名以防止关键字冲突
            column_list = ", ".join(f"`{col}`" for col in columns)
            select_clause = f"SELECT {column_list}"
        else:
            select_clause = "SELECT *"

        # 构建 SQL 查询
        query = f"""
            {select_clause}
            FROM `{table_name}`
            ORDER BY RAND()
            LIMIT 10
        """

        cursor.execute(query)

        # 获取查询结果
        records = cursor.fetchall()

        # 如果没有数据
        if not records:
            return f"数据表 {table_name} 中没有数据"

        # 获取列名
        if records:
            column_names = list(records[0].keys())
        else:
            return f"数据表 {table_name} 中没有数据"

        # 构建Markdown表格
        markdown_table = "| " + " | ".join(column_names) + " |\n"
        markdown_table += "| " + " | ".join(["---"] * len(column_names)) + " |\n"

        # 添加数据行
        for row in records:
            formatted_row = []
            for col in column_names:
                value = row[col]
                if value is None:
                    formatted_row.append("NULL")
                elif isinstance(value, str):
                    # 简化处理：移除换行符，截断长文本
                    clean_value = value.replace('\n', ' ').replace('\r', '')
                    if len(clean_value) > 50:
                        clean_value = clean_value[:47] + "..."
                    formatted_row.append(clean_value)
                else:
                    formatted_row.append(str(value))

            markdown_table += "| " + " | ".join(formatted_row) + " |\n"

        # 构建结果字符串
        prefix = f"数据表 {table_name} 中包含"
        if columns:
            columns_str = ", ".join(columns)
            prefix += f" {columns_str} 字段的示例数据如下：\n\n"
        else:
            prefix += "所有字段的示例数据如下：\n\n"

        return prefix + markdown_table


def get_top_enum_values(conn, table_name, column_name, limit=10):
    """
    获取 MySQL 表中指定字段出现频率最高的前 N 个枚举值及其计数

    :param conn: 数据库连接对象
    :param table_name: 需要查询的表名
    :param column_name: 需要统计的字段名
    :param limit: 返回的结果数量，默认为前10个
    :return: Markdown 格式的统计结果
    """
    with conn.cursor() as cursor:
        # 构建 SQL 查询
        query = f"""
            SELECT 
                `{column_name}` AS value,
                COUNT(*) AS frequency
            FROM 
                `{table_name}`
            GROUP BY 
                `{column_name}`
            ORDER BY 
                frequency DESC,
                value ASC
            LIMIT %s;
        """

        cursor.execute(query, (limit,))

        # 获取查询结果
        records = cursor.fetchall()

        # 如果没有数据
        if not records:
            return f"数据表 {table_name} 中没有找到字段 {column_name} 的数据"

        # 构建结果字符串
        prefix = f"数据表 {table_name} 中 {column_name} 字段的"
        if len(records) <= limit:
            prefix += "枚举值如下："
        else:
            prefix += f" TOP {limit} 枚举值如下："

        result = [
            prefix,
            "",
            "| 枚举值 | 出现次数 |",
            "| --- | --- |"
        ]

        for row in records:
            value = row['value']
            frequency = row['frequency']
            if value is None:
                display_value = "NULL"
            else:
                display_value = str(value)

            result.append(
                f"| {display_value} | {frequency} |"
            )

        return "\n".join(result)


def create_conn():
    """不要在实际项目中写明文账密"""
    conn = pymysql.connect(
        host="localhost",
        port=3306,
        database="score",
        user="admin",
        password="admin-password",
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn


def load_env():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    config = {
        "host": os.getenv('DB_HOST'),
        "port": int(os.getenv('DB_PORT', 3306)),
        "database": os.getenv('DB_NAME'),
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD')
    }

    return config


def create_conn_from_dotenv(config: dict):
    conn = pymysql.connect(
        host=config["host"],
        port=config["port"],
        database=config["database"],
        user=config["user"],
        password=config["password"],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    return conn


def close_conn(conn, verbose=False):
    if conn:
        conn.close()
        if verbose:
            print('The `conn` has been closed.')


if __name__ == '__main__':
    c = create_conn()

    try:
        # 打印表及表注释
        print("【查询数据库中所有表及其注释信息】\n")
        print(get_table_info(c))
        print("*" * 80)

        # 打印字段信息
        print("【查询指定表的所有字段定义和注释】\n")
        print(get_table_columns_info(c, table_name='students'))
        print("*" * 80)

        # 打印样例数据
        print("【查询指定表的所有字段的样例数据】\n")
        print(get_random_sample(c, table_name='students'))
        print("*" * 80)

        # 打印指定字段的样例数据
        print("【查询指定表的指定字段的样例数据】\n")
        print(get_random_sample(c, "students", columns=["name", "gpa"]))
        print("*" * 80)

        # 打印指定字段出现频率前十的枚举值
        print("【查询指定表的指定字段的枚举值】\n")
        print(get_top_enum_values(c, "students", "class"))
        print("*" * 80)
    except pymysql.Error as e:
        print(f"查询失败: {e}")
    finally:
        close_conn(c)
