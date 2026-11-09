// Edge cases: more forms of the violation.
#include <memory>

namespace kv::rule_4_1_2_allocator_void::bad_edge {

template <typename A>
bool equal(const A& a, const A& b) { return a == b; }

bool via_template(const std::allocator<void>& a) { return equal(a, a); }

}  // namespace kv::rule_4_1_2_allocator_void::bad_edge
