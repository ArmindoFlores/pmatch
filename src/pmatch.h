#ifndef PMATCH_H
#define PMATCH_H

#include <utility>
#include <set>
#include <vector>
#include <cstdlib>
typedef char object;

namespace pmatch {
    class Node {
    public:
        bool is_terminal;

        Node(bool is_terminal=false);
        ~Node();

        std::pair<Node*, object> &get_transition();
        void set_transition(Node *to, object symbol);
        void set_transition(Node &to, object symbol);
        std::set<Node*> &get_epsilon_transitions();
        void add_epsilon_transition(Node *to);
        void add_epsilon_transition(Node &to);

    private:
        std::pair<Node*, object> transition;
        std::set<Node*> epsilon_transitions;
    };

    /**
     * This class implements a non-deterministic finite automaton
     */
    class NFA {
    public:
        NFA(object symbol);
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
        ssize_t match(const std::vector<object>& inp);

    private:
        // Start and end nodes, respectively
        Node *start, *end;
        // A set of all nodes allocated by this NFA, to be deleted once the destructor is called
        std::set<Node*> to_delete;
        Node *create_node(bool is_terminal=false);
    };
}

#endif