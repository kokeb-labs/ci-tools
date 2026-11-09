// Seeded violation (member): a built-in array as a class member.
#include <cstdint>

namespace kv::rule_11_3_1::bad_member {

struct Frame {
  std::int32_t payload[4] = {};
};

std::int32_t first(const Frame& f) { return f.payload[0]; }

}  // namespace kv::rule_11_3_1::bad_member
