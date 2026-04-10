from bigint import BigInt
q,r = BigInt('-10')._divide_newton('-10', '3')
print(f'-10/3 = {q}, r={r}')
print(f'Expected: q=-3, r=-1')
