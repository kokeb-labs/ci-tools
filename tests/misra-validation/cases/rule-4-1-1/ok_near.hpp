// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_4_1_1_OK_NEAR_HPP
#define KV_RULE_4_1_1_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_4_1_1::near {

// A standard attribute and alignas are ISO C++, not extensions.
struct alignas(4) Frame {
  std::uint8_t tag;
  std::uint32_t value;
};

[[nodiscard]] inline std::uint32_t value_of(const Frame& f) { return (f.tag == 0U) ? f.value : 0U; }

}  // namespace kv::rule_4_1_1::near

#endif  // KV_RULE_4_1_1_OK_NEAR_HPP
