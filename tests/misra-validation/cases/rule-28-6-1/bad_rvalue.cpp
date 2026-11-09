// Seeded violation: std::move applied to a prvalue, which is already an rvalue (a redundant move).
#include <array>
#include <cstdint>
#include <utility>

namespace kv::rule_28_6_1::bad_rvalue {

struct Buffer {
  std::array<std::uint8_t, 4U> data;
};

Buffer make() { return Buffer{}; }

void fill(Buffer& dest) { dest = std::move(make()); }  // seeded

}  // namespace kv::rule_28_6_1::bad_rvalue
