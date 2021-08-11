#include "pmatch.h"
#include <algorithm>

pmatch::Node::Node(bool is_terminal): is_terminal(is_terminal) {}

pmatch::Node::~Node()
{
}

std::pair<pmatch::Node*, object> &pmatch::Node::get_transition()
{
    return transition;
}

void pmatch::Node::set_transition(pmatch::Node *to, object symbol)
{
    transition.first = to;
    transition.second = symbol;
}

void pmatch::Node::set_transition(pmatch::Node &to, object symbol)
{
    pmatch::Node::set_transition(&to, symbol);
}

std::set<pmatch::Node*> &pmatch::Node::get_epsilon_transitions()
{
    return epsilon_transitions;
}

void pmatch::Node::add_epsilon_transition(Node *to)
{
    epsilon_transitions.insert(to);
}

void pmatch::Node::add_epsilon_transition(Node &to)
{
    epsilon_transitions.insert(&to);
}

pmatch::NFA::NFA(object symbol)
{
    start = create_node(false);
    end = create_node(true);
    if (symbol != 0)
        start->set_transition(end, symbol);
    else
        start->add_epsilon_transition(end);
}

pmatch::NFA::NFA(NFA&& other)
{
    start = other.start;
    end = other.end;
    to_delete = other.to_delete;
    other.to_delete.clear();
}

pmatch::NFA::~NFA()
{
    for (Node* n : to_delete)
        delete n;
}

pmatch::NFA &pmatch::NFA::concat(pmatch::NFA &other)
{
    end->is_terminal = false;
    end->add_epsilon_transition(other.start);
    end = other.end;
    for (pmatch::Node *n : other.to_delete)
        to_delete.insert(n);
    other.to_delete.clear();
    return *this;
}

pmatch::NFA &pmatch::NFA::uni(pmatch::NFA &other)
{
    pmatch::Node *n_start = create_node(false), *n_end = create_node(true);
    end->is_terminal = false;
    other.end->is_terminal = false;
    n_start->add_epsilon_transition(start);
    n_start->add_epsilon_transition(other.start);
    end->add_epsilon_transition(n_end);
    other.end->add_epsilon_transition(n_end);
    start = n_start;
    end = n_end;
    for (pmatch::Node *n : other.to_delete)
        to_delete.insert(n);
    other.to_delete.clear();
    return *this;
}

pmatch::NFA &pmatch::NFA::closure()
{
    pmatch::Node *n_start = create_node(false), *n_end = create_node(true);
    end->is_terminal = false;
    n_start->add_epsilon_transition(n_end);
    n_start->add_epsilon_transition(start);
    end->add_epsilon_transition(n_end);
    end->add_epsilon_transition(start);
    start = n_start;
    end = n_end;
    return *this;
}

pmatch::NFA &pmatch::NFA::semi_closure()
{
    pmatch::Node *n_start = create_node(false), *n_end = create_node(true);
    end->is_terminal = false;
    n_start->add_epsilon_transition(start);
    end->add_epsilon_transition(n_end);
    end->add_epsilon_transition(start);
    start = n_start;
    end = n_end;
    return *this;
}

pmatch::NFA &pmatch::NFA::optional()
{
    pmatch::Node *n_start = create_node(false), *n_end = create_node(true);
    end->is_terminal = false;
    n_start->add_epsilon_transition(n_end);
    n_start->add_epsilon_transition(start);
    end->add_epsilon_transition(n_end);
    start = n_start;
    end = n_end;
    return *this;
}

static void get_next_states(pmatch::Node* state, std::set<pmatch::Node*>& states, std::set<pmatch::Node*>& visited)
{
    if (state->get_epsilon_transitions().size() > 0) {
        for (pmatch::Node *transition : state->get_epsilon_transitions()) {
            if (visited.count(transition) == 0) {
                visited.emplace(transition);
                get_next_states(transition, states, visited);
            }
        }
    }
    else
        states.insert(state);
}

static void get_next_states(pmatch::Node* state, std::set<pmatch::Node*>& states)
{
    std::set<pmatch::Node*> visited;
    get_next_states(state, states, visited);
}

ssize_t pmatch::NFA::match(const std::vector<object>& inp)
{
    std::set<pmatch::Node*> current_states;
    std::set<ssize_t> matches({-1});
    get_next_states(start, current_states);
    ssize_t count = 0;
    for (object symbol : inp) {
        count++;
        std::set<pmatch::Node*> next_states;
        for (Node* state : current_states) {
            if (state->get_transition().second == symbol)
                get_next_states(state->get_transition().first, next_states);
        }
        current_states = next_states;
        for (pmatch::Node* state : current_states) {
            if (state->is_terminal) {
                matches.insert(count);
                break;
            }
        }
    }
    return *std::max_element(matches.begin(), matches.end());
}

pmatch::Node *pmatch::NFA::create_node(bool is_terminal)
{
    Node *new_node = new Node(is_terminal);
    to_delete.insert(new_node);
    return new_node;
}
