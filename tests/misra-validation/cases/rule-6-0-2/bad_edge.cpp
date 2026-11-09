// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_0_2::bad_edge {

extern const char* const kNames[];
const char* first_name() { return kNames[0]; }

}  // namespace kv::rule_6_0_2::bad_edge
