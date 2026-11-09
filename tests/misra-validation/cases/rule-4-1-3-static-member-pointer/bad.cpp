// Seeded violation: access through a static pointer to member that was never set.
#include <cstdint>

namespace kv::rule_4_1_3_static_member_pointer::bad {

struct Point {
  std::uint32_t x{0U};
};

static std::uint32_t Point::*g_member;  // zero-initialised: null

std::uint32_t read(const Point& p) { return p.*g_member; }  // seeded

}  // namespace kv::rule_4_1_3_static_member_pointer::bad

int main() {
  const kv::rule_4_1_3_static_member_pointer::bad::Point p{};
  return static_cast<int>(kv::rule_4_1_3_static_member_pointer::bad::read(p));
}
