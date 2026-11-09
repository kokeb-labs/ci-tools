// Seeded violation: a deprecated adaptor typedef of a standard function object.
#include <functional>

namespace kv::rule_4_1_2_binder_typedef::bad {

using Sum = std::plus<int>::result_type;  // removed adaptor typedef  // seeded

Sum add(Sum a) { return a; }

}  // namespace kv::rule_4_1_2_binder_typedef::bad
