// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_6_9_2_OK_NEAR_HPP
#define KV_RULE_6_9_2_OK_NEAR_HPP

#include <cstddef>
#include <cstdint>

namespace kv::rule_6_9_2::near {

// char for text, bool for truth values, std::size_t for sizes, and auto deduced from a fixed-width type.
inline bool starts_with_a(const char* text) { return (text != nullptr) && (text[0] == 'a'); }
inline std::size_t width() { return sizeof(std::uint32_t); }
inline std::uint32_t same(std::uint32_t v) {
  const auto copy = v;
  return copy;
}

}  // namespace kv::rule_6_9_2::near

#endif  // KV_RULE_6_9_2_OK_NEAR_HPP
