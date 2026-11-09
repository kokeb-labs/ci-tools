// Edge cases: a suffix that starts with a lower-case l, in front of U, and the long long form.
#include <cstdint>

namespace kv::rule_5_13_5::bad_edge {

std::uint64_t long_unsigned() { return 5lu; }  // seeded
std::uint64_t long_upper_unsigned() { return 1lU; }  // seeded
std::int64_t long_long() { return 6ll; }  // seeded

}  // namespace kv::rule_5_13_5::bad_edge
