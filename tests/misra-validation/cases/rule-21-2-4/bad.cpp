// Seeded violation: a member offset computed with the offsetof macro in run-time code.
#include <cstddef>
#include <cstdint>

namespace kv::rule_21_2_4::bad {

struct Frame {
  std::uint8_t command;
  std::uint32_t payload;
};

std::size_t payload_offset() { return offsetof(Frame, payload); }  // seeded

}  // namespace kv::rule_21_2_4::bad
