# -*- coding: utf-8 -*-

"""
PostgreSQL 查询工具

提供一系列工具函数，可查询 PostgreSQL 元数据，包括表名、表结构、表注释、字段注释、数据样例等

主要功能:
- 查询数据库中所有表及其注释信息
- 查询指定表的所有字段定义和注释
- 查询指定表的所有字段的样例数据
- 查询指定表的指定字段的样例数据
- 查询指定表的指定字段的枚举值
"""

import psycopg2
import psycopg2.sql as pyc_sql


def get_table_info(conn):
    """
    获取 PostgreSQL 数据库中所有表及其表注释信息

    :param conn: 数据库连接对象
    :return: 当前数据库中的所有表及注释
    """
    with conn.cursor() as cursor:
        # 执行查询所有表及表注释的 SQL
        cursor.execute("""
            SELECT
                t.table_name,
                obj_description(pc.oid, 'pg_class') AS table_comment
            FROM
                information_schema.tables t
            JOIN
                pg_catalog.pg_class pc ON t.table_name = pc.relname
            JOIN
                pg_catalog.pg_namespace pn ON pn.oid = pc.relnamespace
            WHERE
                t.table_schema NOT IN ('pg_catalog', 'information_schema')
                AND t.table_type = 'BASE TABLE'
                AND pn.nspname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY
                t.table_name;
        """)

        # 获取并打印结果
        records = cursor.fetchall()

        table_info = [
            f"当前数据库中包含 {len(records)} 张数据表：\n"
        ]

        for idx, row in enumerate(records):
            table_name, comment = row
            table_info.append(f"数据表 #{idx}:")
            table_info.append(f"  - 名称: {table_name}")
            table_info.append(f"  - 注释: {comment if comment else '（无注释）'}")

    return "\n".join(table_info)


def get_table_columns_info(conn, table_name, schema='public'):
    """
    获取 PostgreSQL 数据库中指定表的所有字段及字段注释

    :param conn: 数据库连接对象
    :param table_name: 需要查询的表名
    :param schema: 表所在的模式，默认为 'public'
    :return: 表的所有字段信息
    """
    with conn.cursor() as cursor:
        # 执行查询表字段信息的 SQL
        cursor.execute("""
            SELECT
                a.attname AS column_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                d.description AS column_comment
            FROM
                pg_catalog.pg_attribute a
            LEFT JOIN
                pg_catalog.pg_description d ON (d.objoid = a.attrelid AND d.objsubid = a.attnum)
            JOIN
                pg_catalog.pg_class c ON a.attrelid = c.oid
            JOIN
                pg_catalog.pg_namespace n ON c.relnamespace = n.oid
            WHERE
                n.nspname = %s
                AND c.relname = %s
                AND a.attnum > 0
                AND NOT a.attisdropped
            ORDER BY
                a.attnum;
        """, (schema, table_name))

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
            column_name, data_type, comment = row
            result.append(f"字段 #{i+1}:")
            result.append(f"  - 名称: {column_name}")
            result.append(f"  - 类型: {data_type}")
            result.append(f"  - 注释: {comment if comment else '（无注释）'}")
            # result.append("-" * 60)

        return "\n".join(result)


def get_random_sample(conn, table_name, schema='public', columns=None):
    """
    获取 PostgreSQL 表中随机 10 条数据，并输出为 Markdown 表格

    Markdown格式的表格字符串
    :param conn: 数据库连接对象
    :param table_name: 需要查询的表名
    :param schema: 表所在的模式，默认为 'public'
    :param columns: 需要输出的字段名列表（None 表示所有字段）
    :return: Markdown 格式的表格字符串
    """

    with conn.cursor() as cursor:
        # 构建字段选择部分
        if columns:
            # 安全地构建字段标识符列表
            column_identifiers = pyc_sql.SQL(', ').join(pyc_sql.Identifier(col) for col in columns)
            select_clause = pyc_sql.SQL("SELECT {}").format(column_identifiers)
        else:
            select_clause = pyc_sql.SQL("SELECT *")

        # 安全地构建SQL查询
        query = pyc_sql.SQL("""
            {select_clause}
            FROM {schema}.{table}
            ORDER BY RANDOM()
            LIMIT 10
        """).format(
            select_clause=select_clause,
            schema=pyc_sql.Identifier(schema),
            table=pyc_sql.Identifier(table_name))

        cursor.execute(query)

        # 获取查询结果
        records = cursor.fetchall()

        # 如果没有数据
        if not records:
            return f"数据表 {table_name} 中没有数据"

        # 获取列名（使用实际查询的列名）
        column_names = [desc[0] for desc in cursor.description]

        # 构建Markdown表格
        markdown_table = "| " + " | ".join(column_names) + " |\n"
        markdown_table += "| " + " | ".join(["---"] * len(column_names)) + " |\n"

        # 添加数据行
        for row in records:
            formatted_row = []
            for value in row:
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
            columns = ", ".join(columns)
            prefix += f" {columns} 字段的示例数据如下：\n\n"
        else:
            prefix += "所有字段的示例数据如下：\n\n"

        return prefix + markdown_table


def get_top_enum_values(conn, table_name, column_name, schema='public', limit=10):
    """
    获取 PostgreSQL 表中指定字段出现频率最高的前 N 个枚举值及其计数

    :param conn: 数据库连接对象
    :param table_name: 需要查询的表名
    :param column_name: 需要统计的字段名
    :param schema: 表所在的模式，默认为 'public'
    :param limit: 返回的结果数量，默认为前10个
    :return: Markdown 格式的统计结果
    """
    with conn.cursor() as cursor:
        # 安全地构建SQL查询
        query = pyc_sql.SQL("""
            SELECT
                {column} AS value,
                COUNT(*) AS frequency
            FROM
                {schema}.{table}
            GROUP BY
                {column}
            ORDER BY
                frequency DESC,
                value ASC
            LIMIT %s;
        """).format(
            schema=pyc_sql.Identifier(schema),
            table=pyc_sql.Identifier(table_name),
            column=pyc_sql.Identifier(column_name)
        )

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
            value, frequency = row
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
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="ecommerce_orders",
        user="admin",
        password="admin-password"
    )
    return conn


def load_env():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    config = {
        "host": os.getenv('DB_HOST'),
        "port": os.getenv('DB_PORT'),
        "database": os.getenv('DB_NAME'),
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD')
    }

    return config


def create_conn_from_dotenv(config: dict):
    conn = psycopg2.connect(
        host=config["host"],
        port=config["port"],
        database=config["database"],
        user=config["user"],
        password=config["password"]
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
        print(get_table_columns_info(c, table_name='logistics'))
        print("*" * 80)

        # 打印样例数据
        print("【查询指定表的所有字段的样例数据】\n")
        print(get_random_sample(c, table_name='logistics'))
        print("*" * 80)

        # 打印指定字段的样例数据
        print("【查询指定表的指定字段的样例数据】\n")
        print(get_random_sample(c, "orders", columns=["order_id", "status"]))
        print("*" * 80)

        # 打印指定字段出现频率前十的枚举值
        print("【查询指定表的指定字段的枚举值】\n")
        print(get_top_enum_values(c, "orders", "status"))
        print("*" * 80)
    except psycopg2.Error as e:
        print(f"查询失败: {e.pgerror}")
    finally:
        close_conn(c)
