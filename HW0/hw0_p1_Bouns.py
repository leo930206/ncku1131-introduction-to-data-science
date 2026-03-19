import re
from collections import defaultdict
from itertools import product

def parse_term(term):
    # 解析單項式，取得係數和變數次方
    coef_match = re.match(r'^([+-]?\d*)', term)
    coef_str = coef_match.group(1)
    if coef_str in ['', '+']:
        coef = 1
    elif coef_str == '-':
        coef = -1
    else:
        coef = int(coef_str)
    vars_dict = defaultdict(int)
    var_pattern = r'([A-Z])(\d*)'
    for var, exp_str in re.findall(var_pattern, term[coef_match.end():]):
        exp = int(exp_str) if exp_str else 1
        vars_dict[var] += exp
    return coef, vars_dict

def multiply_terms(term1, term2):
    # 單項式相乘，合併係數和指數
    coef1, vars_dict1 = term1
    coef2, vars_dict2 = term2
    new_coef = coef1 * coef2
    new_vars_dict = defaultdict(int, vars_dict1)
    for var, exp in vars_dict2.items():
        new_vars_dict[var] += exp
    return new_coef, new_vars_dict

def expand_polynomial(poly):
    # 展開多項式，取得所有單項式
    poly = poly.strip('()')
    terms = re.findall(r'[+-]?\d*(?:[A-Z]\d*)+', poly)
    expanded_terms = []
    for term in terms:
        parsed_term = parse_term(term)
        if parsed_term:
            expanded_terms.append(parsed_term)
    return expanded_terms

def combine_terms(terms):
    # 合併同類項，保留項目的順序
    combined_terms = []
    term_keys = []
    for coef, vars_dict in terms:
        vars_key = tuple(sorted(vars_dict.items()))
        if vars_key in term_keys:
            index = term_keys.index(vars_key)
            combined_coef, _ = combined_terms[index]
            combined_terms[index] = (combined_coef + coef, vars_dict)
        else:
            term_keys.append(vars_key)
            combined_terms.append((coef, vars_dict))
    # 移除係數為零的項目
    combined_terms = [(coef, vars_dict) for coef, vars_dict in combined_terms if coef != 0]
    return combined_terms

def format_output(terms):
    # 格式化輸出結果，按照原始順序排列
    result_str = ''
    for coef, vars_dict in terms:
        if coef == 0:
            continue
        var_part = ''.join([f"{var}{exp if exp != 1 else ''}" for var, exp in sorted(vars_dict.items())])
        if coef == 1:
            result_str += f"+{var_part}"
        elif coef == -1:
            result_str += f"-{var_part}"
        else:
            result_str += f"{'+' if coef > 0 else ''}{coef}{var_part}"
    return result_str.lstrip('+')  # 移除最前面的 "+"

def polynomial_expansion(input_poly):
    # 主函式，處理多項式展開
    poly_groups = re.findall(r'\([^\(\)]+\)', input_poly)

    # 展開第一個多項式
    result_terms = expand_polynomial(poly_groups[0])

    # 依次展開剩餘的多項式
    for poly in poly_groups[1:]:
        expanded_terms = expand_polynomial(poly)
        temp_result = []
        for term1, term2 in product(result_terms, expanded_terms):
            temp_result.append(multiply_terms(term1, term2))
        result_terms = temp_result

    # 合併同類項並格式化輸出
    result_terms = combine_terms(result_terms)
    output_result = format_output(result_terms)

    return output_result

# 主程式，接受使用者輸入
input_poly = input("Input the polynomials: ")
output_result = polynomial_expansion(input_poly)
print(f"Output Result: {output_result}")
