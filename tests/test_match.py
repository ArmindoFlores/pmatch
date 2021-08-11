import pmatch

def test_or_2():
    a, b = "a", "b"
    expr = pmatch.compile("a|b", locals())
    assert expr.match("a") == 1
    assert expr.match("b") == 1

def test_or_3():
    a, b, c = "a", "b", "c"
    expr = pmatch.compile("a|b|c", locals())
    assert expr.match("a") == 1
    assert expr.match("b") == 1
    assert expr.match("c") == 1

def test_or_complex():
    a, b = "a", "b"
    expr = pmatch.compile("(a b)|b", locals())
    assert expr.match("a") == -1
    assert expr.match("b") == 1
    assert expr.match("ab") == 2

def test_or_redundant():
    a = "a"
    expr = pmatch.compile("(a a)|a", locals())
    assert expr.match("a") == 1
    assert expr.match("aa") == 2
    assert expr.match("aaa") == 2

    expr = pmatch.compile("a|(a a)", locals())
    assert expr.match("a") == 1
    assert expr.match("aa") == 2
    assert expr.match("aaa") == 2

def test_optional():
    a, b = "a", "b"
    expr = pmatch.compile("a (b?) a", locals())
    assert expr.match("a") == -1
    assert expr.match("aa") == 2
    assert expr.match("aba") == 3
    assert expr.match("abba") == -1
    assert expr.match("ab") == -1

def test_any():
    a, b = "a", "b"
    expr = pmatch.compile("a (b*) a", locals())
    assert expr.match("a") == -1
    assert expr.match("aa") == 2
    assert expr.match("aba") == 3
    assert expr.match("abba") == 4
    assert expr.match("ab") == -1

def test_some():
    a, b = "a", "b"
    expr = pmatch.compile("a (b+) a", locals())
    assert expr.match("a") == -1
    assert expr.match("aa") == -1
    assert expr.match("aba") == 3
    assert expr.match("abba") == 4
    assert expr.match("ab") == -1

def test_or_and_some():
    a = "a"
    expr = pmatch.compile("((a a)|a)+", locals())
    assert expr.match("") == -1
    assert expr.match("a") == 1
    assert expr.match("aa") == 2
    assert expr.match("aaa") == 3
    assert expr.match("aaaa") == 4
    assert expr.match("aaaaa") == 5
    assert expr.match("aaaaaa") == 6
    assert expr.match("aaaaaaa") == 7
    assert expr.match("aaaaaaaa") == 8

def test_urls():
    h = "h"
    t = "t"
    p = "p"
    s = "s"
    c = ":"
    sl = "/"
    d = "."
    a = "a"
    expr = pmatch.compile("h t t p (s?) c sl sl (a+)((d (a+))*)", locals())
    assert expr.match("http://aaaaa.aa") == 15
    assert expr.match("https://aaaaa.aa") == 16
    assert expr.match("https://aaa_aa.aa") == 11
    assert expr.match("https://aaaaa.aa.aaa") == 20