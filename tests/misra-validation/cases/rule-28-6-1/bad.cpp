// Seeded violation: std::move applied to a const object, which can only be copied.
#include <array>
#include <cstdint>
#include <utility>

namespace kv::rule_28_6_1::bad {

struct Buffer {
  std::array<std::uint8_t, 4U> data;
};

Buffer forward_copy(const Buffer& source) { return std::move(source); }  // seeded

}  // namespace kv::rule_28_6_1::bad
