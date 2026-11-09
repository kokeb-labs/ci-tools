// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_6_5_1::bad_edge {

extern const std::int32_t kLimit;
const std::int32_t kLimit = 7;  // an external object declared only in this source file  // seeded
std::int32_t twice_limit() { return kLimit * 2; }  // seeded

}  // namespace kv::rule_6_5_1::bad_edge
