# encoding=utf8
"""
For: 用于修复翻译文章中出现 issue#4 中所提到的格式问题
Author: SkyRover
Date: 2018-01-19
"""

import re
import os
import argparse
import fire
from collections import OrderedDict


# 数字，单词和中文接触的方式有三种
# 1. 两边接触的
# 2. 左边接触，右边不接触的
# 3. 右边接触，左边不接触的
# 另外还有两种，数字，单词在行首或者行尾的情况

patterns = OrderedDict({
    # case 1: 中china国, 中001国 -> 中 china 国 中 001 国
    "case1": [re.compile(r'([\u4e00-\u9fa5])([A-Za-z0-9]+|`[A-Za-z0-9]+`)([\u4e00-\u9fa5])'), r"\1 \2 \3"],
    # case 2: 中国china。 -> 中国 china。
    "case2": [re.compile(r'([\u4e00-\u9fa5])([A-Za-z0-9]+|`[A-Za-z0-9]+`)([[:punct:]]*|[[:space:]]*)+'), r"\1 \2\3"],
    # case 3: ,China中国 -> ,China 中国
    "case3": [re.compile(r'([[:punct:]]*|[[:space:]]*)+([A-Za-z0-9]+|`[A-Za-z0-9]+`)([\u4e00-\u9fa5])'), r"\1\2 \3"],
    # case 4: China中国 -> China 中国
    "case4": [re.compile(r'^([A-Za-z0-9]+|`[A-Za-z0-9]+`)([\u4e00-\u9fa5])'), r"\1 \2"],
    # case 5: 中国China -> 中国 China
    "case5": [re.compile(r'([\u4e00-\u9fa5])([A-Za-z0-9]+|`[A-Za-z0-9]+`)$'), r"\1 \2"]
})


def fix_format(path, verbose=False, test=False):
    basename = os.path.basename(path)
    dirname = os.path.dirname(path)
    output = os.path.join(dirname, "format_{}".format(basename))
    origin_lines = open(path, 'r', encoding="utf-8").readlines()
    res = []
    update = False
    for lineno, line in enumerate(origin_lines, start=1):
        for _, pattern_list in patterns.items():
            pattern = pattern_list[0]
            repl = pattern_list[1]
            newline = re.sub(pattern, repl, line)
            if line != newline:
                if verbose:
                    print(">"*50)
                    print("Handling Line: {}".format(lineno))
                    print("Before: {}".format(line))
                    print("="*50)
                    print("After:  {}".format(newline))
                line = newline
                update = True
        res.append(line)
    if not test and update:
        print("Output: {}".format(output))
        with open(output, 'w') as f:
            f.writelines(res)
    elif not update:
        print("Nothing to format...")
    print("Done...")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Issue#4 Format tools')
    # parser.add_argument('path', help="要进行格式化的文件路径")
    # parser.add_argument('--verbose', dest='verbose', action="store_true", help="显示处理详情")
    # parser.add_argument("--test", dest="test", action="store_true", help="进行测试，而不是输出文件")
    # args = parser.parse_args()
    # fix_format(args.path, verbose=args.verbose, test=args.test)
    fire.Fire(fix_format)
