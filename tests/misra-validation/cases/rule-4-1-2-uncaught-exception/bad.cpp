// Seeded violation: the deprecated std::uncaught_exception().
#include <exception>

namespace kv::rule_4_1_2_uncaught_exception::bad {

bool unwinding() { return std::uncaught_exception(); }  // seeded

}  // namespace kv::rule_4_1_2_uncaught_exception::bad
