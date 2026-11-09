// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_1::bad_edge {

// A GNU statement expression.
std::uint32_t twice_plus(std::uint32_t v) {
  return ({  // seeded
    const std::uint32_t t = v << 1U;
    t | 1U;
  });
}

// A GNU type attribute on a struct.
struct __attribute__((packed)) Frame {  // seeded
  std::uint8_t tag;
  std::uint32_t value;
};
std::uint32_t value_of(const Frame& f) { return f.value; }

}  // namespace kv::rule_4_1_1::bad_edge
