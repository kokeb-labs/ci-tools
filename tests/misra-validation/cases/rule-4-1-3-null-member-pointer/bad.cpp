// Seeded violation: access through a null pointer to member.
#include <cstdint>

namespace kv::rule_4_1_3_null_member_pointer::bad {

struct Point {
  std::uint32_t x{0U};
};

std::uint32_t read(const Point& p) {
  std::uint32_t Point::*pm = nullptr;
  return p.*pm;
}

}  // namespace kv::rule_4_1_3_null_member_pointer::bad
