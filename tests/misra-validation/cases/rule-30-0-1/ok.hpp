// Compliant: the number is formatted into a caller-owned buffer with std::to_chars.
#ifndef KV_RULE_30_0_1_OK_HPP
#define KV_RULE_30_0_1_OK_HPP

#include <array>
#include <charconv>
#include <cstdint>
#include <system_error>

namespace kv::rule_30_0_1::ok {

[[nodiscard]] inline bool format(std::uint32_t value, std::array<char, 16U>& out) {
  const std::to_chars_result result = std::to_chars(out.begin(), out.end(), value);
  return result.ec == std::errc{};
}

}  // namespace kv::rule_30_0_1::ok

#endif  // KV_RULE_30_0_1_OK_HPP
