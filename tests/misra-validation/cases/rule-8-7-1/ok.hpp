// Compliant: indexing stays inside the array.
#ifndef KV_RULE_8_7_1_OK_HPP
#define KV_RULE_8_7_1_OK_HPP

#include <array>
#include <cstdint>
#include <cstddef>

namespace kv::rule_8_7_1::ok {

inline std::uint8_t last(const std::array<std::uint8_t, 4>& buffer) { return buffer[buffer.size() - 1U]; }

inline std::size_t length(const std::array<char, 4>& text) {
  std::size_t n = 0U;
  for (const char c : text) {
    if (c == '\0') {
      break;
    }
    ++n;
  }
  return n;
}

}  // namespace kv::rule_8_7_1::ok

#endif  // KV_RULE_8_7_1_OK_HPP
