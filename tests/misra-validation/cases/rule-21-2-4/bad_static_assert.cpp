// Seeded violation: offsetof in a static_assert (a use MD-CPP-007 may deviate; still a violation).
#include <cstddef>
#include <cstdint>

namespace kv::rule_21_2_4::bad_static_assert {

struct Frame {
  std::uint8_t command;
  std::uint8_t length;
};

static_assert(offsetof(Frame, length) == 1U, "the wire frame layout");

}  // namespace kv::rule_21_2_4::bad_static_assert
