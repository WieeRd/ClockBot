# Functions for markdown formatting
# Not so useful tbh but I made it anyway

def codeword(txt):
	return '`' + txt + '`'

def codeline(txt, lang=''):
    return "```" + lang + '\n' + txt + '\n' + "```"

def bold(txt):
	return "**" + txt + "**"

def italic(txt):
	return '_' + txt + '_'

def emphasize(txt):
	return "***" + txt + "***"

def underln(txt):
	return "__" + txt + "__"

def strike(txt):
	return "~~" + txt + "~~"

def spoiler(txt):
	return "||" + txt + "||"

def quote(txt):
	return ">>>" + txt

cd = codeline
cw = codeword
bd = bold
it = italic
ep = emphasize
u_ = underln
st = strike
sp = spoiler
qt = quote

def mdform(txt, *func, **kwargs):
	for f in func:
		if((f==codeln) and (kwargs['lang']!=None)):
			txt = f(txt, kwargs['lang'])
		else:
			txt = f(txt)
	return txt

# ex) mdform("asdf", bd, it, lang='python')