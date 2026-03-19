import re
from collections import defaultdict, OrderedDict

def parse_term(term):
    # 移除空白
    term = term.replace(' ', '')
    coefficient = 1
    variables = defaultdict(int)

    # 匹配係數
    coeff_pattern = r'^([+-]?(\d+))\*?'
    coeff_match = re.match(coeff_pattern, term)
    if coeff_match:
        coeff_str = coeff_match.group(1)
        coefficient = int(coeff_str)
        term = term[coeff_match.end():]
    else:
        # 檢查是否只有符號
        sign_pattern = r'^([+-])'
        sign_match = re.match(sign_pattern, term)
        if sign_match:
            coefficient = 1 if sign_match.group(1) == '+' else -1
            term = term[sign_match.end():]
        else:
            coefficient = 1

    # 匹配所有變數及其指數
    var_pattern = r'([a-zA-Z])(?:\^(\d+))?'
    var_matches = re.findall(var_pattern, term)
    for var, exp in var_matches:
        if exp == '':
            exp = 1
        else:
            exp = int(exp)
        variables[var] += exp

    # 處理僅為數字的項
    if not var_matches and re.match(r'^[+-]?\d+$', term):
        coefficient *= int(term)

    return coefficient, variables

def multiply_terms(term1, term2):
    coeff1, vars1 = term1
    coeff2, vars2 = term2
    result_coeff = coeff1 * coeff2
    result_vars = defaultdict(int, vars1)

    for var, exp in vars2.items():
        result_vars[var] += exp

    return result_coeff, result_vars

def term_to_string(term):
    coeff, vars = term
    if coeff == 0:
        return ''
    
    # 將變數按照字母順序排序
    sorted_vars = sorted(vars.items(), key=lambda x: x[0])

    # 構建變數部分
    var_parts = []
    for var, exp in sorted_vars:
        if exp == 1:
            var_parts.append(f"{var}")
        else:
            var_parts.append(f"{var}^{exp}")
    var_part = ''.join(var_parts)

    # 處理係數部分
    if coeff == 1:
        if var_part:
            return var_part
        else:
            return '1'
    elif coeff == -1:
        if var_part:
            return f"-{var_part}"
        else:
            return '-1'
    else:
        if var_part:
            return f"{coeff}*{var_part}"
        else:
            return str(coeff)

def parse_polynomial(poly):
    terms = re.split(r'(?=[+-])', poly)
    parsed_terms = []
    
    for term in terms:
        term = term.strip()
        if term.startswith('+'):
            term = term[1:]
        parsed_terms.append(parse_term(term))
    
    return parsed_terms

def expand_polynomials(polys):
    expanded_terms = []
    for poly in polys:
        expanded_terms.append(parse_polynomial(poly))

    result = expanded_terms[0]
    for poly_terms in expanded_terms[1:]:
        new_result = []
        for term1 in result:
            for term2 in poly_terms:
                new_result.append(multiply_terms(term1, term2))
        result = new_result

    # 合併相同項次，保持順序
    combined_terms = OrderedDict()
    for coeff, vars in result:
        # 將變數轉換為排序的元組，用於鍵值
        vars_tuple = tuple(sorted((var, int(exp)) for var, exp in vars.items()))
        if vars_tuple in combined_terms:
            combined_terms[vars_tuple] += coeff
        else:
            combined_terms[vars_tuple] = coeff

    # 移除係數為 0 的項次
    combined_terms = OrderedDict((k, v) for k, v in combined_terms.items() if v != 0)

    return combined_terms

def polynomial_to_string(combined_terms):
    result = []
    for vars_tuple, coeff in combined_terms.items():
        if coeff == 0:
            continue
        term = term_to_string((coeff, dict(vars_tuple)))
        if coeff > 0 and result:
            result.append(f"+{term}")
        else:
            result.append(term)
    return ''.join(result).replace('+-', '-')

def main():
    input_poly = input("Input the polynomials: ")
    # 將輸入的多項式轉換為獨立的多項式表達式
    polys = re.findall(r'\(.*?\)', input_poly)
    polys = [poly[1:-1] for poly in polys]  # 去掉括號

    # 展開多項式
    combined_terms = expand_polynomials(polys)

    # 轉換為字串
    result = polynomial_to_string(combined_terms)
    print("Output Result:", result)

# 執行程式
if __name__ == "__main__":
    main()
