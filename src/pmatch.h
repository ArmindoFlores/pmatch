#ifndef PMATCH_H
#define PMATCH_H

#include <utility>
#include <set>
#include <vector>
#include <cstdlib>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;

namespace pmatch {
    class Node {
    public:
        bool is_terminal;

        Node(bool is_terminal=false);
        ~Node();

        std::pair<Node*, py::object> &get_transition();
        void set_transition(Node *to, const py::object &symbol);
        void set_transition(Node &to, const py::object &symbol);
        bool has_transition() const;
        std::set<Node*> &get_epsilon_transitions();
        void add_epsilon_transition(Node *to);
        void add_epsilon_transition(Node &to);

    private:
        bool p_has_transition;
        std::pair<Node*, py::object> transition;
        std::set<Node*> epsilon_transitions;
    };

    /**
     * This class implements a non-deterministic finite automaton
     */
    class NFA {
    public:
        NFA(py::object symbol);
        NFA(NFA&&);
        ~NFA();

        /**
         * Concatenate this NFA to another (updating both of them)
         * @param other is the other NFA
         * @returns the resulting automaton
         */
        NFA &concat(NFA& other);
        /**
         * Create a union of two NFA's (updating both of them)
         * @param other is the other NFA
         * @returns the resulting automaton
         */
        NFA &uni(NFA& other);
        /**
         * Create a closure
         * @returns the resulting automaton
         */
        NFA &closure();
        /**
         * Create a semi-closure
         * @returns the resulting automaton
         * @note this is a made-up term that is supposed to represent the +
         * operator in regular expressions
         */
        NFA &semi_closure();
        /**
         * Make this NFA 'optional'
         * @returns the resulting automaton
         * @note this is a made-up term that is supposed to represent the ?
         * operator in regular expressions
         */
        NFA &optional();

        /**
         * Try to apply the pattern represented by the NFA to the start of the string
         * @returns the size of the match if one is found, and -1 otherwise
         */
        ssize_t match(std::vector<py::object>& inp);

    private:
        // Start and end nodes, respectively
        Node *start, *end;
        // A set of all nodes allocated by this NFA, to be deleted once the destructor is called
        std::set<Node*> to_delete;
        Node *create_node(bool is_terminal=false);
    };
}

PYBIND11_MODULE(_pmatch, m) {
    py::class_<pmatch::NFA>(m, "NFA")
        .def(py::init<py::object>())
        .def("concatenation", &pmatch::NFA::concat)
        .def("union", &pmatch::NFA::uni)
        .def("closure", &pmatch::NFA::closure)
        .def("semi_closure", &pmatch::NFA::semi_closure)
        .def("optional", &pmatch::NFA::optional)
        .def("match", &pmatch::NFA::match);
}

#endif