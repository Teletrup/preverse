dbg = False

def re_dbg(v):
  global dbg
  dbg = v

def re_end(s):
  if s == '':
    return '', None
  return None, None

def re_str(expr, s):
  ss = s[:len(expr)]
  if ss == expr:
    return ss, s[len(expr):] 
    #It doesn't throw "out of range", because if end in a slice is greater then the length,
    #it just returns the whole string. 
    #TODO describe why the condition makes it impossible for the 2nd slice to be invalid 
  else:
    return None, None

def re_ran(lo, hi, s):
  if s == '':
    return None, None
  c = s[0]
  rst = s[1:]
  if (ord(c) >= ord(lo) and ord(c) <= ord(hi)):
    return c, rst
  return None, None

def re_alt(exprs, s):
  for expr in exprs:
    val, rst = re(expr, s)
    if val != None:
      return val, rst
  return None, None

def re_and(exprs, s):
  for expr in exprs:
    val, rst = re(expr, s)
    if val == None:
      return None, None
  else:
    return val, rst

def re_seq(exprs, s):
  val_acc = ''
  rst = s
  for expr in exprs:
    val, rst = re(expr, rst)
    if rst == None:
      return None, None
    val_acc += val
  return val_acc, rst

def re_rep(expr, lo, hi, s):
  val_acc = ''
  s_acc = s
  i = 0
  while hi == None or i <= hi:
    val, rst = re(expr, s_acc)
    if rst == None:
      if lo == None or i >= lo:
        return val_acc, s_acc #rst should be OK, because misses should always return the input string
      return None, None     #^^ now it's not OK. what to do?
    val_acc += val
    s_acc = rst
    i += 1
  return None, None

def re_not(expr, s):
  val, rst = re(expr, s) #returning tuple shenanigans
  if val == None:
    return (s[0], s[1:]) if s else (None, None) #should it return empty string?
  return None, None


re_defs = {
  'wsc' : ['ran', chr(0), ' '],
  'iwsc' : ['and', ['not', 'nl'], 'wsc'],
  'nl' : ['alt', ['str', '\r\n'], ['str', '\n']],
  'numc': ['ran', '0', '9'],
  'alphac': ['alt', ['ran', 'a', 'z'], ['ran', 'A', 'Z']],
  'alphanumc': ['alt', 'numc', 'alphac'],
  'gap' : ['rep', ['seq', ['rep', 'iwsc'], ['alt', 'nl', ['end']]], 2], #infinite loop with rep end
  'paragraph' : ['rep', ['not', 'gap'], 1]
}


def re(expr, s):
  if dbg:
    print(f're({expr}, {s})')
  if type(expr) == str:
    #TODO "expression not expanded, use an expanded expression or re-ex function"
    return re(re_defs[expr], s)
  if type(expr) == list:
    op, *args = expr
    if op == 'end':
      return re_end(s)
    if op == 'str':
      return re_str(args[0], s)
    if op == 'ran':
      return re_ran(*args, s)
    if op == 'alt':
      return re_alt(args, s)
    if op == 'and':
      return re_and(args, s)
    if op == 'seq':
      return re_seq(args, s)
    if op == 'rep':
      lo = args[1] if len(args) >= 2 else None
      hi = args[2] if len(args) >= 3 else None
      return re_rep(args[0], lo, hi, s)
    if op == 'not':
      return re_not(args[0], s)

def lex(rules, text):
  tokens = []
  while text:
    for r in rules:
      val, res = re(r, text)
      if val != None:
        tokens.append([r, val])
        text = res
        break
  return tokens
