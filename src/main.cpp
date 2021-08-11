#include "pmatch.h"
#include <iostream>
#include <string>
#include <vector>

pmatch::NFA value(const std::string& s)
{
    pmatch::NFA expr(s[0]);
    for (char c : s.substr(1)) {
        pmatch::NFA n(c);
        expr.concat(n);
    }
    return expr;
}

pmatch::NFA group(const std::string& s)
{
    pmatch::NFA expr(s[0]);
    for (char c : s.substr(1)) {
        pmatch::NFA n(c);
        expr.uni(n);
    }
    return expr;
}

std::vector<char> stv(const std::string& s)
{
    std::vector<char> result;
    for (char c : s)
        result.push_back(c);
    return result;
}

int main(int argc, char *argv[])
{
    if (argc == 1) {
        std::cout << "Usage: " << argv[0] << " STRING" << std::endl;
        return 1;
    }
    std::string prompt(argv[1]);

    pmatch::NFA expr(value("http")), v2(value("://")), abc(group("abcdefghijklmnopqrstuvwxyz0123456789"));
    expr.concat(value("s").optional());
    expr.concat(v2);
    expr.concat(abc.semi_closure());
    expr.concat(value(".").concat(abc.semi_closure()).semi_closure());
    expr.concat(value("/").concat(abc.closure()).closure());

    std::cout << expr.match(stv(prompt)) << std::endl;
}