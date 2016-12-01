#! /usr/bin/env python
#coding=utf-8

##
# @file:   xls_deploy_tool.py
# @author: jameyli <lgy AT live DOT com>
# @brief:  xls ���õ�����

# ��Ҫ���ܣ�
#     1 ���ö������ɣ�����excel �Զ��������õ�PB����
#     2 �������ݵ��룬��������������PB�����л���Ķ��������ݻ����ı�����
#
# ˵��:
#   1 excel ��ǰ�������ڽṹ����, ������Ϊ���ݣ�����һ������, �ֱ���ͣ�
#       required �������� (V3ȥ��)
#       optional ��ѡ���� ��Ĭ�ϣ�
#           �ڶ���: ��������
#           �����У�������
#           �����У�ע��
#           �����У�����ֵ
#       repeated ������һ��������repeated,������
#           �ڶ���: repeat��������, excel�л��ظ��г�������
#           2011-11-29 �����޸� �ڶ�����������Ͷ���Ļ��������������repeated
#           ����Ŀǰֻ֧������
#           �����У�����
#           �����У�ע��
#           �����У�ʵ�ʵ��ظ�����
#       required_struct ��ѡ�ṹ����
#       optional_struct ��ѡ�ṹ����
#           �ڶ��У��ṹԪ�ظ���
#           �����У��ṹ��
#           �����У����ϲ�ṹ�е�������
#           �����У�������

#    1  | required/optional | repeated  | required_struct/optional_struct   |
#       | ------------------| ---------:| ---------------------------------:|
#    2  | ��������          |           | �ṹԪ�ظ���                      |
#    3  | ������            |           | �ṹ������                        |
#    4  | ע��˵��          |           | ���ϲ�ṹ�е�������              |
#    5  | ����ֵ            |           |                                   |

#
#
# ��ʼ��Ƶĺ����룬ϣ�����ö�����������ݱ���һ��,ʹ��ͬһ��excel
# ��֪���ܷ�ʵ��
#
# ���ܻ���ʵ�֣�����֤������ͨ��CPP���� ohye
#
# 2011-06-17 �޸�:
#   ����sheet_name ʹ�ô�д
#   �ṹ����ʹ�ô�д���»���
# 2011-06-20 �޸�bug:
#   excel�����д��ڿո�
#   repeated_num = 0 ʱ�����
# 2011-11-24 ��ӹ���
#   Ĭ��ֵ
# 2011-11-29 ��ӹ���
# repeated �ڶ�����������Ͷ���Ļ��������������repeated
# ����Ŀǰֻ֧������

# TODO::
# 1 ʱ���������Ի�
# 2 ����server/client ����
# 3 repeated �Ż�
# 4 struct �Ż�

# ����:
# 1 protobuf
# 2 xlrd
##


import xlrd # for read excel
import sys
import os

# TAP�Ŀո���
TAP_BLANK_NUM = 4

FIELD_RULE_ROW = 0
# ��һ�л���ʾ�ظ�������������ṹ��Ԫ����
FIELD_TYPE_ROW = 1
FIELD_NAME_ROW = 2
FIELD_COMMENT_ROW = 3

class LogHelp :
    """��־������"""
    _logger = None
    _close_imme = True

    @staticmethod
    def set_close_flag(flag):
        LogHelp._close_imme = flag

    @staticmethod
    def _initlog():
        import logging

        LogHelp._logger = logging.getLogger()
        logfile = 'convert.log'
        hdlr = logging.FileHandler(logfile)
        formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(lineno)d|%(funcName)s|%(message)s')
        hdlr.setFormatter(formatter)
        LogHelp._logger.addHandler(hdlr)
        LogHelp._logger.setLevel(logging.NOTSET)
        # LogHelp._logger.setLevel(logging.WARNING)

        LogHelp._logger.info("\n\n\n")
        LogHelp._logger.info("logger is inited!")

    @staticmethod
    def get_logger() :
        if LogHelp._logger is None :
            LogHelp._initlog()

        return LogHelp._logger

    @staticmethod
    def close() :
        if LogHelp._close_imme:
            import logging
            if LogHelp._logger is None :
                return
            logging.shutdown()

# log macro
LOG_DEBUG=LogHelp.get_logger().debug
LOG_INFO=LogHelp.get_logger().info
LOG_WARN=LogHelp.get_logger().warn
LOG_ERROR=LogHelp.get_logger().error


class SheetInterpreter:
    """ͨ��excel�����������õ�protobuf�����ļ�"""
    def __init__(self, xls_file_path, sheet_name):
        self._xls_file_path = xls_file_path
        self._sheet_name = sheet_name

        try :
            self._workbook = xlrd.open_workbook(self._xls_file_path)
        except BaseException, e :
            print "open xls file(%s) failed!"%(self._xls_file_path)
            raise

        try :
            self._sheet =self._workbook.sheet_by_name(self._sheet_name)
        except BaseException, e :
            print "open sheet(%s) failed!"%(self._sheet_name)

        # ����������
        self._row_count = len(self._sheet.col_values(0))
        self._col_count = len(self._sheet.row_values(0))

        self._row = 0
        self._col = 0

        # �����е������д��һ��list�� ���ͳһд���ļ�
        self._output = []
        # �Ű������ո���
        self._indentation = 0
        # field number �ṹǶ��ʱʹ���б�
        # ����һ���ṹ������һ��Ԫ�أ��ṹ������ɺ󵯳�
        self._field_index_list = [1]
        # ��ǰ���Ƿ������������ͬ�ṹ�ظ�����
        self._is_layout = True
        # �������нṹ������
        self._struct_name_list = []

        self._pb_file_name = sheet_name.lower() + ".proto"


    def Interpreter(self) :
        """����Ľӿ�"""
        LOG_INFO("begin Interpreter, row_count = %d, col_count = %d", self._row_count, self._col_count)

        self._LayoutFileHeader()

        self._output.append("syntax=\"proto2\";\n\n")
        self._output.append("package tnt_deploy;\n")

        self._LayoutStructHead(self._sheet_name)
        self._IncreaseIndentation()

        while self._col < self._col_count :
            self._FieldDefine(0)

        self._DecreaseIndentation()
        self._LayoutStructTail()

        self._LayoutArray()

        self._Write2File()

        LogHelp.close()
        # ��PBת����py��ʽ
        try :
            command = "protoc --python_out=./ " + self._pb_file_name
            os.system(command)
        except BaseException, e :
            print "protoc failed!"
            raise

    def _FieldDefine(self, repeated_num) :
        LOG_INFO("row=%d, col=%d, repeated_num=%d", self._row, self._col, repeated_num)
        field_rule = str(self._sheet.cell_value(FIELD_RULE_ROW, self._col))

        if field_rule == "required" or field_rule == "optional" :
            field_type = str(self._sheet.cell_value(FIELD_TYPE_ROW, self._col)).strip()
            field_name = str(self._sheet.cell_value(FIELD_NAME_ROW, self._col)).strip()
            field_comment = unicode(self._sheet.cell_value(FIELD_COMMENT_ROW, self._col))

            LOG_INFO("%s|%s|%s|%s", field_rule, field_type, field_name, field_comment)

            comment = field_comment.encode("utf-8")
            self._LayoutComment(comment)

            if repeated_num >= 1:
                field_rule = "repeated"

            self._LayoutOneField(field_rule, field_type, field_name)

            actual_repeated_num = 1 if (repeated_num == 0) else repeated_num
            self._col += actual_repeated_num

        elif field_rule == "repeated" :
            # 2011-11-29 �޸�
            # ��repeated�ڶ��������Ͷ��壬���ʾ��ǰ�ֶ���repeated�����������ڵ����÷ֺ����
            second_row = str(self._sheet.cell_value(FIELD_TYPE_ROW, self._col)).strip()
            LOG_DEBUG("repeated|%s", second_row);
            # exel�п�����С����
            if second_row.isdigit() or second_row.find(".") != -1 :
                # �������һ�����һ���ṹ��
                repeated_num = int(float(second_row))
                LOG_INFO("%s|%d", field_rule, repeated_num)
                self._col += 1
                self._FieldDefine(repeated_num)
            else :
                # һ���Ǽ򵥵ĵ��ֶΣ���ֵ�÷ֺ����
                field_type = second_row
                field_name = str(self._sheet.cell_value(FIELD_NAME_ROW, self._col)).strip()
                field_comment = unicode(self._sheet.cell_value(FIELD_COMMENT_ROW, self._col))
                LOG_INFO("%s|%s|%s|%s", field_rule, field_type, field_name, field_comment)

                comment = field_comment.encode("utf-8")
                self._LayoutComment(comment)

                self._LayoutOneField(field_rule, field_type, field_name)

                self._col += 1

        elif field_rule == "required_struct" or field_rule == "optional_struct":
            field_num = int(self._sheet.cell_value(FIELD_TYPE_ROW, self._col))
            struct_name = str(self._sheet.cell_value(FIELD_NAME_ROW, self._col)).strip()
            field_name = str(self._sheet.cell_value(FIELD_COMMENT_ROW, self._col)).strip()

            LOG_INFO("%s|%d|%s|%s", field_rule, field_num, struct_name, field_name)


            if (self._IsStructDefined(struct_name)) :
                self._is_layout = False
            else :
                self._struct_name_list.append(struct_name)
                self._is_layout = True

            col_begin = self._col
            self._StructDefine(struct_name, field_num)
            col_end = self._col

            self._is_layout = True

            if repeated_num >= 1:
                field_rule = "repeated"
            elif field_rule == "required_struct":
                field_rule = "required"
            else:
                field_rule = "optional"

            self._LayoutOneField(field_rule, struct_name, field_name)

            actual_repeated_num = 1 if (repeated_num == 0) else repeated_num
            self._col += (actual_repeated_num-1) * (col_end-col_begin)
        else :
            self._col += 1
            return

    def _IsStructDefined(self, struct_name) :
        for name in self._struct_name_list :
            if name == struct_name :
                return True
        return False

    def _StructDefine(self, struct_name, field_num) :
        """Ƕ�׽ṹ����"""

        self._col += 1
        self._LayoutStructHead(struct_name)
        self._IncreaseIndentation()
        self._field_index_list.append(1)

        while field_num > 0 :
            self._FieldDefine(0)
            field_num -= 1

        self._field_index_list.pop()
        self._DecreaseIndentation()
        self._LayoutStructTail()

    def _LayoutFileHeader(self) :
        """����PB�ļ���������Ϣ"""
        self._output.append("/**\n")
        self._output.append("* @file:   " + self._pb_file_name + "\n")
        self._output.append("* @author: jameyli <jameyli AT tencent DOT com>\n")
        self._output.append("* @brief:  ����ļ���ͨ�������Զ����ɵģ����鲻Ҫ�ֶ��޸�\n")
        self._output.append("*/\n")
        self._output.append("\n")


    def _LayoutStructHead(self, struct_name) :
        """���ɽṹͷ"""
        if not self._is_layout :
            return
        self._output.append("\n")
        self._output.append(" "*self._indentation + "message " + struct_name + "{\n")

    def _LayoutStructTail(self) :
        """���ɽṹβ"""
        if not self._is_layout :
            return
        self._output.append(" "*self._indentation + "}\n")
        self._output.append("\n")

    def _LayoutComment(self, comment) :
        # ����C����ע�ͣ���ֹ���з���
        if not self._is_layout :
            return
        if comment.count("\n") > 1 :
            if comment[-1] != '\n':
                comment = comment + "\n"
                comment = comment.replace("\n", "\n" + " " * (self._indentation + TAP_BLANK_NUM),
                        comment.count("\n")-1 )
                self._output.append(" "*self._indentation + "/** " + comment + " "*self._indentation + "*/\n")
        else :
            self._output.append(" "*self._indentation + "/** " + comment + " */\n")

    def _LayoutOneField(self, field_rule, field_type, field_name) :
        """���һ�ж���"""
        if not self._is_layout :
            return
        if field_name.find('=') > 0 :
            name_and_value = field_name.split('=')
            self._output.append(" "*self._indentation + field_rule + " " + field_type \
                    + " " + str(name_and_value[0]).strip() + " = " + self._GetAndAddFieldIndex()\
                    + " [default = " + str(name_and_value[1]).strip() + "]" + ";\n")
            return

        if (field_rule != "required" and field_rule != "optional") :
            self._output.append(" "*self._indentation + field_rule + " " + field_type \
                    + " " + field_name + " = " + self._GetAndAddFieldIndex() + ";\n")
            return

        if field_type == "int32" or field_type == "int64"\
                or field_type == "uint32" or field_type == "uint64"\
                or field_type == "sint32" or field_type == "sint64"\
                or field_type == "fixed32" or field_type == "fixed64"\
                or field_type == "sfixed32" or field_type == "sfixed64" \
                or field_type == "double" or field_type == "float" :
                    self._output.append(" "*self._indentation + field_rule + " " + field_type \
                            + " " + field_name + " = " + self._GetAndAddFieldIndex()\
                            + " [default = 0]" + ";\n")
        elif field_type == "string" or field_type == "bytes" :
            self._output.append(" "*self._indentation + field_rule + " " + field_type \
                    + " " + field_name + " = " + self._GetAndAddFieldIndex()\
                    + " [default = \"\"]" + ";\n")
        else :
            self._output.append(" "*self._indentation + field_rule + " " + field_type \
                    + " " + field_name + " = " + self._GetAndAddFieldIndex() + ";\n")
        return

    def _IncreaseIndentation(self) :
        """��������"""
        self._indentation += TAP_BLANK_NUM

    def _DecreaseIndentation(self) :
        """��������"""
        self._indentation -= TAP_BLANK_NUM

    def _GetAndAddFieldIndex(self) :
        """����ֶε����, �����������"""
        index = str(self._field_index_list[- 1])
        self._field_index_list[-1] += 1
        return index

    def _LayoutArray(self) :
        """������鶨��"""
        self._output.append("message " + self._sheet_name + "_ARRAY {\n")
        self._output.append("    repeated " + self._sheet_name + " items = 1;\n}\n")

    def _Write2File(self) :
        """������ļ�"""
        pb_file = open(self._pb_file_name, "w+")
        pb_file.writelines(self._output)
        pb_file.close()


class DataParser:
    """����excel������"""
    def __init__(self, xls_file_path, sheet_name):
        self._xls_file_path = xls_file_path
        self._sheet_name = sheet_name

        try :
            self._workbook = xlrd.open_workbook(self._xls_file_path)
        except BaseException, e :
            print "open xls file(%s) failed!"%(self._xls_file_path)
            raise

        try :
            self._sheet =self._workbook.sheet_by_name(self._sheet_name)
        except BaseException, e :
            print "open sheet(%s) failed!"%(self._sheet_name)
            raise

        self._row_count = len(self._sheet.col_values(0))
        self._col_count = len(self._sheet.row_values(0))

        self._row = 0
        self._col = 0

        try:
            self._module_name = self._sheet_name.lower() + "_pb2"
            sys.path.append(os.getcwd())
            exec('from '+self._module_name + ' import *');
            self._module = sys.modules[self._module_name]
        except BaseException, e :
            print "load module(%s) failed"%(self._module_name)
            raise

    def Parse(self) :
        """����Ľӿ�:��������"""
        LOG_INFO("begin parse, row_count = %d, col_count = %d", self._row_count, self._col_count)

        item_array = getattr(self._module, self._sheet_name+'_ARRAY')()

        # ���ҵ�����ID����
        id_col = 0
        for id_col in range(0, self._col_count) :
            info_id = str(self._sheet.cell_value(self._row, id_col)).strip()
            if info_id == "" :
                continue
            else :
                break

        for self._row in range(4, self._row_count) :
            # ��� id �� �� ֱ����������
            info_id = str(self._sheet.cell_value(self._row, id_col)).strip()
            if info_id == "" :
                LOG_WARN("%d is None", self._row)
                continue
            item = item_array.items.add()
            self._ParseLine(item)

        LOG_INFO("parse result:\n%s", item_array)

        self._WriteReadableData2File(str(item_array))

        data = item_array.SerializeToString()
        self._WriteData2File(data)


        #comment this line for test .by kevin at 2013��1��12�� 17:23:35
        LogHelp.close()

    def _ParseLine(self, item) :
        LOG_INFO("%d", self._row)

        self._col = 0
        while self._col < self._col_count :
            self._ParseField(0, 0, item)

    def _ParseField(self, max_repeated_num, repeated_num, item) :
        field_rule = str(self._sheet.cell_value(0, self._col)).strip()

        if field_rule == "required" or field_rule == "optional" :
            field_name = str(self._sheet.cell_value(2, self._col)).strip()
            if field_name.find('=') > 0 :
                name_and_value = field_name.split('=')
                field_name = str(name_and_value[0]).strip()
            field_type = str(self._sheet.cell_value(1, self._col)).strip()

            LOG_INFO("%d|%d", self._row, self._col)
            LOG_INFO("%s|%s|%s", field_rule, field_type, field_name)

            if max_repeated_num == 0 :
                field_value = self._GetFieldValue(field_type, self._row, self._col)
                # ��value����ֵ
                if field_value != None :
                    item.__setattr__(field_name, field_value)
                self._col += 1
            else :
                if repeated_num == 0 :
                    if field_rule == "required" :
                        print "required but repeated_num = 0"
                        raise
                else :
                    for col in range(self._col, self._col + repeated_num):
                        field_value = self._GetFieldValue(field_type, self._row, col)
                        # ��value����ֵ
                        if field_value != None :
                            item.__getattribute__(field_name).append(field_value)
                self._col += max_repeated_num

        elif field_rule == "repeated" :
            # 2011-11-29 �޸�
            # ��repeated�ڶ��������Ͷ��壬���ʾ��ǰ�ֶ���repeated�����������ڵ����÷ֺ����
            second_row = str(self._sheet.cell_value(FIELD_TYPE_ROW, self._col)).strip()
            LOG_DEBUG("repeated|%s", second_row);
            # exel�п�����С����
            if second_row.isdigit() or second_row.find(".") != -1 :
                # �������һ�����һ���ṹ��
                max_repeated_num = int(float(second_row))
                read = self._sheet.cell_value(self._row, self._col)
                repeated_num = 0 if read == "" else int(self._sheet.cell_value(self._row, self._col))

                LOG_INFO("%s|%d|%d", field_rule, max_repeated_num, repeated_num)

                if max_repeated_num == 0 :
                    print "max repeated num shouldn't be 0"
                    raise

                if repeated_num > max_repeated_num :
                    repeated_num = max_repeated_num

                self._col += 1
                self._ParseField(max_repeated_num, repeated_num, item)

            else :
                # һ���Ǽ򵥵ĵ��ֶΣ���ֵ�÷ֺ����
                # һ��Ҳֻ������������
                field_type = second_row
                field_name = str(self._sheet.cell_value(FIELD_NAME_ROW, self._col)).strip()
                field_value_str = unicode(self._sheet.cell_value(self._row, self._col))
                #field_value_str = unicode(self._sheet.cell_value(self._row, self._col)).strip()

                # LOG_INFO("%d|%d|%s|%s|%s",
                #         self._row, self._col, field_rule, field_type, field_name, field_value_str)

                #2013-01-24 jamey
                #���ӳ����ж�
                if len(field_value_str) > 0:
                    if field_value_str.find(";\n") > 0 :
                        field_value_list = field_value_str.split(";\n")
                    else :
                        field_value_list = field_value_str.split(";")

                    for field_value in field_value_list :
                        if field_type == "bytes":
                            item.__getattribute__(field_name).append(field_value.encode("utf8"))
                        else:
                            item.__getattribute__(field_name).append(int(float(field_value)))

                self._col += 1

        elif field_rule == "required_struct" or field_rule == "optional_struct":
            field_num = int(self._sheet.cell_value(FIELD_TYPE_ROW, self._col))
            struct_name = str(self._sheet.cell_value(FIELD_NAME_ROW, self._col)).strip()
            field_name = str(self._sheet.cell_value(FIELD_COMMENT_ROW, self._col)).strip()

            LOG_INFO("%s|%d|%s|%s", field_rule, field_num, struct_name, field_name)


            col_begin = self._col

            # ����ѭ��һ��
            if max_repeated_num == 0 :
                struct_item = item.__getattribute__(field_name)
                self._ParseStruct(field_num, struct_item)

            else :
                if repeated_num == 0 :
                    if field_rule == "required_struct" :
                        print "required but repeated_num = 0"
                        raise
                    # �ȶ�ȡ��ɾ����
                    struct_item = item.__getattribute__(field_name).add()
                    self._ParseStruct(field_num, struct_item)
                    item.__getattribute__(field_name).__delitem__(-1)

                else :
                    for num in range(0, repeated_num):
                        struct_item = item.__getattribute__(field_name).add()
                        self._ParseStruct(field_num, struct_item)

            col_end = self._col

            max_repeated_num = 1 if (max_repeated_num == 0) else max_repeated_num
            actual_repeated_num = 1 if (repeated_num==0) else repeated_num
            self._col += (max_repeated_num - actual_repeated_num) * ((col_end-col_begin)/actual_repeated_num)

        else :
            self._col += 1
            return

    def _ParseStruct(self, field_num, struct_item) :
        """Ƕ�׽ṹ���ݶ�ȡ"""

        # �����ṹ�嶨��
        self._col += 1
        while field_num > 0 :
            self._ParseField(0, 0, struct_item)
            field_num -= 1

    def _GetFieldValue(self, field_type, row, col) :
        """��pb����ת��Ϊpython����"""

        field_value = self._sheet.cell_value(row, col)
        LOG_INFO("%d|%d|%s", row, col, field_value)

        try:
            if field_type == "int32" or field_type == "int64"\
                    or  field_type == "uint32" or field_type == "uint64"\
                    or field_type == "sint32" or field_type == "sint64"\
                    or field_type == "fixed32" or field_type == "fixed64"\
                    or field_type == "sfixed32" or field_type == "sfixed64" :
                        if len(str(field_value).strip()) <=0 :
                            return None
                        else :
                            return int(field_value)
            elif field_type == "double" or field_type == "float" :
                    if len(str(field_value).strip()) <=0 :
                        return None
                    else :
                        return float(field_value)
            elif field_type == "string" :
                field_value = unicode(field_value)
                if len(field_value) <= 0 :
                    return None
                else :
                    return field_value
            elif field_type == "bytes" :
                field_value = unicode(field_value).encode('utf-8')
                if len(field_value) <= 0 :
                    return None
                else :
                    return field_value
            else :
                return None
        except BaseException, e :
            print "parse cell(%u, %u) error, please check it, maybe type is wrong."%(row, col)
            raise

    def _WriteData2File(self, data) :
        file_name = self._sheet_name.lower() + ".bin"
        file = open(file_name, 'wb+')
        file.write(data)
        file.close()

    def _WriteReadableData2File(self, data) :
        file_name = self._sheet_name.lower() + ".txt"
        file = open(file_name, 'wb+')
        file.write(data)
        file.close()



if __name__ == '__main__' :
    """���"""
    if len(sys.argv) < 3 :
        print "Usage: %s sheet_name(should be upper) xls_file" %(sys.argv[0])
        sys.exit(-1)

    # option 0 ����proto��data 1 ֻ����proto 2 ֻ����data
    op = 0
    if len(sys.argv) > 3 :
        op = int(sys.argv[3])

    sheet_name =  sys.argv[1]
    if (not sheet_name.isupper()):
        print "sheet_name should be upper"
        sys.exit(-2)

    xls_file_path =  sys.argv[2]

    if op == 0 or op == 1:
        try :
            tool = SheetInterpreter(xls_file_path, sheet_name)
            tool.Interpreter()
        except BaseException, e :
            print "Interpreter Failed!!!"
            print e
            sys.exit(-3)

        print "Interpreter Success!!!"

    if op == 0 or op == 2:
        try :
            parser = DataParser(xls_file_path, sheet_name)
            parser.Parse()
        except BaseException, e :
            print "Parse Failed!!!"
            print e
            sys.exit(-4)

        print "Parse Success!!!"
