// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_5_13_5::bad_edge {

std::uint64_t unsigned_long() { return 5ul; }
std::int64_t long_long() { return 6ll; }

}  // namespace kv::rule_5_13_5::bad_edge
